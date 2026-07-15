import { httpClient } from "@/services/api/http-client";
import type { AuthResponse, RegistrationResponse } from "@/types/auth";

export type LoginRequest = {
  identifier: string;
  password: string;
  deviceId?: string;
  deviceName?: string;
  deviceFingerprint?: string;
};

export type RegisterRequest = {
  email: string;
  username: string;
  displayName: string;
  password: string;
  phoneNumber?: string;
};

export type ForgotPasswordRequest = { email: string };
export type ResetPasswordRequest = { token: string; newPassword: string };

export async function login(request: LoginRequest): Promise<AuthResponse> {
  const { data } = await httpClient.post("/auth/login", {
    identifier: request.identifier,
    password: request.password,
    device_id: request.deviceId,
    device_name: request.deviceName,
    device_fingerprint: request.deviceFingerprint,
  });
  return data;
}

export async function register(request: RegisterRequest): Promise<RegistrationResponse> {
  const { data } = await httpClient.post("/auth/register", {
    email: request.email,
    username: request.username,
    display_name: request.displayName,
    password: request.password,
    phone_number: request.phoneNumber,
  });
  return data;
}

export async function forgotPassword(request: ForgotPasswordRequest): Promise<{ message: string }> {
  const { data } = await httpClient.post("/auth/forgot-password", { email: request.email });
  return data;
}

export async function resetPassword(request: ResetPasswordRequest): Promise<{ message: string }> {
  const { data } = await httpClient.post("/auth/reset-password", {
    token: request.token,
    new_password: request.newPassword,
  });
  return data;
}

export async function loadSession(): Promise<{ session: unknown }> {
  const { data } = await httpClient.get("/auth/session");
  return data;
}
