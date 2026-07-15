import axios from "axios";

import { env } from "@/config/env";
import { sessionStore } from "@/store/session-store";

export const httpClient = axios.create({
  baseURL: `${env.apiBaseUrl}/api/v1`,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

httpClient.interceptors.request.use((config) => {
  const token = sessionStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

httpClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = sessionStore.getState().refreshToken;
      if (!refreshToken) {
        sessionStore.getState().clearSession();
        return Promise.reject(error);
      }
      try {
        const response = await axios.post(`${env.apiBaseUrl}/auth/refresh`, { refresh_token: refreshToken });
        const tokens = response.data.tokens ?? response.data;
        sessionStore.getState().setTokens({
          accessToken: tokens.access_token ?? tokens.accessToken,
          refreshToken: tokens.refresh_token ?? tokens.refreshToken,
          tokenType: tokens.token_type ?? tokens.tokenType ?? "bearer",
          accessExpiresIn: tokens.access_expires_in ?? tokens.accessExpiresIn ?? 0,
          refreshExpiresIn: tokens.refresh_expires_in ?? tokens.refreshExpiresIn ?? 0,
        });
        originalRequest.headers.Authorization = `Bearer ${sessionStore.getState().accessToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        sessionStore.getState().clearSession();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);
