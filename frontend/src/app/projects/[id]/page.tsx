/**
 * Project Editor Page
 * Main collaborative design editor with canvas, comments, AI tools
 */
'use client';

import { useState, useLayoutEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { useCollaborativeCanvas } from '@/hooks/useCollaborativeCanvas';
import { CanvasContainer } from '@/components/canvas/CanvasContainer';
import { CanvasToolbar } from '@/components/canvas/CanvasToolbar';
import { PropertiesPanel } from '@/components/canvas/PropertiesPanel';
import { CommentsPanel } from '@/components/collaboration/CommentsPanel';
import { AIVariantsGenerator } from '@/components/ai/AIVariantsGenerator';
import { TemplateSidebar } from '@/components/templates/TemplateSidebar';
import { VersionHistoryPanel } from '@/components/version/VersionHistoryPanel';
import { ExportModal } from '@/components/export/ExportModal';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  MessageSquare, 
  Sparkles, 
  Layout, 
  History, 
  Users,
  Download,
  Save
} from 'lucide-react';

export default function ProjectPage() {
  const params = useParams();
  const projectId = parseInt(params.id as string);
  const [project, setProject] = useState<{
    name: string;
    canvas_width: number;
    canvas_height: number;
    [key: string]: unknown;
  } | null>(null);
  const [token] = useState(() => localStorage.getItem('token') || '');
  const [activePanel, setActivePanel] = useState<'comments' | 'ai' | 'templates' | 'history' | 'properties' | null>(null);
  const [saving, setSaving] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [selectedElements, setSelectedElements] = useState<Record<string, unknown>[]>([]);

  const {
    isConnected,
    activeUsers,
    updateElement,
    createElement,
    deleteElement,
    sendCursorPosition,
    updateSelection
  } = useCollaborativeCanvas(projectId, token);

  const fetchProject = useCallback(async () => {
    try {
      const res = await fetch(`/api/projects/projects/${projectId}/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setProject(data);
      }
    } catch (error) {
      console.error('Failed to fetch project:', error);
    }
  }, [projectId, token]);

  useLayoutEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchProject();
  }, [fetchProject]);

  const handleSave = async () => {
    setSaving(true);
    // Implement save logic
    setTimeout(() => setSaving(false), 1000);
  };

  const handleExport = () => {
    setShowExportModal(true);
  };

  const handleSelectionChange = (selectedIds: string[]) => {
    updateSelection(selectedIds);
    // TODO: Get actual element objects from canvas
    setSelectedElements(selectedIds.map(id => ({ id })));
  };

  if (!project) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Main Canvas Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Toolbar */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                {project.name}
              </h1>
              
              {/* Collaboration Status */}
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
                {activeUsers.length > 0 && (
                  <div className="flex items-center gap-1 ml-2">
                    <Users className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {activeUsers.length} online
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActivePanel(activePanel === 'templates' ? null : 'templates')}
              >
                <Layout className="w-4 h-4 mr-2" />
                Templates
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActivePanel(activePanel === 'ai' ? null : 'ai')}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                AI Tools
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActivePanel(activePanel === 'comments' ? null : 'comments')}
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                Comments
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setActivePanel(activePanel === 'history' ? null : 'history')}
              >
                <History className="w-4 h-4 mr-2" />
                History
              </Button>

              <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

              <Button
                variant="outline"
                size="sm"
                onClick={handleExport}
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>

              <Button
                size="sm"
                onClick={handleSave}
                disabled={saving}
              >
                <Save className="w-4 h-4 mr-2" />
                {saving ? 'Saving...' : 'Save'}
              </Button>
            </div>
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 relative overflow-hidden">
          <CanvasToolbar
            onAddText={() => console.log('Add text')}
            onAddRectangle={() => console.log('Add rectangle')}
            onAddCircle={() => console.log('Add circle')}
            onAddImage={() => console.log('Add image')}
            onDelete={() => console.log('Delete')}
            onClone={() => console.log('Clone')}
            onBringToFront={() => console.log('Bring to front')}
            onSendToBack={() => console.log('Send to back')}
            onExportPNG={() => console.log('Export PNG')}
            onExportSVG={() => console.log('Export SVG')}
            onSave={handleSave}
            onAIGenerate={() => console.log('AI Generate')}
            hasSelection={selectedElements.length > 0}
          />
          
          <CanvasContainer
            projectId={projectId}
            project={project}
            isConnected={isConnected}
            activeUsers={activeUsers}
            onElementUpdate={updateElement}
            onElementCreate={createElement}
            onElementDelete={deleteElement}
            onCursorMove={sendCursorPosition}
            onSelectionChange={handleSelectionChange}
          />
        </div>

        {/* Status Bar */}
        <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-2">
          <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
            <div className="flex items-center gap-4">
              <span>Canvas: {project?.canvas_width} × {project?.canvas_height}</span>
              <span>Last saved: Just now</span>
            </div>
            <div className="flex items-center gap-4">
              {activeUsers.map((user) => (
                <div key={user.user_id} className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-blue-500" />
                  <span>{user.username}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar Panels */}
      {activePanel && (
        <div className="w-96 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col">
          {activePanel === 'comments' && (
            <CommentsPanel 
              projectId={projectId}
              onCommentClick={(comment) => {
                // Jump to comment position on canvas
                console.log('Jump to comment:', comment);
              }}
            />
          )}

          {activePanel === 'ai' && (
            <div className="flex-1 overflow-y-auto p-4">
              <Tabs defaultValue="variants" className="w-full">
                <TabsList className="w-full">
                  <TabsTrigger value="variants" className="flex-1">Variants</TabsTrigger>
                  <TabsTrigger value="improve" className="flex-1">Improve</TabsTrigger>
                  <TabsTrigger value="a11y" className="flex-1">A11y</TabsTrigger>
                </TabsList>
                
                <TabsContent value="variants" className="mt-4">
                  <AIVariantsGenerator
                    onVariantSelect={(variant) => {
                      console.log('Apply variant:', variant);
                      // Apply variant to canvas
                    }}
                  />
                </TabsContent>
                
                <TabsContent value="improve" className="mt-4">
                  <div className="space-y-4">
                    <h3 className="font-semibold">AI Suggestions</h3>
                    <Button className="w-full">
                      <Sparkles className="w-4 h-4 mr-2" />
                      Get Improvement Suggestions
                    </Button>
                  </div>
                </TabsContent>
                
                <TabsContent value="a11y" className="mt-4">
                  <div className="space-y-4">
                    <h3 className="font-semibold">Accessibility Check</h3>
                    <Button className="w-full">
                      Check WCAG Compliance
                    </Button>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}

          {activePanel === 'templates' && (
            <TemplateSidebar
              onTemplateSelect={(template) => {
                console.log('Apply template:', template);
              }}
            />
          )}

          {activePanel === 'history' && (
            <VersionHistoryPanel projectId={projectId} />
          )}

          {activePanel === 'properties' && (
            <PropertiesPanel
              selectedElements={selectedElements}
              onPropertyChange={(property, value) => {
                console.log('Property changed:', property, value);
              }}
            />
          )}
        </div>
      )}

      {/* Export Modal */}
      <ExportModal
        open={showExportModal}
        onOpenChange={setShowExportModal}
        projectId={projectId}
      />
    </div>
  );
}
