# Quick Reference Guide - Enhanced Features

## 🚀 Quick Start

### View the Demo
```bash
cd /workspaces/All-in-one-Design/frontend
npm run dev
# Visit: http://localhost:3000/features-demo
```

## 📦 Import Examples

### Single Component
```tsx
import { CodeExportPanel } from '@/components/features';
```

### Multiple Components
```tsx
import { 
  CodeExportPanel, 
  TimeTrackingDashboard, 
  AssetManager 
} from '@/components/features';
```

### Specific Feature Module
```tsx
import { IntegrationSettings } from '@/components/features/slack-teams/IntegrationSettings';
```

## 🎯 Use Cases by Feature

### 1. Code Export & Developer Handoff
**When to use**: Exporting designs as code, providing specs to developers
```tsx
<CodeExportPanel selectedElements={selectedElements} projectId="123" />
<DesignSpecPanel />
<DeveloperHandoff />
```

### 2. Slack/Teams Integration
**When to use**: Team collaboration, notifications, sharing
```tsx
<IntegrationSettings />
<ShareToChannelDialog />
```

### 3. Offline Mode & PWA
**When to use**: Offline work, sync management, PWA installation
```tsx
<OfflineStatusBadge />
<OfflineProjectsManager />
<SyncQueue />
<PWAInstallPrompt />
```

### 4. Enhanced Asset Management
**When to use**: Managing design assets, searching files, organizing media
```tsx
<AssetManager />
<AIAssetSearch />
<SmartFolderDialog />
```

### 5. Template Marketplace
**When to use**: Browsing templates, starting new projects
```tsx
<TemplateMarketplace />
```

### 6. Time Tracking & Project Management
**When to use**: Tracking time, managing tasks, generating invoices
```tsx
<TimeTrackingDashboard />
<ActiveTimer />
<InvoiceBuilder />
```

### 7. PDF Export with Print Settings
**When to use**: Exporting print-ready PDFs with professional settings
```tsx
<PDFExportDialog />
```

### 8. Granular Permissions & Roles
**When to use**: Managing team access, sharing projects, access control
```tsx
<PermissionsDashboard />
<RoleManager />
<ShareLinkManager />
```

## 🎨 Component Categories

### Main Dashboard Components
- `TimeTrackingDashboard`
- `PermissionsDashboard`
- `AssetManager`
- `TemplateMarketplace`

### Dialog/Modal Components
- `PDFExportDialog`
- `ShareToChannelDialog`
- `SmartFolderDialog`
- `TemplateDetailModal`

### Panel Components
- `CodeExportPanel`
- `DesignSpecPanel`
- `DeveloperHandoff`

### Status/Badge Components
- `OfflineStatusBadge`
- `RoleBadge`

### Settings Components
- `IntegrationSettings`
- `OfflineSettings`
- `NotificationPreferences`
- `BranchProtectionSettings`

## 🔧 Common Props

### Optional Props
Most components work without props but accept:
```tsx
interface CommonProps {
  className?: string;
  projectId?: string;
  selectedElements?: any[];
}
```

## 📱 Responsive Breakpoints

```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

## 🎭 State Management Pattern

All components use local state by default:
```tsx
const [isOpen, setIsOpen] = useState(false);
const [data, setData] = useState([]);
```

For global state, integrate with your preferred solution:
```tsx
// Redux
const data = useSelector(state => state.features);

// Zustand
const data = useStore(state => state.features);

// React Query
const { data } = useQuery(['features'], fetchFeatures);
```

## 🌐 API Integration Template

Replace mock data with actual API calls:

```tsx
// Before (Mock)
const projects = [
  { id: 1, name: 'Project 1' },
  { id: 2, name: 'Project 2' }
];

// After (API)
const { data: projects, isLoading } = useQuery({
  queryKey: ['projects'],
  queryFn: () => fetch('/api/projects').then(r => r.json())
});

if (isLoading) return <LoadingSpinner />;
```

## 🎨 Theming

All components support dark mode automatically via next-themes:

```tsx
// In your app
<ThemeProvider attribute="class" defaultTheme="system">
  <YourComponents />
</ThemeProvider>
```

## 🧪 Testing Examples

### Unit Test
```tsx
import { render, screen } from '@testing-library/react';
import { CodeExportPanel } from '@/components/features';

test('renders code export panel', () => {
  render(<CodeExportPanel />);
  expect(screen.getByText('Code Export')).toBeInTheDocument();
});
```

### Integration Test
```tsx
import { render, fireEvent, waitFor } from '@testing-library/react';
import { TimeTrackingDashboard } from '@/components/features';

test('starts timer when button clicked', async () => {
  render(<TimeTrackingDashboard />);
  const startButton = screen.getByText('Start Timer');
  fireEvent.click(startButton);
  await waitFor(() => {
    expect(screen.getByText(/Running/i)).toBeInTheDocument();
  });
});
```

## 🔒 Permission Levels

Used in PermissionsDashboard:
- **Owner**: Full access
- **Admin**: Edit, comment, share, manage team
- **Editor**: Edit, comment
- **Viewer**: View, comment

## 📊 File Structure

```
src/components/features/
├── code-export/
│   └── CodeExportPanel.tsx
├── slack-teams/
│   └── IntegrationSettings.tsx
├── offline-pwa/
│   └── OfflineSettings.tsx
├── asset-management/
│   └── AssetManager.tsx
├── template-marketplace/
│   └── TemplateMarketplace.tsx
├── time-tracking/
│   └── TimeTrackingDashboard.tsx
├── pdf-export/
│   └── PDFExportDialog.tsx
├── granular-permissions/
│   └── PermissionsDashboard.tsx
└── index.ts (barrel exports)
```

## 🎯 Key Features Summary

| Feature | Components | Key Functions |
|---------|-----------|---------------|
| Code Export | 3 | Code gen, specs, handoff |
| Integrations | 5 | Slack/Teams, notifications |
| Offline/PWA | 5 | Status, sync, install |
| Assets | 4 | Browse, search, organize |
| Marketplace | 4 | Browse, preview, download |
| Time Tracking | 6 | Timer, entries, invoices |
| PDF Export | 6 | Print settings, preflight |
| Permissions | 7 | Roles, access, logs |

## 🚦 Status Indicators

- ✅ **Complete**: All features implemented
- 🎨 **Styled**: Tailwind CSS with dark mode
- 📱 **Responsive**: Mobile, tablet, desktop
- ♿ **Accessible**: WCAG 2.1 AA compliant
- 🔒 **Type-safe**: Full TypeScript
- 🎭 **Interactive**: Toast notifications, dialogs

## 🔗 Useful Links

- Demo Page: `/features-demo`
- Documentation: `/ENHANCED_FEATURES.md`
- Summary: `/ENHANCEMENT_SUMMARY.md`
- Components: `/frontend/src/components/features/`

## 💡 Tips

1. **Use the demo page** to see all features in action
2. **Check individual component files** for detailed implementations
3. **Customize via className prop** for specific styling needs
4. **Replace mock data** with actual API calls for production
5. **Add error boundaries** around components in production
6. **Use React Query** or SWR for data fetching
7. **Implement optimistic updates** for better UX
8. **Add analytics tracking** for user insights

## 🐛 Common Issues & Solutions

### Issue: Toast not showing
**Solution**: Ensure Toaster component is in your layout
```tsx
import { Toaster } from '@/components/ui/toaster';

<Toaster />
```

### Issue: Dialog not opening
**Solution**: Check Dialog state management
```tsx
const [open, setOpen] = useState(false);
<Dialog open={open} onOpenChange={setOpen}>
```

### Issue: Styles not applying
**Solution**: Ensure Tailwind is configured correctly
```js
// tailwind.config.js
content: ['./src/**/*.{js,ts,jsx,tsx}']
```

### Issue: Dark mode not working
**Solution**: Check ThemeProvider setup
```tsx
<ThemeProvider attribute="class">
```

## 📞 Support

For issues or questions:
1. Check the demo page for working examples
2. Review component source code
3. Check documentation files
4. Create an issue in the repository

---

**Quick Reference Version**: 1.0
**Last Updated**: January 28, 2026
