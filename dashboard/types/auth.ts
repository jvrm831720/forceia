export interface LoginCredentials {
  email: string;
  password: string;
  remember?: boolean;
}

export type AuthErrorCode =
  | "invalid_credentials"
  | "invalid_email"
  | "empty_password"
  | "account_disabled"
  | "connection_error"
  | "rate_limited"
  | "unknown";

export interface AuthError {
  code: AuthErrorCode;
  message: string;
}

export type LoginResult =
  | { ok: true }
  | { ok: false; error: AuthError };

export type PasswordResetResult =
  | { ok: true }
  | { ok: false; error: AuthError };

export interface PasswordResetRequest {
  email: string;
}
