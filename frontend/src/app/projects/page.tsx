"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { projectsAPI, type Project } from '@/lib/design-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, FileImage, Layout, Palette, Search } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Input } from '@/components/ui/input';
import { ErrorBoundary, InlineError } from '@/components/error-boundary';
import { ProjectGridSkeleton } from '@/components/loading-skeletons';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'recent' | 'name' | 'oldest'>('recent');
  const router = useRouter();
  const { toast } = useToast();

  const loadProjectsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectsAPI.myProjects();
      setProjects(data);
    } catch {
      setError('Failed to load projects. Please check your connection and try again.');
      toast({
        title: 'Error',
        description: 'Failed to load projects',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjectsData();
  }, [toast]);

  // Filter and sort projects
  useEffect(() => {
    const filtered = projects.filter((project) =>
      project.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'recent':
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        case 'oldest':
          return new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

    setFilteredProjects(filtered);
  }, [projects, searchTerm, sortBy]);

  const createNewProject = async (projectType: 'graphic' | 'ui_ux' | 'logo') => {
    try {
      const project = await projectsAPI.create({
        name: `New ${projectType === 'ui_ux' ? 'UI/UX' : projectType === 'graphic' ? 'Graphic' : 'Logo'} Project`,
        project_type: projectType,
        canvas_width: 1920,
        canvas_height: 1080,
      });

      toast({
        title: 'Success',
        description: 'Project created successfully',
      });

      router.push(`/editor?project=${project.id}`);
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to create project',
        variant: 'destructive',
      });
    }
  };

  const getProjectIcon = (type: string) => {
    switch (type) {
      case 'ui_ux':
        return <Layout className="h-8 w-8" />;
      case 'graphic':
        return <FileImage className="h-8 w-8" />;
      case 'logo':
        return <Palette className="h-8 w-8" />;
      default:
        return <FileImage className="h-8 w-8" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <DashboardSidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <MainHeader />

        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
          {/* Header Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Projects</h1>
            <p className="text-gray-600">Manage and organize all your design projects</p>
          </div>

          {/* Controls Section */}
          <div className="mb-8 flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <Input
                placeholder="Search projects..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Sort Dropdown */}
            <div className="flex gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'recent' | 'name' | 'oldest')}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 bg-white"
              >
                <option value="recent">Most Recent</option>
                <option value="oldest">Oldest</option>
                <option value="name">Name (A-Z)</option>
              </select>

              {/* Create Button */}
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </div>
          </div>

          {/* Projects Grid */}
          <ErrorBoundary>
          {loading ? (
            <ProjectGridSkeleton count={8} />
          ) : error ? (
            <InlineError message={error} onRetry={loadProjectsData} />
          ) : filteredProjects.length === 0 ? (
            <Card>
              <CardContent className="text-center py-16">
                <FileImage className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 text-lg mb-4">
                  {searchTerm ? 'No projects found matching your search' : 'No projects yet'}
                </p>
                {!searchTerm && (
                  <Button
                    className="bg-blue-600 hover:bg-blue-700"
                    onClick={() => createNewProject('ui_ux')}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Project
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredProjects.map((project) => (
                <Card
                  key={project.id}
                  className="hover:shadow-lg transition-shadow cursor-pointer hover:border-blue-200"
                  onClick={() => router.push(`/editor?project=${project.id}`)}
                >
                  <CardHeader>
                    <div className="aspect-video bg-gray-100 rounded flex items-center justify-center mb-2">
                      {getProjectIcon(project.project_type)}
                    </div>
                    <CardTitle className="text-base truncate">{project.name}</CardTitle>
                    <CardDescription className="text-sm">
                      {project.project_type === 'ui_ux' ? 'UI/UX Design' :
                       project.project_type === 'graphic' ? 'Graphic Design' : 'Logo Design'}
                    </CardDescription>
                  </CardHeader>
                  <CardFooter className="text-xs text-gray-500">
                    {new Date(project.updated_at).toLocaleDateString()}
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
