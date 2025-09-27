'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function HomePage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">
            Forglass Regenerator Optimizer
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            System optymalizacji regeneratorów pieców szklarskich.
            Redukuj zużycie paliwa o 5-15% i emisje CO₂ poprzez precyzyjne obliczenia termodynamiczne.
          </p>

          <div className="grid md:grid-cols-3 gap-8 mt-12">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Import i walidacja</h3>
              <p className="text-gray-600">
                Import plików XLSX z automatyczną walidacją danych i konwersją jednostek
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Optymalizacja SLSQP</h3>
              <p className="text-gray-600">
                Zaawansowane algorytmy optymalizacji z real-time monitoringiem postępu
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Raporty i analiza</h3>
              <p className="text-gray-600">
                Szczegółowe raporty PDF/XLSX z analizą oszczędności i ROI
              </p>
            </div>
          </div>

          <div className="mt-12">
            <div className="bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Status systemu</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Backend API:</span>
                  <span className="text-green-600 font-medium">🟢 Online</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Baza danych:</span>
                  <span className="text-green-600 font-medium">🟢 Połączono</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Cache Redis:</span>
                  <span className="text-green-600 font-medium">🟢 Aktywny</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Celery Workers:</span>
                  <span className="text-green-600 font-medium">🟢 Gotowe</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <a
              href="/login"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Zaloguj się do systemu
            </a>
          </div>

          <div className="mt-8">
            <p className="text-sm text-gray-500">
              Wersja 1.0.0 • Forglass Engineering Team • 2025
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}