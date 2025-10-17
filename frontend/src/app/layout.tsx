import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';
// TODO: Re-enable sonner after fixing pnpm installation
// import { Toaster } from 'sonner';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Forglass Regenerator Optimizer',
  description: 'System optymalizacji regeneratorów pieców szklarskich',
  keywords: ['forglass', 'regenerator', 'optimization', 'glass', 'furnace'],
  authors: [{ name: 'Forglass Engineering Team' }],
  robots: 'noindex, nofollow', // Production deployment should remove this
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pl" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        <AuthProvider>
          <div className="min-h-screen bg-background font-sans antialiased">
            {children}
          </div>
          {/* TODO: Re-enable Toaster after fixing pnpm installation */}
          {/* <Toaster position="top-right" richColors closeButton /> */}
        </AuthProvider>
      </body>
    </html>
  );
}
