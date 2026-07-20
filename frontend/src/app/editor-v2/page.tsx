'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import { Loader2 } from 'lucide-react';

/**
 * Legacy Pro Editor route — redirects to the canonical /editor.
 */
function EditorV2Redirect() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    if (!params.get('project') && params.get('projectId')) {
      params.set('project', params.get('projectId')!);
      params.delete('projectId');
    }
    const qs = params.toString();
    router.replace(qs ? `/editor?${qs}` : '/editor');
  }, [router, searchParams]);

  return (
    <div className="flex h-screen items-center justify-center gap-2 text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" />
      Opening editor…
    </div>
  );
}

export default function EnhancedEditorPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen items-center justify-center">
          <Loader2 className="h-4 w-4 animate-spin" />
        </div>
      }
    >
      <EditorV2Redirect />
    </Suspense>
  );
}
