import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Forglass Regenerator Optimizer',
  description: 'System optymalizacji regeneratorów pieców szklarskich',
  keywords: ['forglass', 'regenerator', 'optimization', 'glass', 'furnace'],
  authors: [{ name: 'Forglass Engineering Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'noindex, nofollow', // Production deployment should remove this
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
        </AuthProvider>
      </body>
    </html>
  );
}