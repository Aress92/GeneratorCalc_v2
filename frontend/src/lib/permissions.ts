/**
 * Permission helpers for role-based access control.
 *
 * Pomocniki uprawnień dla kontroli dostępu opartej na rolach.
 */

import { User, UserRole } from './auth';

export type Permission =
  | 'admin'
  | 'engineer'
  | 'create_scenarios'
  | 'manage_users'
  | 'view_reports'
  | 'create_reports'
  | 'manage_materials'
  | 'import_data';

export const hasPermission = (user: User | null, permission: Permission): boolean => {
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

    case 'view_reports':
      return true; // All authenticated users can view reports

    case 'create_reports':
      return user.role === UserRole.ENGINEER || user.role === UserRole.ADMIN;

    case 'manage_materials':
      return user.role === UserRole.ENGINEER || user.role === UserRole.ADMIN;

    case 'import_data':
      return user.role === UserRole.ENGINEER || user.role === UserRole.ADMIN;

    default:
      return false;
  }
};

export const canAccessPage = (user: User | null, page: string): boolean => {
  if (!user) return false;

  switch (page) {
    case '/dashboard':
      return true; // All authenticated users
    case '/configurator':
      return hasPermission(user, 'engineer');
    case '/import':
      return hasPermission(user, 'import_data');
    case '/optimize':
      return hasPermission(user, 'create_scenarios');
    case '/reports':
      return hasPermission(user, 'view_reports');
    case '/admin':
      return hasPermission(user, 'admin');
    default:
      return true;
  }
};

export const getPermissionDisplayName = (permission: Permission): string => {
  switch (permission) {
    case 'admin':
      return 'Administrator';
    case 'engineer':
      return 'Inżynier';
    case 'create_scenarios':
      return 'Tworzenie scenariuszy';
    case 'manage_users':
      return 'Zarządzanie użytkownikami';
    case 'view_reports':
      return 'Podgląd raportów';
    case 'create_reports':
      return 'Tworzenie raportów';
    case 'manage_materials':
      return 'Zarządzanie materiałami';
    case 'import_data':
      return 'Import danych';
    default:
      return permission;
  }
};