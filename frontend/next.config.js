/** @type {import('next').NextConfig} */
const nextConfig = {
  // Production optimization: standalone output for Docker
  output: 'standalone',

  typescript: {
    // Włącza strict mode dla TypeScript
    tsconfigPath: './tsconfig.json',
  },
  eslint: {
    // Włącza ESLint podczas build
    ignoreDuringBuilds: false,
  },
  // Server Actions are now enabled by default in Next.js 14
  // Konfiguracja obrazów
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif'],
  },
  // Konfiguracja CORS dla development
  async rewrites() {
    return process.env.NODE_ENV === 'development'
      ? [
          {
            source: '/api/:path*',
            destination: 'http://backend:8000/api/:path*',
          },
        ]
      : [];
  },
  // Konfiguracja headers bezpieczeństwa
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
  // Optymalizacja bundle
  webpack: (config, { isServer }) => {
    // Optymalizacja dla Plotly.js
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        module: false,
      };
    }
    return config;
  },
  // Konfiguracja środowiska
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
};

module.exports = nextConfig;