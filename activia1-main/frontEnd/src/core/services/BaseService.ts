/**
 * Servicio base con caché, debouncing y manejo de errores
 */
import { httpClient } from '@/core/http/HttpClient';
import { CacheManager } from '@/core/cache/CacheManager';

// Development-only logging
const isDev = import.meta.env.DEV;
const devLog = (message: string) => { if (isDev) console.log(message); };

export interface PaginationParams {
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export abstract class BaseService<T> {
  protected cache?: CacheManager<T | T[]>;
  private debounceTimers: Map<string, ReturnType<typeof setTimeout>> = new Map();
  private abortControllers: Map<string, AbortController> = new Map();

  constructor(
    protected endpoint: string,
    cacheOptions?: { max: number; ttl: number; persist?: boolean }
  ) {
    if (cacheOptions) {
      this.cache = new CacheManager<T | T[]>(endpoint, cacheOptions);
    }
  }

  // Core CRUD operations
  protected async get(url: string, useCache = true): Promise<T> {
    const cacheKey = `GET:${url}`;

    if (useCache && this.cache?.has(cacheKey)) {
      devLog(`[Cache HIT] ${url}`);
      return this.cache.get(cacheKey) as T;
    }

    devLog(`[Cache MISS] ${url}`);
    const data = await httpClient.get<T>(url);

    if (this.cache) {
      this.cache.set(cacheKey, data);
    }

    return data;
  }

  protected async list(url: string, useCache = true): Promise<T[]> {
    const cacheKey = `LIST:${url}`;

    if (useCache && this.cache?.has(cacheKey)) {
      devLog(`[Cache HIT] ${url}`);
      return this.cache.get(cacheKey) as T[];
    }

    devLog(`[Cache MISS] ${url}`);
    const data = await httpClient.get<T[]>(url);

    if (this.cache) {
      this.cache.set(cacheKey, data);
    }

    return data;
  }

  protected async post<P = Record<string, unknown>>(url: string, payload: P): Promise<T> {
    const data = await httpClient.post<T>(url, payload);

    // Invalidate related cache
    this.invalidateCache();

    return data;
  }

  protected async put<P = Record<string, unknown>>(url: string, payload: P): Promise<T> {
    const data = await httpClient.put<T>(url, payload);

    // Invalidate related cache
    this.invalidateCache();

    return data;
  }

  protected async patch<P = Partial<T>>(url: string, payload: P): Promise<T> {
    const data = await httpClient.patch<T>(url, payload);

    // Invalidate related cache
    this.invalidateCache();

    return data;
  }

  protected async delete(url: string): Promise<void> {
    await httpClient.delete(url);

    // Invalidate related cache
    this.invalidateCache();
  }

  // Pagination helper
  protected async getPaginated(
    url: string,
    params: PaginationParams = {},
    useCache = true
  ): Promise<PaginatedResponse<T>> {
    const queryParams = new URLSearchParams({
      page: String(params.page ?? 1),
      limit: String(params.limit ?? 20),
      ...(params.sort && { sort: params.sort }),
      ...(params.order && { order: params.order })
    });

    const fullUrl = `${url}?${queryParams.toString()}`;
    const cacheKey = `PAGINATED:${fullUrl}`;

    if (useCache && this.cache?.has(cacheKey)) {
      devLog(`[Cache HIT] ${fullUrl}`);
      return this.cache.get(cacheKey) as PaginatedResponse<T>;
    }

    devLog(`[Cache MISS] ${fullUrl}`);
    const data = await httpClient.get<PaginatedResponse<T>>(fullUrl);

    if (this.cache) {
      this.cache.set(cacheKey, data as unknown as T);
    }

    return data;
  }

  // Debouncing for search/filter operations
  protected debounce<R, Args extends unknown[]>(
    key: string,
    fn: (...args: Args) => Promise<R>,
    delay: number
  ): (...args: Args) => Promise<R> {
    return (...args: Args) => {
      return new Promise((resolve, reject) => {
        const existingTimer = this.debounceTimers.get(key);
        if (existingTimer) {
          clearTimeout(existingTimer);
        }

        const timer = setTimeout(async () => {
          try {
            const result = await fn(...args);
            resolve(result);
          } catch (error) {
            reject(error);
          } finally {
            this.debounceTimers.delete(key);
          }
        }, delay);

        this.debounceTimers.set(key, timer);
      });
    };
  }

  // Cancelable requests for typeahead/search
  protected async getCancelable(url: string, cancelKey: string): Promise<T> {
    // Cancel previous request with same key
    const existingController = this.abortControllers.get(cancelKey);
    if (existingController) {
      existingController.abort();
    }

    // Create new controller
    const controller = new AbortController();
    this.abortControllers.set(cancelKey, controller);

    try {
      const data = await httpClient.get<T>(url, {
        signal: controller.signal
      });

      this.abortControllers.delete(cancelKey);
      return data;
    } catch (error: unknown) {
      const err = error as Error & { name?: string };
      if (err.name === 'CanceledError') {
        devLog(`[Request Canceled] ${url}`);
        throw new Error('Request canceled');
      }
      throw error;
    }
  }

  // Cache management
  protected invalidateCache(pattern?: string): void {
    if (!this.cache) return;

    if (pattern) {
      // Invalidate specific keys matching pattern
      const keys = this.cache.keys();
      keys.forEach(key => {
        if (key.includes(pattern)) {
          this.cache!.delete(key);
        }
      });
    } else {
      // Invalidate all cache
      this.cache.clear();
    }

    devLog(`[Cache] Invalidated ${pattern || 'all'}`);
  }

  // Error handling helpers
  protected handleError(error: unknown, context: string): never {
    console.error(`[${this.endpoint}] ${context}:`, error);

    const err = error as { error?: { message?: string }; request?: unknown; message?: string };

    // Check for APIError structure (from axios interceptor)
    if (err.error?.message) {
      throw new Error(`${context}: ${err.error.message}`);
    } else if (err.request) {
      // No response received
      throw new Error(`${context}: No response from server`);
    } else {
      // Request setup error
      throw new Error(`${context}: ${err.message || 'Unknown error'}`);
    }
  }

  // Cleanup
  destroy(): void {
    // Clear all debounce timers
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();

    // Abort all pending requests
    this.abortControllers.forEach(controller => controller.abort());
    this.abortControllers.clear();

    // Clear cache
    if (this.cache) {
      this.cache.clear();
    }
  }
}
