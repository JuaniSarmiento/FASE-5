/**
 * Error Utility Functions - FIX 2.4 Cortez3
 *
 * Centralized error handling utilities for consistent error extraction
 * and type-safe error processing across the application.
 */

/**
 * Application error interface for structured error handling
 */
export interface AppError {
  message: string;
  code?: string;
  status?: number;
  details?: Record<string, unknown>;
}

/**
 * Extracts a user-friendly error message from various error types.
 *
 * Handles:
 * - Standard Error objects
 * - String errors
 * - Axios error responses (nested response.data.message)
 * - API error responses with message field
 * - Unknown error types
 *
 * @param error - The error to extract message from
 * @returns A human-readable error message
 *
 * @example
 * ```typescript
 * try {
 *   await submitExercise(code);
 * } catch (error) {
 *   const message = extractErrorMessage(error);
 *   showToast(message, 'error');
 * }
 * ```
 */
export function extractErrorMessage(error: unknown): string {
  // Handle standard Error objects
  if (error instanceof Error) {
    return error.message;
  }

  // Handle string errors
  if (typeof error === 'string') {
    return error;
  }

  // Handle object-based errors
  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;

    // Direct message field
    if ('message' in err && typeof err.message === 'string') {
      return err.message;
    }

    // Axios-style nested response.data.message
    if ('response' in err && err.response && typeof err.response === 'object') {
      const response = err.response as Record<string, unknown>;

      // Check response.data.message
      if ('data' in response && response.data && typeof response.data === 'object') {
        const data = response.data as Record<string, unknown>;
        if ('message' in data && typeof data.message === 'string') {
          return data.message;
        }
        // Check for error.message nested structure
        if ('error' in data && data.error && typeof data.error === 'object') {
          const errorObj = data.error as Record<string, unknown>;
          if ('message' in errorObj && typeof errorObj.message === 'string') {
            return errorObj.message;
          }
        }
      }

      // Check response.statusText
      if ('statusText' in response && typeof response.statusText === 'string') {
        return response.statusText;
      }
    }

    // FastAPI/APIResponse error structure
    if ('error' in err && err.error && typeof err.error === 'object') {
      const errorObj = err.error as Record<string, unknown>;
      if ('message' in errorObj && typeof errorObj.message === 'string') {
        return errorObj.message;
      }
    }

    // Detail field (common in FastAPI validation errors)
    if ('detail' in err) {
      if (typeof err.detail === 'string') {
        return err.detail;
      }
      if (Array.isArray(err.detail) && err.detail.length > 0) {
        const firstError = err.detail[0];
        if (typeof firstError === 'object' && firstError && 'msg' in firstError) {
          return String(firstError.msg);
        }
      }
    }
  }

  return 'An unexpected error occurred';
}

/**
 * Type guard to check if an error matches the AppError interface
 *
 * @param error - The value to check
 * @returns True if the error is an AppError
 *
 * @example
 * ```typescript
 * if (isAppError(error)) {
 *   console.log(error.code);
 * }
 * ```
 */
export function isAppError(error: unknown): error is AppError {
  return (
    error !== null &&
    typeof error === 'object' &&
    'message' in error &&
    typeof (error as AppError).message === 'string'
  );
}

/**
 * Creates a standardized AppError from various error types
 *
 * @param error - The error to convert
 * @param defaultMessage - Default message if extraction fails
 * @returns A standardized AppError object
 */
export function toAppError(
  error: unknown,
  defaultMessage = 'An unexpected error occurred'
): AppError {
  const message = extractErrorMessage(error);

  // Extract additional details if available
  let code: string | undefined;
  let status: number | undefined;
  let details: Record<string, unknown> | undefined;

  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;

    // Extract error code
    if ('code' in err && typeof err.code === 'string') {
      code = err.code;
    } else if ('error' in err && typeof err.error === 'object' && err.error) {
      const errorObj = err.error as Record<string, unknown>;
      if ('error_code' in errorObj && typeof errorObj.error_code === 'string') {
        code = errorObj.error_code;
      }
    }

    // Extract status code
    if ('status' in err && typeof err.status === 'number') {
      status = err.status;
    } else if ('response' in err && typeof err.response === 'object' && err.response) {
      const response = err.response as Record<string, unknown>;
      if ('status' in response && typeof response.status === 'number') {
        status = response.status;
      }
    }

    // Extract additional details
    if ('details' in err && typeof err.details === 'object' && err.details) {
      details = err.details as Record<string, unknown>;
    }
  }

  return {
    message: message || defaultMessage,
    code,
    status,
    details,
  };
}

/**
 * Checks if an error is a network error (no response received)
 *
 * @param error - The error to check
 * @returns True if it's a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;

    // Axios network error (no response)
    if ('request' in err && !('response' in err)) {
      return true;
    }

    // Check for common network error messages
    if ('message' in err && typeof err.message === 'string') {
      const msg = err.message.toLowerCase();
      return (
        msg.includes('network error') ||
        msg.includes('failed to fetch') ||
        msg.includes('net::err')
      );
    }
  }

  return false;
}

/**
 * Checks if an error is an authentication error (401/403)
 *
 * @param error - The error to check
 * @returns True if it's an auth error
 */
export function isAuthError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;

    // Check direct status
    if ('status' in err && typeof err.status === 'number') {
      return err.status === 401 || err.status === 403;
    }

    // Check response.status (Axios)
    if ('response' in err && typeof err.response === 'object' && err.response) {
      const response = err.response as Record<string, unknown>;
      if ('status' in response && typeof response.status === 'number') {
        return response.status === 401 || response.status === 403;
      }
    }
  }

  return false;
}

/**
 * Checks if an error is a rate limit error (429)
 *
 * @param error - The error to check
 * @returns True if it's a rate limit error
 */
export function isRateLimitError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;

    // Check direct status
    if ('status' in err && err.status === 429) {
      return true;
    }

    // Check response.status (Axios)
    if ('response' in err && typeof err.response === 'object' && err.response) {
      const response = err.response as Record<string, unknown>;
      if ('status' in response && response.status === 429) {
        return true;
      }
    }

    // Check error code
    if ('error' in err && typeof err.error === 'object' && err.error) {
      const errorObj = err.error as Record<string, unknown>;
      if ('error_code' in errorObj && errorObj.error_code === 'RATE_LIMIT_EXCEEDED') {
        return true;
      }
    }
  }

  return false;
}
