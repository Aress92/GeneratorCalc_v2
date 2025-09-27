/**
 * Authentication utilities and API client.
 *
 * Obsługa uwierzytelniania z JWT HttpOnly cookies.
 */

import { z } from 'zod';

// API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// User roles
export enum UserRole {
  ADMIN = 'ADMIN',
  ENGINEER = 'ENGINEER',
  VIEWER = 'VIEWER'
}

// Schemas for validation
export const LoginSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  password: z.string().min(1, 'Password is required')
});

export const UserSchema = z.object({
  id: z.string().uuid(),
  username: z.string(),
  email: z.string().email(),
  full_name: z.string().nullable(),
  role: z.nativeEnum(UserRole),
  is_active: z.boolean(),
  is_verified: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
  last_login: z.string().nullable()
});

export const LoginResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
  expires_in: z.number(),
  user: UserSchema
});

export const PasswordChangeSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one digit')
    .regex(/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/, 'Password must contain at least one special character')
});

// Types
export type LoginData = z.infer<typeof LoginSchema>;
export type User = z.infer<typeof UserSchema>;
export type LoginResponse = z.infer<typeof LoginResponseSchema>;
export type PasswordChangeData = z.infer<typeof PasswordChangeSchema>;

// Auth API client
export class AuthAPI {
  private static baseURL = `${API_BASE_URL}/api/v1/auth`;

  /**
   * Login user with credentials
   */
  static async login(credentials: LoginData): Promise<LoginResponse> {
    const response = await fetch(`${this.baseURL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include HttpOnly cookies
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    return LoginResponseSchema.parse(data);
  }

  /**
   * Logout user and clear cookies
   */
  static async logout(): Promise<void> {
    const response = await fetch(`${this.baseURL}/logout`, {
      method: 'POST',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Logout failed');
    }
  }

  /**
   * Get current user information
   */
  static async getCurrentUser(): Promise<User> {
    const response = await fetch(`${this.baseURL}/me`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Not authenticated');
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get user info');
    }

    const data = await response.json();
    return UserSchema.parse(data);
  }

  /**
   * Verify if current token is valid
   */
  static async verifyToken(): Promise<{ valid: boolean; user_id?: string; username?: string; role?: UserRole }> {
    try {
      const response = await fetch(`${this.baseURL}/verify-token`, {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        return { valid: false };
      }

      return await response.json();
    } catch {
      return { valid: false };
    }
  }

  /**
   * Refresh JWT token
   */
  static async refreshToken(): Promise<{ access_token: string; expires_in: number }> {
    const response = await fetch(`${this.baseURL}/refresh`, {
      method: 'POST',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    return await response.json();
  }

  /**
   * Change user password
   */
  static async changePassword(passwordData: PasswordChangeData): Promise<void> {
    const response = await fetch(`${this.baseURL}/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(passwordData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Password change failed');
    }
  }

  /**
   * Request password reset
   */
  static async requestPasswordReset(email: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/request-password-reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Password reset request failed');
    }
  }
}

// Permission helpers
export const hasPermission = (user: User | null, permission: 'admin' | 'engineer' | 'create_scenarios' | 'manage_users'): boolean => {
  if (!user || !user.is_active) return false;

  switch (permission) {
    case 'admin':
      return user.role === UserRole.ADMIN;
    case 'engineer':
      return user.role === UserRole.ENGINEER || user.role === UserRole.ADMIN;
    case 'create_scenarios':
      return user.role === UserRole.ENGINEER || user.role === UserRole.ADMIN;
    case 'manage_users':
      return user.role === UserRole.ADMIN;
    default:
      return false;
  }
};

// Role display helpers
export const getRoleDisplayName = (role: UserRole): string => {
  switch (role) {
    case UserRole.ADMIN:
      return 'Administrator';
    case UserRole.ENGINEER:
      return 'Inżynier';
    case UserRole.VIEWER:
      return 'Podgląd';
    default:
      return role;
  }
};

export const getRoleBadgeColor = (role: UserRole): string => {
  switch (role) {
    case UserRole.ADMIN:
      return 'bg-red-100 text-red-800';
    case UserRole.ENGINEER:
      return 'bg-blue-100 text-blue-800';
    case UserRole.VIEWER:
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// Re-export withAuth for convenience
export { withAuth } from './withAuth';