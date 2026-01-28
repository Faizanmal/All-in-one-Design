import type { FabricCanvas, FabricObject, FabricEvent } from '@/types/fabric';
"use client";

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Sparkles, Loader2 } from 'lucide-react';
import { aiAPI } from '@/lib/design-api';
import { useToast } from '@/hooks/use-toast';

interface AIGenerateDialogProps {
  onGenerate: (result: Record<string, unknown>) => void;
  designType?: 'graphic' | 'ui_ux' | 'logo';
}

export const AIGenerateDialog: React.FC<AIGenerateDialogProps> = ({
  onGenerate,
  designType = 'ui_ux',
}) => {
  const [open, setOpen] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [selectedDesignType, setSelectedDesignType] = useState<'graphic' | 'ui_ux' | 'logo'>(designType);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a prompt',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);

    try {
      const result = await aiAPI.generateLayout(prompt, selectedDesignType);
      onGenerate(result);
      setOpen(false);
      setPrompt('');
      
      toast({
        title: 'Success',
        description: 'Design generated successfully!',
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to generate design. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const examplePrompts = {
    ui_ux: [
      'Create a modern travel app UI with map and booking button',
      'Design a dashboard for analytics with charts and metrics',
      'Build a landing page for a SaaS product with hero section',
    ],
    graphic: [
      'Design a social media post for a summer sale',
      'Create a poster for a music festival',
      'Make an Instagram story template for a fashion brand',
    ],
    logo: [
      'Modern tech startup logo with blue and white colors',
      'Minimalist coffee shop logo with warm tones',
      'Professional consulting firm logo, corporate style',
    ],
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Sparkles className="h-4 w-4 mr-2" />
          AI Generate
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Generate Design with AI</DialogTitle>
          <DialogDescription>
            Describe what you want to create and our AI will generate it for you.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="design-type">Design Type</Label>
            <Select
              value={selectedDesignType}
              onValueChange={(value: 'graphic' | 'ui_ux' | 'logo') => setSelectedDesignType(value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ui_ux">UI/UX Design</SelectItem>
                <SelectItem value="graphic">Graphic Design</SelectItem>
                <SelectItem value="logo">Logo Design</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="prompt">Your Prompt</Label>
            <Textarea
              id="prompt"
              placeholder="Describe your design..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              className="resize-none"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm text-muted-foreground">Example Prompts:</Label>
            <div className="space-y-1">
              {examplePrompts[selectedDesignType].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setPrompt(example)}
                  className="block w-full text-left text-sm text-muted-foreground hover:text-foreground hover:bg-accent px-2 py-1 rounded transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => setOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleGenerate} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AIGenerateDialog;
