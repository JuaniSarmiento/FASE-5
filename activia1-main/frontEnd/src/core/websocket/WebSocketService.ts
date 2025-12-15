/**
 * WebSocket Service para actualizaciones en tiempo real
 */

interface WebSocketMessage {
  type: string;
  data: unknown;
  timestamp: string;
}

interface WebSocketConfig {
  url: string;
  reconnectDelay: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
}

type MessageHandler = (message: WebSocketMessage) => void;
type EventHandler = () => void;

// Development-only logging helper
const isDev = import.meta.env.DEV;
const devLog = (message: string, ...args: unknown[]) => {
  if (isDev) console.log(message, ...args);
};
const devWarn = (message: string, ...args: unknown[]) => {
  if (isDev) console.warn(message, ...args);
};
const devError = (message: string, ...args: unknown[]) => {
  if (isDev) console.error(message, ...args);
};

export class WebSocketService {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map();
  private eventHandlers: Map<string, Set<EventHandler>> = new Map();
  private reconnectAttempts = 0;
  private heartbeatTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private isIntentionallyClosed = false;

  constructor(config?: Partial<WebSocketConfig>) {
    // FIX: Usar wss:// para HTTPS, ws:// para HTTP
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const defaultWsUrl = `${wsProtocol}//${window.location.host}/ws`;

    this.config = {
      url: config?.url || defaultWsUrl,
      reconnectDelay: config?.reconnectDelay || 3000,
      maxReconnectAttempts: config?.maxReconnectAttempts || 10,
      heartbeatInterval: config?.heartbeatInterval || 30000
    };
  }

  connect(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      devWarn('[WebSocket] Already connected');
      return;
    }

    this.isIntentionallyClosed = false;

    try {
      devLog(`[WebSocket] Connecting to ${this.config.url}...`);
      this.ws = new WebSocket(this.config.url);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);

    } catch (error) {
      devError('[WebSocket] Connection error:', error);
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    devLog('[WebSocket] Disconnecting...');
    this.isIntentionallyClosed = true;

    this.stopHeartbeat();
    this.stopReconnect();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.triggerEvent('disconnect');
  }

  send(type: string, data: unknown): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      devWarn('[WebSocket] Cannot send, not connected');
      return;
    }

    const message: WebSocketMessage = {
      type,
      data,
      timestamp: new Date().toISOString()
    };

    try {
      this.ws.send(JSON.stringify(message));
      devLog(`[WebSocket →] ${type}`, data);
    } catch (error) {
      devError('[WebSocket] Send error:', error);
    }
  }

  on(type: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }

    this.messageHandlers.get(type)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.messageHandlers.get(type)?.delete(handler);
    };
  }

  onEvent(event: string, handler: EventHandler): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }

    this.eventHandlers.get(event)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.eventHandlers.get(event)?.delete(handler);
    };
  }

  private handleOpen(): void {
    devLog('[WebSocket] ✓ Connected');
    this.reconnectAttempts = 0;
    this.startHeartbeat();
    this.triggerEvent('connect');
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      devLog(`[WebSocket ←] ${message.type}`, message.data);

      // Trigger handlers for this message type
      const handlers = this.messageHandlers.get(message.type);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            devError(`[WebSocket] Handler error for ${message.type}:`, error);
          }
        });
      }

      // Trigger 'message' event for all messages
      this.triggerEvent('message');

    } catch (error) {
      devError('[WebSocket] Parse error:', error);
    }
  }

  private handleError(event: Event): void {
    devError('[WebSocket] Error:', event);
    this.triggerEvent('error');
  }

  private handleClose(event: CloseEvent): void {
    devLog(`[WebSocket] Closed: ${event.code} - ${event.reason}`);

    this.stopHeartbeat();
    this.triggerEvent('close');

    // Attempt reconnect if not intentional
    if (!this.isIntentionallyClosed && this.reconnectAttempts < this.config.maxReconnectAttempts) {
      this.scheduleReconnect();
    } else if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      devError('[WebSocket] Max reconnect attempts reached');
      this.triggerEvent('max_reconnect_failed');
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return;
    }

    this.reconnectAttempts++;
    const delay = this.config.reconnectDelay * Math.min(this.reconnectAttempts, 5);

    devLog(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delay);
  }

  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();

    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send('ping', { timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private triggerEvent(event: string): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler();
        } catch (error) {
          devError(`[WebSocket] Event handler error for ${event}:`, error);
        }
      });
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  getState(): string {
    if (!this.ws) return 'DISCONNECTED';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'OPEN';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'CLOSED';
      default:
        return 'UNKNOWN';
    }
  }
}

// Global singleton instance
export const wsService = new WebSocketService();

// Auto-connect on instantiation
if (typeof window !== 'undefined') {
  wsService.connect();

  // Cleanup on page unload
  window.addEventListener('beforeunload', () => {
    wsService.disconnect();
  });
}
