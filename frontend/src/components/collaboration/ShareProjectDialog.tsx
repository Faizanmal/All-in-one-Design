'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Share2, Copy, UserPlus, Loader2 } from 'lucide-react';
import { projectsAPI } from '@/lib/design-api';
import { useToast } from '@/hooks/use-toast';

interface ShareProjectDialogProps {
  projectId: number;
  projectName?: string;
  trigger?: React.ReactNode;
}

export function ShareProjectDialog({
  projectId,
  projectName,
  trigger,
}: ShareProjectDialogProps) {
  const [open, setOpen] = useState(false);
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const shareUrl =
    typeof window !== 'undefined'
      ? `${window.location.origin}/editor?project=${projectId}`
      : `/editor?project=${projectId}`;

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      toast({ title: 'Link copied', description: 'Anyone with access can open this project.' });
    } catch {
      toast({
        title: 'Copy failed',
        description: shareUrl,
        variant: 'destructive',
      });
    }
  };

  const handleInvite = async () => {
    if (!username.trim()) return;
    setLoading(true);
    try {
      await projectsAPI.addCollaborator(projectId, username.trim());
      toast({
        title: 'Collaborator added',
        description: `${username.trim()} can now edit this project.`,
      });
      setUsername('');
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Could not add collaborator';
      toast({
        title: 'Invite failed',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm" className="gap-1.5">
            <Share2 className="h-3.5 w-3.5" />
            Share
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Share project</DialogTitle>
          <DialogDescription>
            Invite collaborators or copy a link to {projectName || 'this project'}.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-2">
            <Label htmlFor="share-link">Editor link</Label>
            <div className="flex gap-2">
              <Input id="share-link" readOnly value={shareUrl} className="text-xs" />
              <Button type="button" variant="secondary" size="icon" onClick={handleCopyLink}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="invite-user">Invite by username</Label>
            <div className="flex gap-2">
              <Input
                id="invite-user"
                placeholder="teammate_username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleInvite();
                  }
                }}
              />
              <Button type="button" onClick={handleInvite} disabled={loading || !username.trim()}>
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <UserPlus className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Done
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
