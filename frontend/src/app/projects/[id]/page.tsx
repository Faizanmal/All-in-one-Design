'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

/**
 * Legacy project editor route — redirects to canonical /editor?project=.
 */
export default function ProjectPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  useEffect(() => {
    if (projectId) {
      router.replace(`/editor?project=${projectId}`);
    } else {
      router.replace('/editor');
    }
  }, [projectId, router]);

  return (
    <div className="flex h-screen items-center justify-center gap-2 text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" />
      Opening editor…
    </div>
  );
}
