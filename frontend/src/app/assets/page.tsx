'use client';

import { useState, useEffect, useCallback } from 'react';
import { assetVersionsApi, assetCommentsApi, assetCollectionsApi, AssetVersion, AssetComment, AssetCollection } from '@/lib/assets-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Clock, 
  MessageSquare, 
  FolderOpen, 
  RotateCcw, 
  Plus
} from 'lucide-react';

export default function AssetsPage() {
  // Use setSelectedAssetId for asset selection in UI
  const [selectedAssetId, setSelectedAssetId] = useState<number | null>(null);
  const [versions, setVersions] = useState<AssetVersion[]>([]);
  const [comments, setComments] = useState<AssetComment[]>([]);
  const [collections, setCollections] = useState<AssetCollection[]>([]);
  const [loading, setLoading] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [newCollectionName, setNewCollectionName] = useState('');
  const [newCollectionDesc, setNewCollectionDesc] = useState('');
  const { toast } = useToast();

  // Load versions
  const loadVersions = useCallback(async (assetId: number) => {
    try {
      setLoading(true);
      const response = await assetVersionsApi.list(assetId);
      setVersions(response.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load asset versions',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  // Load comments
  const loadComments = useCallback(async (assetId: number) => {
    try {
      const response = await assetCommentsApi.list(assetId);
      setComments(response.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load comments',
        variant: 'destructive',
      });
    }
  }, [toast]);

  // Load collections
  const loadCollections = useCallback(async () => {
    try {
      const response = await assetCollectionsApi.list();
      setCollections(response.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load collections',
        variant: 'destructive',
      });
    }
  }, [toast]);

  useEffect(() => {
    loadCollections();
  }, [loadCollections]);

  // Example usage: select first asset in collections (if any)
  useEffect(() => {
    if (collections.length > 0 && selectedAssetId === null) {
      setSelectedAssetId(collections[0].id);
    }
  }, [collections, selectedAssetId]);

  useEffect(() => {
    if (selectedAssetId) {
      loadVersions(selectedAssetId);
      loadComments(selectedAssetId);
    }
  }, [selectedAssetId, loadVersions, loadComments]);

  // Restore version
  const handleRestoreVersion = async (versionId: number) => {
    try {
      await assetVersionsApi.restore(versionId);
      toast({
        title: 'Success',
        description: 'Asset restored to selected version',
      });
      if (selectedAssetId) loadVersions(selectedAssetId);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to restore version',
        variant: 'destructive',
      });
    }
  };

  // Add comment
  const handleAddComment = async () => {
    if (!selectedAssetId || !newComment.trim()) return;
    
    try {
      await assetCommentsApi.create({
        asset: selectedAssetId,
        content: newComment,
      });
      setNewComment('');
      toast({
        title: 'Success',
        description: 'Comment added successfully',
      });
      loadComments(selectedAssetId);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to add comment',
        variant: 'destructive',
      });
    }
  };

  // Create collection
  const handleCreateCollection = async () => {
    if (!newCollectionName.trim()) return;
    
    try {
      await assetCollectionsApi.create({
        name: newCollectionName,
        description: newCollectionDesc,
      });
      setNewCollectionName('');
      setNewCollectionDesc('');
      toast({
        title: 'Success',
        description: 'Collection created successfully',
      });
      loadCollections();
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to create collection',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Asset Management</h1>
        <p className="text-muted-foreground">Manage versions, comments, and collections for your assets</p>
      </div>

      <Tabs defaultValue="versions" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="versions">
            <Clock className="w-4 h-4 mr-2" />
            Versions
          </TabsTrigger>
          <TabsTrigger value="comments">
            <MessageSquare className="w-4 h-4 mr-2" />
            Comments
          </TabsTrigger>
          <TabsTrigger value="collections">
            <FolderOpen className="w-4 h-4 mr-2" />
            Collections
          </TabsTrigger>
        </TabsList>

        <TabsContent value="versions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Asset Versions</CardTitle>
              <CardDescription>View and restore previous versions of your assets</CardDescription>
            </CardHeader>
            <CardContent>
              {!selectedAssetId ? (
                <p className="text-muted-foreground">Select an asset to view its versions</p>
              ) : loading ? (
                <p>Loading versions...</p>
              ) : versions.length === 0 ? (
                <p className="text-muted-foreground">No versions found</p>
              ) : (
                <div className="space-y-3">
                  {versions.map((version) => (
                    <Card key={version.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-semibold">Version {version.version_number}</span>
                              {version.is_current && (
                                <Badge variant="default">Current</Badge>
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              {version.description || 'No description'}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                              Created by {version.created_by.username} on{' '}
                              {new Date(version.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          {!version.is_current && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleRestoreVersion(version.id)}
                            >
                              <RotateCcw className="w-4 h-4 mr-2" />
                              Restore
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="comments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Asset Comments</CardTitle>
              <CardDescription>Leave feedback and comments on assets</CardDescription>
            </CardHeader>
            <CardContent>
              {!selectedAssetId ? (
                <p className="text-muted-foreground">Select an asset to view comments</p>
              ) : (
                <>
                  <div className="space-y-3 mb-4">
                    {comments.length === 0 ? (
                      <p className="text-muted-foreground">No comments yet</p>
                    ) : (
                      comments.map((comment) => (
                        <Card key={comment.id}>
                          <CardContent className="pt-4">
                            <div className="flex items-start justify-between">
                              <div>
                                <p className="font-semibold text-sm">{comment.user.username}</p>
                                <p className="text-sm mt-1">{comment.content}</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                  {new Date(comment.created_at).toLocaleString()}
                                </p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <Textarea
                      placeholder="Add a comment..."
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                    />
                    <Button onClick={handleAddComment}>
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Add Comment
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="collections" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Asset Collections</CardTitle>
              <CardDescription>Organize your assets into collections</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Input
                    placeholder="Collection name"
                    value={newCollectionName}
                    onChange={(e) => setNewCollectionName(e.target.value)}
                  />
                  <Textarea
                    placeholder="Description (optional)"
                    value={newCollectionDesc}
                    onChange={(e) => setNewCollectionDesc(e.target.value)}
                  />
                  <Button onClick={handleCreateCollection}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Collection
                  </Button>
                </div>

                <div className="space-y-3">
                  {collections.length === 0 ? (
                    <p className="text-muted-foreground">No collections yet</p>
                  ) : (
                    collections.map((collection) => (
                      <Card key={collection.id}>
                        <CardContent className="pt-6">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="font-semibold">{collection.name}</h3>
                              <p className="text-sm text-muted-foreground">{collection.description}</p>
                              <p className="text-xs text-muted-foreground mt-1">
                                {collection.asset_count} assets • Created{' '}
                                {new Date(collection.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            <Button variant="outline" size="sm">
                              <FolderOpen className="w-4 h-4 mr-2" />
                              Open
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
