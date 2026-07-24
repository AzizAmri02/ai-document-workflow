import { apiRequest, setToken } from "./client";
import type { User } from "../types";

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function register(email: string, password: string, fullName: string): Promise<User> {
  return apiRequest<User>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
}

export async function login(email: string, password: string): Promise<void> {
  const response = await apiRequest<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(response.access_token);
}

export function logout(): void {
  setToken(null);
}

export async function getCurrentUser(): Promise<User> {
  return apiRequest<User>("/api/auth/me");
}
