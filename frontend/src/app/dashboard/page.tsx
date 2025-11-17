"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { projectsAPI, type Project } from '@/lib/design-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, FileImage, Layout, Palette } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    const loadProjectsData = async () => {
      try {
        setLoading(true);
        const data = await projectsAPI.myProjects();
        setProjects(data);
      } catch {
        toast({
          title: 'Error',
          description: 'Failed to load projects',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };
    
    loadProjectsData();
  }, [toast]);

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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">AI Design Tool</h1>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => router.push('/templates')}>
                Templates
              </Button>
              <Button variant="outline" onClick={() => router.push('/settings')}>
                Settings
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
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

        {/* Recent Projects */}
        <section>
          <h2 className="text-xl font-semibold mb-4">Recent Projects</h2>
          
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader>
                    <div className="h-32 bg-gray-200 rounded"></div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : projects.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <FileImage className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No projects yet. Create your first project above!</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {projects.map((project) => (
                <Card
                  key={project.id}
                  className="hover:shadow-lg transition-shadow cursor-pointer"
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
                    Updated {new Date(project.updated_at).toLocaleDateString()}
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
