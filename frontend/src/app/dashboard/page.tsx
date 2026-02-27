"use client";

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { projectsAPI, type Project } from '@/lib/design-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, FileImage, Layout, Palette, Sparkles, Wand2, Heart, Archive, Clock, RefreshCw } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { ErrorBoundary, InlineError } from '@/components/error-boundary';
import { ProjectGridSkeleton } from '@/components/loading-skeletons';

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [favorites, setFavorites] = useState<number[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const filter = searchParams.get('filter') || 'all';
  const newProjectType = searchParams.get('newProject') as 'graphic' | 'ui_ux' | 'logo' | null;
  const { toast } = useToast();

  const loadProjectsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectsAPI.myProjects();
      setProjects(data);
      
      // Load favorites from localStorage
      const savedFavorites = localStorage.getItem('favoriteProjects');
      if (savedFavorites) {
        setFavorites(JSON.parse(savedFavorites));
      }
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

  // Handle auto-creation of new project from query param
  useEffect(() => {
    if (newProjectType) {
      createNewProject(newProjectType);
      // Clear the query param
      router.replace('/dashboard');
    }
  }, [newProjectType]);

  // Filter projects based on the filter parameter
  useEffect(() => {
    let filtered = [...projects];

    switch (filter) {
      case 'recent':
        filtered.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
        break;
      case 'favorites':
        filtered = filtered.filter((p) => favorites.includes(p.id));
        break;
      case 'archived':
        // Filter for archived projects (if your API has an archived field)
        filtered = filtered.filter((p) => (p as any).is_archived === true);
        break;
      default:
        // Show all projects
        break;
    }

    setFilteredProjects(filtered);
  }, [projects, filter, favorites]);

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

  const toggleFavorite = (projectId: number) => {
    const newFavorites = favorites.includes(projectId)
      ? favorites.filter((id) => id !== projectId)
      : [...favorites, projectId];
    setFavorites(newFavorites);
    localStorage.setItem('favoriteProjects', JSON.stringify(newFavorites));
  };

  const getFilterTitle = () => {
    switch (filter) {
      case 'recent':
        return 'Recent Projects';
      case 'favorites':
        return 'Favorite Projects';
      case 'archived':
        return 'Archived Projects';
      default:
        return 'Recent Projects';
    }
  };

  const getFilterIcon = () => {
    switch (filter) {
      case 'recent':
        return <Clock className="h-5 w-5" />;
      case 'favorites':
        return <Heart className="h-5 w-5" />;
      case 'archived':
        return <Archive className="h-5 w-5" />;
      default:
        return <FileImage className="h-5 w-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex">
      {/* Sidebar */}
      <DashboardSidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <MainHeader />

        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <ErrorBoundary compact>
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4 dark:text-white">Create New Project</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => createNewProject('ui_ux')}>
              <CardHeader>
                <Layout className="h-10 w-10 text-blue-600 mb-2" />
                <CardTitle>UI/UX Design</CardTitle>
                <CardDescription>
                  Create modern app interfaces and web designs
                </CardDescription>
              </CardHeader>
              <CardFooter>
                <Button className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Create UI/UX Project
                </Button>
              </CardFooter>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => createNewProject('graphic')}>
              <CardHeader>
                <FileImage className="h-10 w-10 text-green-600 mb-2" />
                <CardTitle>Graphic Design</CardTitle>
                <CardDescription>
                  Design social media posts, posters, and more
                </CardDescription>
              </CardHeader>
              <CardFooter>
                <Button className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Graphic Design
                </Button>
              </CardFooter>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => createNewProject('logo')}>
              <CardHeader>
                <Palette className="h-10 w-10 text-purple-600 mb-2" />
                <CardTitle>Logo Design</CardTitle>
                <CardDescription>
                  Generate professional logos with AI
                </CardDescription>
              </CardHeader>
              <CardFooter>
                <Button className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Logo
                </Button>
              </CardFooter>
            </Card>
          </div>
        </section>
        </ErrorBoundary>

        {/* Design Workspaces */}
        <ErrorBoundary compact>
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4 dark:text-white">Design Workspaces</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/design-hub">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 hover:border-blue-500">
                <CardHeader>
                  <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-linear-to-br from-blue-500 to-purple-600 mb-3">
                    <Layout className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle>Design Hub</CardTitle>
                  <CardDescription>
                    Main dashboard to manage all your designs and projects
                  </CardDescription>
                </CardHeader>
              </Card>
            </Link>

            <Link href="/ai-logo-designer">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 hover:border-pink-500">
                <CardHeader>
                  <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-linear-to-br from-pink-500 to-rose-600 mb-3">
                    <Wand2 className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle>AI Logo Designer</CardTitle>
                  <CardDescription>
                    Create professional logos with AI-powered generation
                  </CardDescription>
                </CardHeader>
              </Card>
            </Link>

            <Link href="/ai-uiux-generator">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 hover:border-cyan-500">
                <CardHeader>
                  <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-linear-to-br from-cyan-500 to-blue-600 mb-3">
                    <Sparkles className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle>AI UI/UX Generator</CardTitle>
                  <CardDescription>
                    Generate complete UI/UX designs from text descriptions
                  </CardDescription>
                </CardHeader>
              </Card>
            </Link>
          </div>
        </section>
        </ErrorBoundary>

        {/* Recent Projects */}
        <ErrorBoundary>
        <section>
          <div className="flex items-center gap-2 mb-4">
            {getFilterIcon()}
            <h2 className="text-xl font-semibold">{getFilterTitle()}</h2>
          </div>
          
          {loading ? (
            <ProjectGridSkeleton count={4} />
          ) : error ? (
            <InlineError message={error} onRetry={loadProjectsData} />
          ) : filteredProjects.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <FileImage className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">
                  {filter === 'favorites'
                    ? 'No favorite projects yet. Star your favorite projects to see them here!'
                    : filter === 'archived'
                    ? 'No archived projects'
                    : 'No projects yet. Create your first project above!'}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredProjects.map((project) => (
                <Card
                  key={project.id}
                  className="hover:shadow-lg transition-shadow cursor-pointer group"
                  onClick={() => router.push(`/editor?project=${project.id}`)}
                >
                  <CardHeader>
                    <div className="aspect-video bg-gray-100 rounded flex items-center justify-center mb-2 group-hover:bg-gray-150">
                      {getProjectIcon(project.project_type)}
                    </div>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-base truncate">{project.name}</CardTitle>
                        <CardDescription className="text-sm">
                          {project.project_type === 'ui_ux' ? 'UI/UX Design' :
                           project.project_type === 'graphic' ? 'Graphic Design' : 'Logo Design'}
                        </CardDescription>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleFavorite(project.id);
                        }}
                        className="flex-shrink-0 mt-1"
                      >
                        <Heart
                          className={`h-5 w-5 transition-colors ${
                            favorites.includes(project.id)
                              ? 'fill-red-500 text-red-500'
                              : 'text-gray-400 hover:text-red-500'
                          }`}
                        />
                      </button>
                    </div>
                  </CardHeader>
                  <CardFooter className="text-xs text-gray-500">
                    Updated {new Date(project.updated_at).toLocaleDateString()}
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </section>
        </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
