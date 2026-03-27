"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Database,
  Plus,
  Search,
  Link2,
  RefreshCw,
  Table,
  Sheet,
  Cloud,
  FileJson,
  ArrowRight,
  CircleDot,
  CheckCircle,
  AlertCircle,
  Settings2,
  Edit2,
  Trash2,
  Eye,
  Plug,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';

// Types
interface DataSource {
  id: number;
  name: string;
  type: 'api' | 'spreadsheet' | 'database' | 'json';
  icon: React.ElementType;
  status: 'connected' | 'disconnected' | 'error';
  lastSync: string;
  records: number;
  fields: string[];
}

interface DataBinding {
  id: number;
  element: string;
  property: string;
  source: string;
  field: string;
  transform?: string;
}

// Mock Data
const mockSources: DataSource[] = [
  { id: 1, name: 'Products API', type: 'api', icon: Cloud, status: 'connected', lastSync: '2 min ago', records: 156, fields: ['id', 'name', 'price', 'image', 'category', 'stock'] },
  { id: 2, name: 'Users Spreadsheet', type: 'spreadsheet', icon: Sheet, status: 'connected', lastSync: '15 min ago', records: 1243, fields: ['email', 'name', 'avatar', 'role', 'joined'] },
  { id: 3, name: 'Analytics DB', type: 'database', icon: Database, status: 'connected', lastSync: '1 hour ago', records: 50000, fields: ['page', 'views', 'sessions', 'bounce_rate'] },
  { id: 4, name: 'Config JSON', type: 'json', icon: FileJson, status: 'disconnected', lastSync: '3 days ago', records: 15, fields: ['theme', 'logo', 'colors', 'fonts'] },
];

const mockBindings: DataBinding[] = [
  { id: 1, element: 'Product Card Title', property: 'Text Content', source: 'Products API', field: 'name' },
  { id: 2, element: 'Product Card Price', property: 'Text Content', source: 'Products API', field: 'price', transform: 'currency' },
  { id: 3, element: 'Product Card Image', property: 'Image Source', source: 'Products API', field: 'image' },
  { id: 4, element: 'User Avatar', property: 'Image Source', source: 'Users Spreadsheet', field: 'avatar' },
  { id: 5, element: 'User Name', property: 'Text Content', source: 'Users Spreadsheet', field: 'name' },
  { id: 6, element: 'Stats Card', property: 'Text Content', source: 'Analytics DB', field: 'views', transform: 'thousands' },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'connected': return 'bg-green-100 text-green-700 border-green-200';
    case 'disconnected': return 'bg-gray-100 text-gray-700 border-gray-200';
    case 'error': return 'bg-red-100 text-red-700 border-red-200';
    default: return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

const _getStatusIcon = (status: string) => {
  switch (status) {
    case 'connected': return <CheckCircle className="h-4 w-4 text-green-500" />;
    case 'disconnected': return <CircleDot className="h-4 w-4 text-gray-400" />;
    case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />;
    default: return <CircleDot className="h-4 w-4 text-gray-400" />;
  }
};

// Data Source Card
function DataSourceCard({ source, onConnect, onEdit }: { source: DataSource; onConnect: () => void; onEdit: () => void }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-lg ${source.status === 'connected' ? 'bg-blue-100' : 'bg-gray-100'}`}>
            <source.icon className={`h-6 w-6 ${source.status === 'connected' ? 'text-blue-600' : 'text-gray-400'}`} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-gray-900 truncate">{source.name}</h4>
              <Badge variant="outline" className={getStatusColor(source.status)}>{source.status}</Badge>
            </div>
            <p className="text-sm text-gray-500">{source.records.toLocaleString()} records • {source.fields.length} fields</p>
            <p className="text-xs text-gray-400 mt-1">Last synced {source.lastSync}</p>
          </div>
          <div className="flex gap-1">
            {source.status === 'connected' ? (
              <Button size="sm" variant="ghost"><RefreshCw className="h-4 w-4" /></Button>
            ) : (
              <Button size="sm" variant="outline" onClick={onConnect}><Plug className="h-4 w-4 mr-1" />Connect</Button>
            )}
            <Button size="sm" variant="ghost" onClick={onEdit}><Settings2 className="h-4 w-4" /></Button>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-xs font-medium text-gray-500 mb-2">Available Fields</p>
          <div className="flex flex-wrap gap-1">
            {source.fields.slice(0, 4).map(field => (
              <Badge key={field} variant="outline" className="text-xs font-mono">{field}</Badge>
            ))}
            {source.fields.length > 4 && (
              <Badge variant="outline" className="text-xs">+{source.fields.length - 4} more</Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Binding Row
function BindingRow({ binding, onEdit, onDelete }: { binding: DataBinding; onEdit: () => void; onDelete: () => void }) {
  return (
    <div className="flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-200 group hover:shadow-sm transition-shadow">
      <div className="flex-1 flex items-center gap-3">
        <div className="p-2 bg-purple-100 rounded-lg">
          <Link2 className="h-4 w-4 text-purple-600" />
        </div>
        <div>
          <p className="font-medium text-gray-900">{binding.element}</p>
          <p className="text-sm text-gray-500">{binding.property}</p>
        </div>
      </div>
      <ArrowRight className="h-4 w-4 text-gray-400" />
      <div className="flex-1">
        <p className="font-medium text-blue-600">{binding.source}</p>
        <div className="flex items-center gap-2">
          <code className="text-sm bg-gray-100 px-2 py-0.5 rounded">{binding.field}</code>
          {binding.transform && <Badge variant="outline" className="text-xs">{binding.transform}</Badge>}
        </div>
      </div>
      <div className="opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity">
        <Button size="sm" variant="ghost" onClick={onEdit}><Edit2 className="h-4 w-4" /></Button>
        <Button size="sm" variant="ghost" className="text-red-600" onClick={onDelete}><Trash2 className="h-4 w-4" /></Button>
      </div>
    </div>
  );
}

export default function DataBindingPage() {
  const { toast } = useToast();
  const [sources] = useState<DataSource[]>(mockSources);
  const [bindings] = useState<DataBinding[]>(mockBindings);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddSource, setShowAddSource] = useState(false);
  const [showAddBinding, setShowAddBinding] = useState(false);

  const connectedCount = sources.filter(s => s.status === 'connected').length;

  const handleAddSource = () => {
    setShowAddSource(false);
    toast({ title: 'Data Source Added', description: 'New data source has been connected' });
  };

  const handleAddBinding = () => {
    setShowAddBinding(false);
    toast({ title: 'Binding Created', description: 'Element has been bound to data field' });
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-hidden p-6">
          <div className="max-w-7xl mx-auto h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                  <Database className="h-7 w-7 text-blue-600" />Data Binding
                </h1>
                <p className="text-gray-500">Connect designs to dynamic data sources</p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setShowAddSource(true)}><Plus className="h-4 w-4 mr-2" />Add Data Source</Button>
                <Button onClick={() => setShowAddBinding(true)}><Link2 className="h-4 w-4 mr-2" />Create Binding</Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg"><Database className="h-5 w-5 text-blue-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Data Sources</p>
                    <p className="text-2xl font-bold text-gray-900">{sources.length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-green-100 rounded-lg"><CheckCircle className="h-5 w-5 text-green-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Connected</p>
                    <p className="text-2xl font-bold text-green-600">{connectedCount}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-purple-100 rounded-lg"><Link2 className="h-5 w-5 text-purple-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Active Bindings</p>
                    <p className="text-2xl font-bold text-gray-900">{bindings.length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-amber-100 rounded-lg"><Table className="h-5 w-5 text-amber-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Total Records</p>
                    <p className="text-2xl font-bold text-gray-900">51K</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content */}
            <Tabs defaultValue="sources" className="flex-1 flex flex-col overflow-hidden">
              <TabsList className="w-fit mb-4">
                <TabsTrigger value="sources">Data Sources ({sources.length})</TabsTrigger>
                <TabsTrigger value="bindings">Bindings ({bindings.length})</TabsTrigger>
                <TabsTrigger value="preview">Live Preview</TabsTrigger>
              </TabsList>

              <TabsContent value="sources" className="flex-1 overflow-hidden mt-0">
                <ScrollArea className="h-full">
                  <div className="grid grid-cols-2 gap-4 pr-4">
                    {sources.map(source => (
                      <DataSourceCard key={source.id} source={source} onConnect={() => toast({ title: 'Connecting...' })} onEdit={() => {}} />
                    ))}
                    <Card className="border-dashed cursor-pointer hover:border-blue-400 transition-colors" onClick={() => setShowAddSource(true)}>
                      <CardContent className="p-8 flex flex-col items-center justify-center text-center">
                        <Plus className="h-8 w-8 text-gray-400 mb-2" />
                        <p className="font-medium text-gray-600">Add Data Source</p>
                        <p className="text-sm text-gray-400">Connect API, database, or file</p>
                      </CardContent>
                    </Card>
                  </div>
                </ScrollArea>
              </TabsContent>

              <TabsContent value="bindings" className="flex-1 overflow-hidden mt-0">
                <div className="mb-4">
                  <div className="relative max-w-md">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input placeholder="Search bindings..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-10" />
                  </div>
                </div>
                <ScrollArea className="flex-1">
                  <div className="space-y-3 pr-4">
                    {bindings.filter(b => b.element.toLowerCase().includes(searchQuery.toLowerCase())).map(binding => (
                      <BindingRow key={binding.id} binding={binding} onEdit={() => {}} onDelete={() => toast({ title: 'Binding Removed' })} />
                    ))}
                  </div>
                </ScrollArea>
              </TabsContent>

              <TabsContent value="preview" className="flex-1 overflow-hidden mt-0">
                <div className="h-full flex items-center justify-center bg-white rounded-lg border border-gray-200">
                  <div className="text-center">
                    <Eye className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="font-semibold text-gray-900 mb-2">Live Preview</h3>
                    <p className="text-gray-500 mb-4">See your data bindings in action</p>
                    <Button><RefreshCw className="h-4 w-4 mr-2" />Refresh Data</Button>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      {/* Add Data Source Dialog */}
      <Dialog open={showAddSource} onOpenChange={setShowAddSource}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add Data Source</DialogTitle>
            <DialogDescription>Connect a new data source to your project</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-3">
              {[{ icon: Cloud, label: 'REST API' }, { icon: Sheet, label: 'Spreadsheet' }, { icon: Database, label: 'Database' }, { icon: FileJson, label: 'JSON File' }].map(type => (
                <button key={type.label} className="p-4 rounded-lg border-2 border-gray-200 hover:border-blue-500 transition-colors text-center">
                  <type.icon className="h-8 w-8 text-gray-600 mx-auto mb-2" />
                  <span className="text-sm font-medium">{type.label}</span>
                </button>
              ))}
            </div>
            <div>
              <Label>Source Name</Label>
              <Input placeholder="e.g., Products API" className="mt-1" />
            </div>
            <div>
              <Label>URL / Connection String</Label>
              <Input placeholder="https://api.example.com/data" className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddSource(false)}>Cancel</Button>
            <Button onClick={handleAddSource}>Connect Source</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Binding Dialog */}
      <Dialog open={showAddBinding} onOpenChange={setShowAddBinding}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Create Data Binding</DialogTitle>
            <DialogDescription>Link a design element to a data field</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Design Element</Label>
              <Select>
                <SelectTrigger className="mt-1"><SelectValue placeholder="Select element" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="title">Product Card Title</SelectItem>
                  <SelectItem value="price">Product Card Price</SelectItem>
                  <SelectItem value="image">Product Card Image</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Property</Label>
              <Select>
                <SelectTrigger className="mt-1"><SelectValue placeholder="Select property" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="text">Text Content</SelectItem>
                  <SelectItem value="src">Image Source</SelectItem>
                  <SelectItem value="href">Link URL</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Data Source</Label>
              <Select>
                <SelectTrigger className="mt-1"><SelectValue placeholder="Select source" /></SelectTrigger>
                <SelectContent>
                  {sources.filter(s => s.status === 'connected').map(s => (
                    <SelectItem key={s.id} value={s.name}>{s.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Field</Label>
              <Select>
                <SelectTrigger className="mt-1"><SelectValue placeholder="Select field" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="name">name</SelectItem>
                  <SelectItem value="price">price</SelectItem>
                  <SelectItem value="image">image</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddBinding(false)}>Cancel</Button>
            <Button onClick={handleAddBinding}>Create Binding</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
