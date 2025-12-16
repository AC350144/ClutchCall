import { apiJson } from "./apiClient";

export type AuthOk = { status: string } | { status: "ok" } | Record<string, unknown>;

/**
 * Matches backend routes:
 *   GET  /validate
 *   POST /login
 *   POST /register
 *   POST /logout
 *
 * Frontend uses "/api/*" and Vite proxy rewrites to backend.
 */

export async function validateSession(): Promise<AuthOk> {
  return apiJson<AuthOk>("/validate", { method: "GET" });
}

export async function login(email: string, password: string): Promise<AuthOk> {
  return apiJson<AuthOk>("/login", {
    method: "POST",
    body: { email, password },
  });
}

export async function register(email: string, password: string): Promise<AuthOk> {
  return apiJson<AuthOk>("/register", {
    method: "POST",
    body: { email, password },
  });
}

export async function logout(): Promise<AuthOk> {
  return apiJson<AuthOk>("/logout", { method: "POST" });
}
