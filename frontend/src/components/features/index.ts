// Export barrel file for all new feature components

// Feature 18: Code Export & Developer Handoff
export { 
  CodeExportPanel, 
  DesignSpecPanel, 
  DeveloperHandoff 
} from './code-export/CodeExportPanel';

// Feature 19: Slack/Teams Integration
export { 
  SlackIntegration, 
  TeamsIntegration, 
  NotificationPreferences, 
  ShareToChannelDialog,
  IntegrationSettings 
} from './slack-teams/IntegrationSettings';

// Feature 20: Offline Mode & PWA
export { 
  OfflineStatusBadge, 
  OfflineProjectsManager, 
  SyncQueue, 
  PWAInstallPrompt,
  OfflineSettings 
} from './offline-pwa/OfflineSettings';

// Feature 21: Asset Management Enhanced
export { 
  AssetManager, 
  AssetCard, 
  AIAssetSearch, 
  SmartFolderDialog 
} from './asset-management/AssetManager';

// Feature 22: Template Marketplace
export { 
  TemplateMarketplace, 
  TemplateCard, 
  TemplateDetailModal, 
  CategoryFilter 
} from './template-marketplace/TemplateMarketplace';

// Feature 23: Time Tracking & Project Management
export { 
  TimeTrackingDashboard, 
  ActiveTimer, 
  TimeEntryList, 
  TaskBoard, 
  WeeklyGoalProgress, 
  InvoiceBuilder 
} from './time-tracking/TimeTrackingDashboard';

// Feature 24: PDF Export with Bleed
export { 
  PDFExportDialog, 
  BleedSettings, 
  PrintMarksSettings, 
  ColorModeSettings, 
  PreflightCheck, 
  SpreadView 
} from './pdf-export/PDFExportDialog';

// Feature 25: Granular Permissions & Roles
export { 
  PermissionsDashboard, 
  RoleManager, 
  RoleBadge, 
  PermissionMatrix, 
  ShareLinkManager, 
  BranchProtectionSettings, 
  AccessLogs 
} from './granular-permissions/PermissionsDashboard';

// Re-export all feature components for easy consumption
export * from './code-export/CodeExportPanel';
export * from './slack-teams/IntegrationSettings';
export * from './offline-pwa/OfflineSettings';
export * from './asset-management/AssetManager';
export * from './template-marketplace/TemplateMarketplace';
export * from './time-tracking/TimeTrackingDashboard';
export * from './pdf-export/PDFExportDialog';
export * from './granular-permissions/PermissionsDashboard';
