'use client';

import React, { useState, useCallback } from 'react';
import {
  ChevronDown,
  ChevronRight,
  Plus,
  Settings,
  Play,
  Copy,
  Trash2,
  Move,
  MousePointer,
  Layers,
  Eye,
  EyeOff
} from 'lucide-react';

interface ComponentState {
  id: string;
  name: string;
  isDefault: boolean;
  properties: Record<string, unknown>;
}

interface Interaction {
  id: string;
  trigger: string;
  action: string;
  targetState?: string;
}

interface InteractiveComponent {
  id: string;
  name: string;
  type: string;
  states: ComponentState[];
  interactions: Interaction[];
  variables: Record<string, unknown>;
}

interface InteractiveComponentsProps {
  onComponentCreate?: (component: InteractiveComponent) => void;
  onPreview?: (componentId: string) => void;
}

const COMPONENT_TYPES = [
  { type: 'dropdown', label: 'Dropdown Menu', icon: ChevronDown },
  { type: 'carousel', label: 'Carousel', icon: Layers },
  { type: 'accordion', label: 'Accordion', icon: ChevronRight },
  { type: 'tabs', label: 'Tab Bar', icon: Layers },
  { type: 'modal', label: 'Modal Dialog', icon: Layers },
  { type: 'tooltip', label: 'Tooltip', icon: MousePointer },
  { type: 'toggle', label: 'Toggle Switch', icon: Settings },
  { type: 'slider', label: 'Slider', icon: Move },
];

const TRIGGERS = [
  { value: 'click', label: 'On Click' },
  { value: 'hover', label: 'On Hover' },
  { value: 'focus', label: 'On Focus' },
  { value: 'mouseEnter', label: 'Mouse Enter' },
  { value: 'mouseLeave', label: 'Mouse Leave' },
  { value: 'swipeLeft', label: 'Swipe Left' },
  { value: 'swipeRight', label: 'Swipe Right' },
  { value: 'keypress', label: 'Key Press' },
  { value: 'timer', label: 'After Delay' },
];

const ACTIONS = [
  { value: 'changeState', label: 'Change State' },
  { value: 'nextState', label: 'Next State' },
  { value: 'prevState', label: 'Previous State' },
  { value: 'toggleState', label: 'Toggle State' },
  { value: 'setVariable', label: 'Set Variable' },
  { value: 'openOverlay', label: 'Open Overlay' },
  { value: 'closeOverlay', label: 'Close Overlay' },
  { value: 'navigate', label: 'Navigate To' },
  { value: 'scrollTo', label: 'Scroll To' },
];

export function InteractiveComponents({ onComponentCreate, onPreview }: InteractiveComponentsProps) {
  const [components, setComponents] = useState<InteractiveComponent[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<InteractiveComponent | null>(null);
  const [activeTab, setActiveTab] = useState<'states' | 'interactions' | 'variables'>('states');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newComponentType, setNewComponentType] = useState('dropdown');
  const [newComponentName, setNewComponentName] = useState('');

  const handleCreateComponent = useCallback(() => {
    if (!newComponentName) return;

    const defaultStates: ComponentState[] = [];
    
    // Create default states based on component type
    switch (newComponentType) {
      case 'dropdown':
        defaultStates.push(
          { id: 'closed', name: 'Closed', isDefault: true, properties: { isOpen: false } },
          { id: 'open', name: 'Open', isDefault: false, properties: { isOpen: true } }
        );
        break;
      case 'carousel':
        defaultStates.push(
          { id: 'slide1', name: 'Slide 1', isDefault: true, properties: { activeSlide: 0 } },
          { id: 'slide2', name: 'Slide 2', isDefault: false, properties: { activeSlide: 1 } },
          { id: 'slide3', name: 'Slide 3', isDefault: false, properties: { activeSlide: 2 } }
        );
        break;
      case 'accordion':
        defaultStates.push(
          { id: 'collapsed', name: 'Collapsed', isDefault: true, properties: { expanded: false } },
          { id: 'expanded', name: 'Expanded', isDefault: false, properties: { expanded: true } }
        );
        break;
      case 'toggle':
        defaultStates.push(
          { id: 'off', name: 'Off', isDefault: true, properties: { checked: false } },
          { id: 'on', name: 'On', isDefault: false, properties: { checked: true } }
        );
        break;
      default:
        defaultStates.push(
          { id: 'default', name: 'Default', isDefault: true, properties: {} }
        );
    }

    const newComponent: InteractiveComponent = {
      id: `component_${Date.now()}`,
      name: newComponentName,
      type: newComponentType,
      states: defaultStates,
      interactions: [],
      variables: {}
    };

    setComponents([...components, newComponent]);
    setSelectedComponent(newComponent);
    setShowCreateModal(false);
    setNewComponentName('');
    onComponentCreate?.(newComponent);
  }, [newComponentName, newComponentType, components, onComponentCreate]);

  const addState = useCallback(() => {
    if (!selectedComponent) return;

    const newState: ComponentState = {
      id: `state_${Date.now()}`,
      name: `State ${selectedComponent.states.length + 1}`,
      isDefault: false,
      properties: {}
    };

    const updated = {
      ...selectedComponent,
      states: [...selectedComponent.states, newState]
    };

    setSelectedComponent(updated);
    setComponents(components.map(c => c.id === updated.id ? updated : c));
  }, [selectedComponent, components]);

  const addInteraction = useCallback(() => {
    if (!selectedComponent) return;

    const newInteraction: Interaction = {
      id: `interaction_${Date.now()}`,
      trigger: 'click',
      action: 'changeState',
      targetState: selectedComponent.states[0]?.id
    };

    const updated = {
      ...selectedComponent,
      interactions: [...selectedComponent.interactions, newInteraction]
    };

    setSelectedComponent(updated);
    setComponents(components.map(c => c.id === updated.id ? updated : c));
  }, [selectedComponent, components]);

  const updateInteraction = useCallback((interactionId: string, field: string, value: string) => {
    if (!selectedComponent) return;

    const updated = {
      ...selectedComponent,
      interactions: selectedComponent.interactions.map(i => 
        i.id === interactionId ? { ...i, [field]: value } : i
      )
    };

    setSelectedComponent(updated);
    setComponents(components.map(c => c.id === updated.id ? updated : c));
  }, [selectedComponent, components]);

  return (
    <div className="flex h-full bg-white dark:bg-gray-800">
      {/* Component List */}
      <div className="w-64 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Interactive Components</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4" />
            New Component
          </button>
        </div>

        <div className="flex-1 overflow-auto p-2">
          {components.length === 0 ? (
            <div className="text-center text-gray-500 dark:text-gray-400 py-8">
              <Layers className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No interactive components yet</p>
            </div>
          ) : (
            <div className="space-y-1">
              {components.map(component => (
                <button
                  key={component.id}
                  onClick={() => setSelectedComponent(component)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedComponent?.id === component.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                    <span className="font-medium text-gray-900 dark:text-white">{component.name}</span>
                  </div>
                  <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {component.type} • {component.states.length} states
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Component Editor */}
      <div className="flex-1 flex flex-col">
        {selectedComponent ? (
          <>
            {/* Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {selectedComponent.name}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {selectedComponent.type.charAt(0).toUpperCase() + selectedComponent.type.slice(1)}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onPreview?.(selectedComponent.id)}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  <Play className="w-4 h-4" />
                  Preview
                </button>
                <button className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                  <Copy className="w-4 h-4" />
                </button>
                <button className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700">
              {['states', 'interactions', 'variables'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab as 'variables' | 'states' | 'interactions')}
                  className={`px-6 py-3 text-sm font-medium capitalize transition-colors ${
                    activeTab === tab
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto p-4">
              {activeTab === 'states' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900 dark:text-white">Component States</h4>
                    <button
                      onClick={addState}
                      className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                    >
                      <Plus className="w-4 h-4" />
                      Add State
                    </button>
                  </div>
                  
                  <div className="grid gap-3">
                    {selectedComponent.states.map((state, index) => (
                      <div
                        key={state.id}
                        className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <input
                              type="text"
                              value={state.name}
                              className="font-medium bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-1 text-gray-900 dark:text-white"
                            />
                            {state.isDefault && (
                              <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded">
                                Default
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-1">
                            <button className="p-1 text-gray-400 hover:text-gray-600">
                              <Eye className="w-4 h-4" />
                            </button>
                            {!state.isDefault && (
                              <button className="p-1 text-red-400 hover:text-red-600">
                                <Trash2 className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </div>
                        <div className="text-sm text-gray-500">
                          Properties: {JSON.stringify(state.properties)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'interactions' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900 dark:text-white">Interactions</h4>
                    <button
                      onClick={addInteraction}
                      className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                    >
                      <Plus className="w-4 h-4" />
                      Add Interaction
                    </button>
                  </div>

                  {selectedComponent.interactions.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <MousePointer className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>No interactions defined</p>
                      <p className="text-sm">Add interactions to make this component interactive</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {selectedComponent.interactions.map(interaction => (
                        <div
                          key={interaction.id}
                          className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                        >
                          <div className="grid grid-cols-3 gap-4">
                            <div>
                              <label className="block text-xs text-gray-500 mb-1">Trigger</label>
                              <select
                                value={interaction.trigger}
                                onChange={(e) => updateInteraction(interaction.id, 'trigger', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                              >
                                {TRIGGERS.map(t => (
                                  <option key={t.value} value={t.value}>{t.label}</option>
                                ))}
                              </select>
                            </div>
                            <div>
                              <label className="block text-xs text-gray-500 mb-1">Action</label>
                              <select
                                value={interaction.action}
                                onChange={(e) => updateInteraction(interaction.id, 'action', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                              >
                                {ACTIONS.map(a => (
                                  <option key={a.value} value={a.value}>{a.label}</option>
                                ))}
                              </select>
                            </div>
                            <div>
                              <label className="block text-xs text-gray-500 mb-1">Target State</label>
                              <select
                                value={interaction.targetState}
                                onChange={(e) => updateInteraction(interaction.id, 'targetState', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                              >
                                {selectedComponent.states.map(s => (
                                  <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                              </select>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'variables' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900 dark:text-white">Variables</h4>
                    <button className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700">
                      <Plus className="w-4 h-4" />
                      Add Variable
                    </button>
                  </div>
                  <div className="text-center py-8 text-gray-500">
                    <Settings className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No variables defined</p>
                    <p className="text-sm">Variables can be used to store and share state</p>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <Layers className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">Select or create a component</p>
              <p className="text-sm">Create interactive components with states and behaviors</p>
            </div>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Create Interactive Component
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Component Name
                </label>
                <input
                  type="text"
                  value={newComponentName}
                  onChange={(e) => setNewComponentName(e.target.value)}
                  placeholder="Enter component name..."
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Component Type
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {COMPONENT_TYPES.map(type => (
                    <button
                      key={type.type}
                      onClick={() => setNewComponentType(type.type)}
                      className={`flex items-center gap-2 p-3 rounded-lg border transition-colors ${
                        newComponentType === type.type
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <type.icon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                      <span className="text-sm text-gray-900 dark:text-white">{type.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateComponent}
                disabled={!newComponentName}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Create Component
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default InteractiveComponents;
