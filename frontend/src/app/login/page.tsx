"use client";

import dynamic from 'next/dynamic';
import { Suspense } from 'react';
import { Loader2 } from 'lucide-react';

const LoginPage = dynamic(() => import('./LoginPage'), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <Loader2 className="h-12 w-12 animate-spin text-gray-900 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Loading Login
        </h2>
        <p className="text-gray-500">
          Please wait...
        </p>
      </div>
    </div>
  )
});

export default function Page() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-gray-900 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Loading Login
          </h2>
          <p className="text-gray-500">
            Please wait...
          </p>
        </div>
      </div>
    }>
      <LoginPage />
    </Suspense>
  );
}
