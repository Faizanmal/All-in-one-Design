/**
 * Central export file for all hooks
 * Import hooks from specific files or use this index for convenience
 * 
 * Note: Some hooks may have duplicate names across files.
 * Import directly from specific files to avoid conflicts:
 * import { use3DModels } from '@/hooks/use3DStudio';
 */

// 3D Studio hooks
export * from './use3DStudio';

// Animation hooks
export * from './useAnimations';

// Design Systems hooks
export * from './useDesignSystems';

// Optimization hooks
export * from './useOptimization';

// Whitelabel & Agency hooks
export * from './useWhitelabel';

// Font Assets hooks
export * from './useFontAssets';

// Plugin hooks
export * from './usePlugins';

// Advanced Feature hooks (Auto-layout, Component Variants, etc.)
export * from './use-advanced-features';

// Feature hooks (Phase 4 features: Code Export, Slack/Teams, etc.)
export * from './useFeatureHooks';

// Note: use-features and use-new-features have conflicting exports
// Import them directly when needed:
// import { ... } from '@/hooks/use-features';
// import { ... } from '@/hooks/use-new-features';

// Accessibility Testing hooks
export * from './useAccessibilityTesting';

// Commenting hooks
export * from './useCommenting';

// Data Binding hooks
export * from './useDataBinding';

// Design Analytics hooks
export * from './useDesignAnalytics';

// Interactive Components hooks
export * from './useInteractiveComponents';

// Media Assets hooks
export * from './useMediaAssets';

// PDF Annotation hooks
export * from './usePDFAnnotation';

// Smart Tools hooks
export * from './useSmartTools';

// Vector Editing hooks
export * from './useVectorEditing';

// Collaborative Canvas hooks
export * from './useCollaborativeCanvas';

// Mobile hooks
export * from './use-mobile';

// API hooks
export * from './use-api';

// Utility hooks
export * from './useDebounce';
export * from './use-toast';
