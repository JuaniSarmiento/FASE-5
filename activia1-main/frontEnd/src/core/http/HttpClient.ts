/**
 * Cliente HTTP con Circuit Breaker, Retry Logic y Request Queue
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { API_ENDPOINTS } from '@/core/config/routes.config';

// Development-only logging
const isDev = import.meta.env.DEV;
const devLog = (message: string, ...args: unknown[]) => { if (isDev) console.log(message, ...args); };
const devError = (message: string, ...args: unknown[]) => { if (isDev) console.error(message, ...args); };

// Extend Axios config to include metadata
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    metadata?: { startTime: number };
  }
}

interface CircuitBreakerState {
  failures: number;
  lastFailure: number;
  state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
}

interface RequestQueueItem<T = unknown> {
  config: AxiosRequestConfig;
  resolve: (value: T) => void;
  reject: (reason: Error | AxiosError) => void;
}

interface HttpMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  retriedRequests: number;
  averageLatency: number;
  circuitBreakerTrips: number;
}

export class HttpClient {
  private client: AxiosInstance;
  private circuitBreaker: CircuitBreakerState = {
    failures: 0,
    lastFailure: 0,
    state: 'CLOSED'
  };
  private requestQueue: RequestQueueItem[] = [];
  private isProcessingQueue = false;
  private metrics: HttpMetrics = {
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    retriedRequests: 0,
    averageLatency: 0,
    circuitBreakerTrips: 0
  };

  private readonly FAILURE_THRESHOLD = 5;
  private readonly TIMEOUT = 30000;
  private readonly RETRY_ATTEMPTS = 3;
  private readonly CIRCUIT_RESET_TIME = 60000; // 1 minute
  private readonly QUEUE_PROCESS_DELAY = 100; // ms

  constructor(baseURL?: string) {
    this.client = axios.create({
      baseURL: baseURL || API_ENDPOINTS.BASE,
      timeout: this.TIMEOUT,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const startTime = Date.now();
        config.metadata = { startTime };

        // Add auth token
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add correlation ID
        config.headers['X-Correlation-ID'] = this.generateCorrelationId();

        devLog(`[HTTP →] ${config.method?.toUpperCase()} ${config.url}`);
        this.metrics.totalRequests++;

        return config;
      },
      (error) => {
        devError('[HTTP] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        this.onSuccess(response);
        return response;
      },
      async (error) => {
        return this.handleError(error);
      }
    );
  }

  private async handleError(error: AxiosError): Promise<AxiosResponse> {
    const config = error.config as AxiosRequestConfig & { __retryCount?: number };

    // Record failure
    this.onFailure();

    // Initialize retry counter
    if (!config) {
      return Promise.reject(error);
    }
    if (!config.__retryCount) {
      config.__retryCount = 0;
    }

    // Check if we should retry
    if (
      config.__retryCount < this.RETRY_ATTEMPTS &&
      this.isRetryableError(error)
    ) {
      config.__retryCount++;
      this.metrics.retriedRequests++;

      const delay = this.calculateBackoff(config.__retryCount);
      devLog(
        `[HTTP ↻] Retry ${config.__retryCount}/${this.RETRY_ATTEMPTS} after ${delay}ms`
      );

      await this.sleep(delay);
      return this.client(config);
    }

    // Max retries exceeded or non-retryable error
    this.metrics.failedRequests++;
    devError('[HTTP ✗] Request failed:', error.message);

    return Promise.reject(error);
  }

  private isRetryableError(error: AxiosError): boolean {
    if (!error.response) {
      // Network errors, timeouts
      return true;
    }

    const status = error.response.status;
    // Retry on 5xx and specific 4xx
    return status >= 500 || status === 408 || status === 429;
  }

  private calculateBackoff(retryCount: number): number {
    // Exponential backoff with jitter
    const baseDelay = 1000;
    const exponentialDelay = baseDelay * Math.pow(2, retryCount - 1);
    const jitter = Math.random() * 200;
    return Math.min(exponentialDelay + jitter, 10000); // Max 10s
  }

  private onSuccess(response: AxiosResponse): void {
    // Calculate latency
    const latency = Date.now() - (response.config.metadata?.startTime || Date.now());
    this.updateAverageLatency(latency);

    this.metrics.successfulRequests++;
    devLog(`[HTTP ✓] ${response.config.url} (${latency}ms)`);

    // Reset circuit breaker if in HALF_OPEN
    if (this.circuitBreaker.state === 'HALF_OPEN') {
      this.circuitBreaker.state = 'CLOSED';
      this.circuitBreaker.failures = 0;
      devLog('[Circuit Breaker] → CLOSED (recovered)');
    }
  }

  private onFailure(): void {
    this.circuitBreaker.failures++;
    this.circuitBreaker.lastFailure = Date.now();

    if (this.circuitBreaker.failures >= this.FAILURE_THRESHOLD) {
      this.circuitBreaker.state = 'OPEN';
      this.metrics.circuitBreakerTrips++;
      devError(
        `[Circuit Breaker] → OPEN (${this.circuitBreaker.failures} failures)`
      );

      setTimeout(() => {
        this.circuitBreaker.state = 'HALF_OPEN';
        devLog('[Circuit Breaker] → HALF_OPEN (testing)');
      }, this.CIRCUIT_RESET_TIME);
    }
  }

  private checkCircuitBreaker(): void {
    if (this.circuitBreaker.state === 'OPEN') {
      const error = new Error('Circuit breaker is OPEN. Service temporarily unavailable.');
      error.name = 'CircuitBreakerError';
      throw error;
    }
  }

  private updateAverageLatency(newLatency: number): void {
    const totalRequests = this.metrics.successfulRequests;
    this.metrics.averageLatency =
      (this.metrics.averageLatency * (totalRequests - 1) + newLatency) / totalRequests;
  }

  private getToken(): string | null {
    if (typeof localStorage === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Public API methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    this.checkCircuitBreaker();
    const response = await this.client.get<T>(url, config);
    return this.extractData(response);
  }

  async post<T, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig): Promise<T> {
    this.checkCircuitBreaker();
    const response = await this.client.post<T>(url, data, config);
    return this.extractData(response);
  }

  async put<T, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig): Promise<T> {
    this.checkCircuitBreaker();
    const response = await this.client.put<T>(url, data, config);
    return this.extractData(response);
  }

  async patch<T, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig): Promise<T> {
    this.checkCircuitBreaker();
    const response = await this.client.patch<T>(url, data, config);
    return this.extractData(response);
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    this.checkCircuitBreaker();
    const response = await this.client.delete<T>(url, config);
    return this.extractData(response);
  }

  private extractData<T>(response: AxiosResponse): T {
    // Handle APIResponse wrapper from backend
    if (response.data && 'data' in response.data && response.data.success !== undefined) {
      return response.data.data;
    }
    return response.data;
  }

  // Queue management for rate-limited requests
  // FIX Cortez16: Use type assertion for queue item to handle generic type
  async queueRequest<T>(config: AxiosRequestConfig): Promise<T> {
    return new Promise((resolve, reject) => {
      this.requestQueue.push({
        config,
        resolve: resolve as (value: unknown) => void,
        reject
      });
      if (!this.isProcessingQueue) {
        this.processQueue();
      }
    });
  }

  private async processQueue(): Promise<void> {
    if (this.requestQueue.length === 0) {
      this.isProcessingQueue = false;
      return;
    }

    this.isProcessingQueue = true;
    const item = this.requestQueue.shift();

    if (item) {
      try {
        const response = await this.client(item.config);
        item.resolve(this.extractData(response));
      } catch (error) {
        // FIX Cortez16: Cast error to expected type
        item.reject(error as Error | AxiosError);
      }

      await this.sleep(this.QUEUE_PROCESS_DELAY);
      this.processQueue();
    }
  }

  // Metrics and health
  getMetrics(): HttpMetrics {
    return { ...this.metrics };
  }

  getCircuitBreakerState(): CircuitBreakerState {
    return { ...this.circuitBreaker };
  }

  resetMetrics(): void {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      retriedRequests: 0,
      averageLatency: 0,
      circuitBreakerTrips: 0
    };
  }
}

// Global singleton instance
export const httpClient = new HttpClient();

// Ollama-specific client (uses env var or localhost for local LLM)
const OLLAMA_URL = import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434';
export const ollamaClient = new HttpClient(OLLAMA_URL);
