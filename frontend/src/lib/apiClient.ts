export type ApiErrorInfo = {
  status: number;
  message: string;
  url: string;
  bodyText?: string;
};

export class ApiError extends Error {
  info: ApiErrorInfo;

  constructor(info: ApiErrorInfo) {
    super(info.message);
    this.name = "ApiError";
    this.info = info;
  }
}

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  headers?: Record<string, string>;
  body?: unknown;
  credentials?: RequestCredentials; // default "include"
  signal?: AbortSignal;
};

function normalizePath(path: string) {
  // Always treat input as "/something"
  if (!path.startsWith("/")) return `/${path}`;
  return path;
}

/**
 * Generic JSON request helper.
 * Uses Vite proxy base "/api" so frontend can call backend without CORS issues during dev.
 */
export async function apiJson<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `/api${normalizePath(path)}`;

  const res = await fetch(url, {
    method: options.method ?? "GET",
    credentials: options.credentials ?? "include",
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers ?? {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
    signal: options.signal,
  });

  // Try parse JSON; if not JSON, fall back to text for debugging
  const contentType = res.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");

  if (!res.ok) {
    let bodyText: string | undefined;
    try {
      bodyText = await res.text();
    } catch {
      bodyText = undefined;
    }

    throw new ApiError({
      status: res.status,
      message: `API request failed (${res.status})`,
      url,
      bodyText,
    });
  }

  if (isJson) {
    return (await res.json()) as T;
  }

  // If backend returns non-json success (rare), return as any
  const text = await res.text();
  return text as unknown as T;
}

/**
 * Same as apiJson but returns raw text.
 */
export async function apiText(
  path: string,
  options: RequestOptions = {}
): Promise<string> {
  const url = `/api${normalizePath(path)}`;

  const res = await fetch(url, {
    method: options.method ?? "GET",
    credentials: options.credentials ?? "include",
    headers: {
      ...(options.headers ?? {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
    signal: options.signal,
  });

  if (!res.ok) {
    let bodyText: string | undefined;
    try {
      bodyText = await res.text();
    } catch {
      bodyText = undefined;
    }

    throw new ApiError({
      status: res.status,
      message: `API request failed (${res.status})`,
      url,
      bodyText,
    });
  }

  return await res.text();
}
