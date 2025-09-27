/**
 * Higher-order component for protecting pages with authentication.
 *
 * HOC zabezpieczający strony uwierzytelnianiem.
 */

'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export function withAuth<P extends object>(Component: React.ComponentType<P>) {
  const AuthenticatedComponent = (props: P) => {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!loading && !user) {
        router.push('/login');
      }
    }, [loading, user, router]);

    // Show loading while checking auth
    if (loading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    // Don't render component until user is authenticated
    if (!user) {
      return null;
    }

    return <Component {...props} />;
  };

  // Set display name for debugging
  AuthenticatedComponent.displayName = `withAuth(${Component.displayName || Component.name})`;

  return AuthenticatedComponent;
}

export default withAuth;