"use client";

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';

function GitHubCallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { handleGitHubCallback } = useAuth();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const errorParam = searchParams.get('error');

      if (errorParam) {
        setStatus('error');
        setError(searchParams.get('error_description') || 'Authentication was cancelled');
        return;
      }

      if (!code || !state) {
        setStatus('error');
        setError('Missing authentication parameters');
        return;
      }

      try {
        await handleGitHubCallback(code, state);
        setStatus('success');
        
        // Redirect to dashboard after success
        setTimeout(() => {
          router.push('/dashboard');
        }, 1500);
      } catch (err) {
        setStatus('error');
        setError(err instanceof Error ? err.message : 'Authentication failed');
      }
    };

    processCallback();
  }, [searchParams, handleGitHubCallback, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-blue-50 to-purple-50 p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
        {status === 'loading' && (
          <>
            <Loader2 className="h-12 w-12 animate-spin text-gray-900 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Completing Sign In
            </h2>
            <p className="text-gray-500">
              Please wait while we authenticate with GitHub...
            </p>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Sign In Successful!
            </h2>
            <p className="text-gray-500">
              Redirecting to your dashboard...
            </p>
          </>
        )}

        {status === 'error' && (
          <>
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Authentication Failed
            </h2>
            <p className="text-gray-500 mb-4">
              {error || 'An error occurred during authentication'}
            </p>
            <button
              onClick={() => router.push('/login')}
              className="bg-gray-900 text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition-colors"
            >
              Back to Login
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default function GitHubCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-gray-900 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Processing Authentication
          </h2>
          <p className="text-gray-500">
            Please wait while we complete your GitHub login...
          </p>
        </div>
      </div>
    }>
      <GitHubCallbackContent />
    </Suspense>
  );
}
