/**
 * Sistema de caché LRU con persistencia y TTL
 */

// Development-only logging
const isDev = import.meta.env.DEV;
const devLog = (message: string) => { if (isDev) console.log(message); };
const devWarn = (message: string, ...args: unknown[]) => { if (isDev) console.warn(message, ...args); };

interface CacheEntry<T> {
  value: T;
  expiry: number;
}

interface CacheOptions {
  max: number;
  ttl: number; // milliseconds
  persist?: boolean;
  updateAgeOnGet?: boolean;
}

export class CacheManager<T = unknown> {
  private cache: Map<string, CacheEntry<T>>;
  private accessOrder: string[];
  private storageKey: string;
  private options: Required<CacheOptions>;

  constructor(name: string, options: CacheOptions) {
    this.storageKey = `cache_${name}`;
    this.cache = new Map();
    this.accessOrder = [];
    this.options = {
      max: options.max,
      ttl: options.ttl,
      persist: options.persist ?? false,
      updateAgeOnGet: options.updateAgeOnGet ?? true
    };

    if (this.options.persist) {
      this.loadFromStorage();
    }

    // Cleanup expired entries every minute
    setInterval(() => this.cleanup(), 60000);
  }

  set(key: string, value: T): void {
    const expiry = Date.now() + this.options.ttl;

    // Remove if exists
    if (this.cache.has(key)) {
      this.accessOrder = this.accessOrder.filter(k => k !== key);
    }

    // Add new entry
    this.cache.set(key, { value, expiry });
    this.accessOrder.push(key);

    // Evict if over capacity
    if (this.cache.size > this.options.max) {
      const oldest = this.accessOrder.shift();
      if (oldest) {
        this.cache.delete(oldest);
      }
    }

    if (this.options.persist) {
      this.persistToStorage();
    }
  }

  get(key: string): T | undefined {
    const entry = this.cache.get(key);

    if (!entry) {
      return undefined;
    }

    // Check expiry
    if (Date.now() > entry.expiry) {
      this.delete(key);
      return undefined;
    }

    // Update access order
    if (this.options.updateAgeOnGet) {
      this.accessOrder = this.accessOrder.filter(k => k !== key);
      this.accessOrder.push(key);
    }

    return entry.value;
  }

  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;

    if (Date.now() > entry.expiry) {
      this.delete(key);
      return false;
    }

    return true;
  }

  delete(key: string): void {
    this.cache.delete(key);
    this.accessOrder = this.accessOrder.filter(k => k !== key);

    if (this.options.persist) {
      this.persistToStorage();
    }
  }

  clear(): void {
    this.cache.clear();
    this.accessOrder = [];

    if (this.options.persist && typeof localStorage !== 'undefined') {
      localStorage.removeItem(this.storageKey);
    }
  }

  size(): number {
    return this.cache.size;
  }

  keys(): string[] {
    return Array.from(this.cache.keys());
  }

  private cleanup(): void {
    const now = Date.now();
    const toDelete: string[] = [];

    this.cache.forEach((entry, key) => {
      if (now > entry.expiry) {
        toDelete.push(key);
      }
    });

    toDelete.forEach(key => this.delete(key));

    if (toDelete.length > 0) {
      devLog(`[Cache] Cleaned up ${toDelete.length} expired entries`);
    }
  }

  private persistToStorage(): void {
    if (typeof localStorage === 'undefined') return;

    try {
      const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
        key,
        value: entry.value,
        expiry: entry.expiry
      }));

      localStorage.setItem(this.storageKey, JSON.stringify(entries));
    } catch (error) {
      devWarn('[Cache] Failed to persist to storage:', error);
    }
  }

  private loadFromStorage(): void {
    if (typeof localStorage === 'undefined') return;

    try {
      const stored = localStorage.getItem(this.storageKey);
      if (!stored) return;

      const entries = JSON.parse(stored) as Array<{
        key: string;
        value: T;
        expiry: number;
      }>;

      const now = Date.now();
      entries.forEach(({ key, value, expiry }) => {
        if (expiry > now) {
          this.cache.set(key, { value, expiry });
          this.accessOrder.push(key);
        }
      });

      devLog(`[Cache] Loaded ${this.cache.size} entries from storage`);
    } catch (error) {
      devWarn('[Cache] Failed to load from storage:', error);
    }
  }

  getStats() {
    return {
      size: this.cache.size,
      max: this.options.max,
      utilizationPercent: (this.cache.size / this.options.max) * 100,
      oldestKey: this.accessOrder[0],
      newestKey: this.accessOrder[this.accessOrder.length - 1]
    };
  }
}

// Global cache instances
export const sessionsCache = new CacheManager('sessions', {
  max: 50,
  ttl: 1000 * 60 * 30, // 30 minutes
  persist: true
});

export const interactionsCache = new CacheManager('interactions', {
  max: 200,
  ttl: 1000 * 60 * 10 // 10 minutes
});

export const evaluationsCache = new CacheManager('evaluations', {
  max: 100,
  ttl: 1000 * 60 * 15 // 15 minutes
});

export const risksCache = new CacheManager('risks', {
  max: 50,
  ttl: 1000 * 60 * 20 // 20 minutes
});

export const tracesCache = new CacheManager('traces', {
  max: 150,
  ttl: 1000 * 60 * 10 // 10 minutes
});
