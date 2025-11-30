'use client';

import { Button } from '@/components/ui/button';
import { AlertOctagon, RefreshCw } from 'lucide-react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
          <div className="max-w-md w-full text-center">
            <div className="mb-8">
              <div className="mx-auto w-20 h-20 bg-red-900/30 rounded-full flex items-center justify-center mb-6">
                <AlertOctagon className="w-10 h-10 text-red-400" />
              </div>
              <h1 className="text-3xl font-bold text-white mb-3">
                Critical Error
              </h1>
              <p className="text-gray-400 mb-6">
                A critical error has occurred. We&apos;ve been notified and are working to fix it.
              </p>
              {error.digest && (
                <p className="text-sm text-gray-500 font-mono bg-gray-800 rounded px-4 py-2 inline-block mb-6">
                  Reference: {error.digest}
                </p>
              )}
            </div>

            <Button
              onClick={reset}
              size="lg"
              className="flex items-center gap-2 mx-auto bg-blue-600 hover:bg-blue-700"
            >
              <RefreshCw className="w-5 h-5" />
              Reload Application
            </Button>

            <p className="mt-8 text-sm text-gray-500">
              If reloading doesn&apos;t help, try clearing your browser cache or{' '}
              <a href="mailto:support@aidesigntool.com" className="text-blue-400 hover:underline">
                contact support
              </a>
            </p>
          </div>
        </div>
      </body>
    </html>
  );
}
