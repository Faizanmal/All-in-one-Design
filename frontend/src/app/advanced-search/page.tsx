'use client';

import { useState } from 'react';
import advancedSearchApi, { 
  Project, 
  Asset, 
  Template, 
  Team,
  ProjectSearchFilters,
  AssetSearchFilters,
  TemplateSearchFilters,
  TeamSearchFilters
} from '@/lib/advanced-search-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import Image from 'next/image';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { 
  Search, 
  FileText, 
  Image as ImageIcon, 
  Layout, 
  Users,
  Filter,
  X
} from 'lucide-react';

export default function AdvancedSearchPage() {
  const [query, setQuery] = useState('');
  const [activeTab, setActiveTab] = useState('global');
  const [loading, setLoading] = useState(false);
  
  // Results
  const [projects, setProjects] = useState<Project[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  
  // Filters
  const [projectFilters, setProjectFilters] = useState<ProjectSearchFilters>({});
  const [assetFilters, setAssetFilters] = useState<AssetSearchFilters>({});
  const [templateFilters, setTemplateFilters] = useState<TemplateSearchFilters>({});
  const [teamFilters, setTeamFilters] = useState<TeamSearchFilters>({});

  // Usable: Clear filters handlers
  const clearAssetFilters = () => setAssetFilters({});
  const clearTemplateFilters = () => setTemplateFilters({});
  const clearTeamFilters = () => setTeamFilters({});
  
  const { toast } = useToast();

  // Global search
  const handleGlobalSearch = async () => {
    if (!query.trim()) return;
    
    try {
      setLoading(true);
      const response = await advancedSearchApi.global(query);
      setProjects(response.data.projects);
      setAssets(response.data.assets);
      setTemplates(response.data.templates);
      setTeams(response.data.teams);
    } catch (error) {
      // Usable: log error for debugging
      console.error('Global search error:', error);
      toast({
        title: 'Error',
        description: 'Failed to perform search',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Search projects
  const handleProjectSearch = async () => {
    try {
      setLoading(true);
      const response = await advancedSearchApi.projects({
        ...projectFilters,
        q: query,
      });
      setProjects(response.data.results);
    } catch (error) {
      // Usable: log error for debugging
      console.error('Project search error:', error);
      toast({
        title: 'Error',
        description: 'Failed to search projects',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Search assets
  const handleAssetSearch = async () => {
    try {
      setLoading(true);
      const response = await advancedSearchApi.assets({
        ...assetFilters,
        q: query,
      });
      setAssets(response.data.results);
    } catch (error) {
      // Usable: log error for debugging
      console.error('Asset search error:', error);
      toast({
        title: 'Error',
        description: 'Failed to search assets',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Search templates
  const handleTemplateSearch = async () => {
    try {
      setLoading(true);
      const response = await advancedSearchApi.templates({
        ...templateFilters,
        q: query,
      });
      setTemplates(response.data.results);
    } catch (error) {
      // Usable: log error for debugging
      console.error('Template search error:', error);
      toast({
        title: 'Error',
        description: 'Failed to search templates',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Search teams
  const handleTeamSearch = async () => {
    try {
      setLoading(true);
      const response = await advancedSearchApi.teams({
        ...teamFilters,
        q: query,
      });
      setTeams(response.data.results);
    } catch (error) {
      // Usable: log error for debugging
      console.error('Team search error:', error);
      toast({
        title: 'Error',
        description: 'Failed to search teams',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle search based on active tab
  const handleSearch = () => {
    switch (activeTab) {
      case 'global':
        handleGlobalSearch();
        break;
      case 'projects':
        handleProjectSearch();
        break;
      case 'assets':
        handleAssetSearch();
        break;
      case 'templates':
        handleTemplateSearch();
        break;
      case 'teams':
        handleTeamSearch();
        break;
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Advanced Search</h1>
        <p className="text-muted-foreground">Search across projects, assets, templates, and teams</p>
      </div>

      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Input
              placeholder="Search..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1"
            />
            <Button onClick={handleSearch} disabled={loading}>
              <Search className="w-4 h-4 mr-2" />
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="global">
            <Search className="w-4 h-4 mr-2" />
            All
          </TabsTrigger>
          <TabsTrigger value="projects">
            <FileText className="w-4 h-4 mr-2" />
            Projects
          </TabsTrigger>
          <TabsTrigger value="assets">
            <ImageIcon className="w-4 h-4 mr-2" />
            Assets
          </TabsTrigger>
          <TabsTrigger value="templates">
            <Layout className="w-4 h-4 mr-2" />
            Templates
          </TabsTrigger>
          <TabsTrigger value="teams">
            <Users className="w-4 h-4 mr-2" />
            Teams
          </TabsTrigger>
        </TabsList>

        <TabsContent value="global" className="space-y-6">
          {projects.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Projects ({projects.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {projects.map((project) => (
                    <Card key={project.id}>
                      <CardContent className="pt-4">
                        <h3 className="font-semibold">{project.name}</h3>
                        <p className="text-sm text-muted-foreground">{project.description}</p>
                        <div className="flex gap-2 mt-2">
                          <Badge>{project.type}</Badge>
                          {project.tags?.map((tag) => (
                            <Badge key={tag} variant="outline">{tag}</Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {assets.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Assets ({assets.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-4">
                  {assets.map((asset) => (
                    <Card key={asset.id}>
                      <CardContent className="pt-4">
                        {asset.thumbnail && (
                          <Image src={asset.thumbnail} alt={asset.name} width={400} height={128} className="w-full h-32 object-cover rounded mb-2" />
                        )}
                        <p className="text-sm font-semibold truncate">{asset.name}</p>
                        <p className="text-xs text-muted-foreground">{asset.file_type}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {templates.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Templates ({templates.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  {templates.map((template) => (
                    <Card key={template.id}>
                      <CardContent className="pt-4">
                        {template.thumbnail && (
                          <Image src={template.thumbnail} alt={template.name} width={400} height={160} className="w-full h-40 object-cover rounded mb-2" />
                        )}
                        <h3 className="font-semibold">{template.name}</h3>
                        <p className="text-sm text-muted-foreground">{template.category}</p>
                        <div className="flex gap-2 mt-2">
                          {template.is_premium && <Badge>Premium</Badge>}
                          {template.is_featured && <Badge variant="secondary">Featured</Badge>}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {teams.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Teams ({teams.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {teams.map((team) => (
                    <Card key={team.id}>
                      <CardContent className="pt-4">
                        <h3 className="font-semibold">{team.name}</h3>
                        <p className="text-sm text-muted-foreground">{team.description}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {team.member_count} members • {team.project_count} projects
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="projects" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Project Filters</CardTitle>
              <CardDescription>Use filters to refine your project search. <Filter className="inline w-4 h-4" /></CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select
                value={projectFilters.type}
                onValueChange={(value) => setProjectFilters({ ...projectFilters, type: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Project Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="graphic_design">Graphic Design</SelectItem>
                  <SelectItem value="ui_ux">UI/UX Design</SelectItem>
                  <SelectItem value="logo">Logo</SelectItem>
                </SelectContent>
              </Select>
              
              <Select
                value={projectFilters.sort}
                onValueChange={(value) => setProjectFilters({ ...projectFilters, sort: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sort By" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="-created_at">Newest First</SelectItem>
                  <SelectItem value="created_at">Oldest First</SelectItem>
                  <SelectItem value="name">Name A-Z</SelectItem>
                  <SelectItem value="-name">Name Z-A</SelectItem>
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Results</CardTitle>
            </CardHeader>
            <CardContent>
              {projects.length === 0 ? (
                <p className="text-muted-foreground">No projects found</p>
              ) : (
                <div className="space-y-2">
                  {projects.map((project) => (
                    <Card key={project.id}>
                      <CardContent className="pt-4">
                        <h3 className="font-semibold">{project.name}</h3>
                        <p className="text-sm text-muted-foreground">{project.description}</p>
                        <div className="flex gap-2 mt-2">
                          <Badge>{project.type}</Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="assets">
          <Card>
            <CardHeader>
              <CardTitle>Asset Results</CardTitle>
              <CardDescription>Clear asset filters <Button variant="ghost" size="sm" onClick={clearAssetFilters}><X className="w-4 h-4" /></Button></CardDescription>
            </CardHeader>
            <CardContent>
              {assets.length === 0 ? (
                <p className="text-muted-foreground">No assets found</p>
              ) : (
                <div className="grid grid-cols-4 gap-4">
                  {assets.map((asset) => (
                    <Card key={asset.id}>
                      <CardContent className="pt-4">
                        {asset.thumbnail && (
                          <Image src={asset.thumbnail} alt={asset.name} width={400} height={128} className="w-full h-32 object-cover rounded mb-2" />
                        )}
                        <p className="text-sm font-semibold truncate">{asset.name}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates">
          <Card>
            <CardHeader>
              <CardTitle>Template Results</CardTitle>
              <CardDescription>Clear template filters <Button variant="ghost" size="sm" onClick={clearTemplateFilters}><X className="w-4 h-4" /></Button></CardDescription>
            </CardHeader>
            <CardContent>
              {templates.length === 0 ? (
                <p className="text-muted-foreground">No templates found</p>
              ) : (
                <div className="grid grid-cols-3 gap-4">
                  {templates.map((template) => (
                    <Card key={template.id}>
                      <CardContent className="pt-4">
                        {template.thumbnail && (
                          <Image src={template.thumbnail} alt={template.name} width={400} height={160} className="w-full h-40 object-cover rounded mb-2" />
                        )}
                        <h3 className="font-semibold">{template.name}</h3>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="teams">
          <Card>
            <CardHeader>
              <CardTitle>Team Results</CardTitle>
              <CardDescription>Clear team filters <Button variant="ghost" size="sm" onClick={clearTeamFilters}><X className="w-4 h-4" /></Button></CardDescription>
            </CardHeader>
            <CardContent>
              {teams.length === 0 ? (
                <p className="text-muted-foreground">No teams found</p>
              ) : (
                <div className="space-y-2">
                  {teams.map((team) => (
                    <Card key={team.id}>
                      <CardContent className="pt-4">
                        <h3 className="font-semibold">{team.name}</h3>
                        <p className="text-sm text-muted-foreground">{team.description}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
