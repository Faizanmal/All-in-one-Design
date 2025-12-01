# New Features Implementation Guide

This document describes the four major features implemented in this update:

## 1. AI Cost & Quota Controls

### Backend Components

**Models** (`/backend/subscriptions/quota_models.py`):
- `AIUsageQuota` - Monthly quota tracking per user
- `AIUsageRecord` - Individual AI request records  
- `BudgetAlert` - User-configurable spending alerts
- `AIModelPricing` - Configurable AI model pricing

**Service** (`/backend/subscriptions/quota_service.py`):
- `QuotaService` - Central quota management
  - `check_quota()` - Verify if operation is allowed
  - `use_quota()` - Record usage after operation
  - `estimate_cost()` - Calculate operation cost
  - `dry_run_check()` - Preview operation impact

**API Endpoints** (`/backend/subscriptions/quota_views.py`):
- `GET /api/v1/subscriptions/quotas/current/` - Current quota status
- `GET /api/v1/subscriptions/quota/usage-summary/` - Usage breakdown
- `POST /api/v1/subscriptions/quota/dry-run/` - Test operation impact
- `GET /api/v1/subscriptions/quota/dashboard/` - Dashboard data

### Frontend Components

**Hooks** (`/frontend/src/hooks/use-new-features.ts`):
- `useCurrentQuota()` - Get current quota data
- `useUsageSummary()` - Get usage breakdown by period
- `useDryRunCheck()` - Estimate operation cost
- `useQuotaDashboard()` - Dashboard aggregated data

**Component** (`/frontend/src/components/quota/QuotaDashboard.tsx`):
- Visual quota usage gauges
- Budget tracking with alerts
- Usage breakdown by operation type
- Cost estimator tool
- Recent activity feed

---

## 2. Visual Versioning with Diff

### Backend Components

**Models** (`/backend/projects/version_models.py`):
- `ProjectSnapshot` - Full design snapshots with thumbnails
- `VersionDiff` - Cached diffs between versions
- `VersionComment` - Comments on versions
- `VersionService` - Version management logic

**API Endpoints** (`/backend/projects/version_views.py`):
- `GET /api/v1/projects/projects/{id}/versions/` - List versions
- `POST /api/v1/projects/projects/{id}/versions/` - Create snapshot
- `POST /api/v1/projects/projects/{id}/versions/{ver}/restore/` - Restore version
- `POST /api/v1/projects/projects/{id}/versions/diff/` - Get diff
- `GET /api/v1/projects/projects/{id}/versions/branches/` - List branches
- `POST /api/v1/projects/projects/{id}/versions/branch/` - Create branch

### Frontend Components

**Hooks** (`/frontend/src/hooks/use-new-features.ts`):
- `useProjectVersions()` - List project versions
- `useCreateSnapshot()` - Save new version
- `useRestoreVersion()` - Restore to previous state
- `useVersionDiff()` - Compare versions
- `useProjectBranches()` - List branches
- `useCreateBranch()` - Create new branch

**Component** (`/frontend/src/components/version/VersionHistory.tsx`):
- Version timeline with thumbnails
- Branch tabs and creation
- Visual diff viewer
- Restore confirmation dialog
- Component-level change tracking

---

## 3. Real-time Collaboration

### Backend Components

**WebSocket Consumers** (`/backend/projects/realtime_consumers.py`):
- `CanvasConsumer` - Handles canvas operations
  - Object locking/unlocking
  - Canvas operation sync
  - Cursor position updates
  - Selection change sync
- `PresenceConsumer` - User presence tracking

**Routing** (`/backend/projects/routing.py`):
- `ws/canvas/<project_id>/` - Canvas WebSocket
- `ws/presence/<project_id>/` - Presence WebSocket

### Frontend Components

**Provider** (`/frontend/src/components/realtime/RealtimeProvider.tsx`):
- `RealtimeProvider` - Context provider for WebSocket connections
- `useRealtime()` - Hook to access collaboration state
- `CollaboratorCursors` - Renders remote user cursors
- `ConnectionStatus` - Shows connection state
- `ActiveCollaborators` - User avatar list

**Features**:
- Real-time cursor positions
- Object locking to prevent conflicts
- Presence indicators
- Auto-reconnection
- Throttled updates for performance

---

## 4. Accessibility Audit

### Backend Components

**Service** (`/backend/ai_services/accessibility_service.py`):
- `AccessibilityAuditService`
  - `audit_design()` - Full WCAG audit
  - `check_color_contrast()` - WCAG contrast checking
  - `calculate_wcag_level()` - Determine compliance level
  - `generate_auto_fixes()` - Suggest automatic fixes

**API Endpoints** (`/backend/ai_services/accessibility_views.py`):
- `POST /api/v1/ai/accessibility/projects/{id}/audit/` - Run audit
- `POST /api/v1/ai/accessibility/projects/{id}/fix/` - Apply fixes
- `POST /api/v1/ai/accessibility/check-contrast/` - Check contrast
- `GET /api/v1/ai/accessibility/wcag-guidelines/` - WCAG reference

### Frontend Components

**Hooks** (`/frontend/src/hooks/use-new-features.ts`):
- `useAccessibilityAudit()` - Run/get audit results
- `useApplyAccessibilityFixes()` - Apply auto-fixes
- `useCheckContrast()` - Manual contrast check
- `useAnalyzePalette()` - Analyze color palette

**Component** (`/frontend/src/components/accessibility/AccessibilityAudit.tsx`):
- Accessibility score gauge
- Issues grouped by category
- Severity-based filtering
- Auto-fix selection and application
- Manual contrast checker tool
- WCAG level selector (A/AA/AAA)

---

## Usage Examples

### Check Quota Before AI Operation

```typescript
const dryRun = useDryRunCheck();

const handleGenerateImage = async () => {
  const check = await dryRun.mutateAsync({
    operationType: 'image_generation',
    amount: 1,
  });
  
  if (!check.allowed) {
    alert('Quota exceeded!');
    return;
  }
  
  // Proceed with generation
};
```

### Create Version Snapshot

```typescript
const createSnapshot = useCreateSnapshot();

const handleSave = async () => {
  await createSnapshot.mutateAsync({
    projectId: project.id,
    label: 'Before major redesign',
    changeSummary: 'Saving current state',
  });
};
```

### Use Real-time Collaboration

```tsx
function CanvasEditor({ projectId }: { projectId: string }) {
  return (
    <RealtimeProvider projectId={projectId} user={currentUser}>
      <Canvas />
      <CollaboratorCursors />
      <ConnectionStatus />
    </RealtimeProvider>
  );
}
```

### Run Accessibility Audit

```typescript
const { data: audit } = useAccessibilityAudit(projectId, {
  targetLevel: 'AA',
});

const applyFixes = useApplyAccessibilityFixes();

const handleFixAll = async () => {
  await applyFixes.mutateAsync({
    projectId,
    applyAll: true,
  });
};
```

---

## Database Migrations

Run migrations to set up the new models:

```bash
cd backend
python manage.py migrate
```

## Dependencies

Ensure these are installed:

```bash
# Backend
pip install stripe Pillow channels channels-redis

# Frontend
npm install @tanstack/react-query
```
