/**
 * React Hooks for Advanced Figma-like Features
 * Production-ready hooks using React Query
 */
import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query';
import { autoLayoutApi, AutoLayoutFrame, LayoutPreset, ResponsiveBreakpoint } from '@/lib/auto-layout-api';
import { componentVariantsApi, ComponentSet, ComponentVariant, ComponentProperty, ComponentInstance } from '@/lib/component-variants-api';
import { designBranchesApi, DesignBranch, DesignCommit, BranchReview, BranchComparison } from '@/lib/design-branches-api';
import { animationTimelineApi, AnimationProject, AnimationComposition, AnimationLayer, AnimationKeyframe, LottieExport } from '@/lib/animation-timeline-api';
import { designQAApi, LintRuleSet, DesignLintReport, LintIssue, AccessibilityReport, QASummary } from '@/lib/design-qa-api';
import { presentationModeApi, Presentation, PresentationSlide, DevModeProject, CodeExportConfig, NodeSpecs } from '@/lib/presentation-mode-api';
import { whiteboardApi, Whiteboard, StickyNote, WhiteboardShape, Connector, WhiteboardComment, WhiteboardElements } from '@/lib/whiteboard-api';
import { mobileApi, MobileDevice, MobileSession, OfflineCache, MobileNotification, MobilePreference, SyncStatus } from '@/lib/mobile-api';

// ==================== Auto Layout Hooks ====================

export function useAutoLayoutFrames(projectId: number, options?: UseQueryOptions<AutoLayoutFrame[]>) {
  return useQuery({
    queryKey: ['auto-layout-frames', projectId],
    queryFn: () => autoLayoutApi.getFrames(projectId),
    ...options,
  });
}

export function useAutoLayoutFrame(frameId: string, options?: UseQueryOptions<AutoLayoutFrame>) {
  return useQuery({
    queryKey: ['auto-layout-frame', frameId],
    queryFn: () => autoLayoutApi.getFrame(frameId),
    enabled: !!frameId,
    ...options,
  });
}

export function useLayoutPresets(category?: string, options?: UseQueryOptions<LayoutPreset[]>) {
  return useQuery({
    queryKey: ['layout-presets', category],
    queryFn: () => autoLayoutApi.getPresets(category),
    ...options,
  });
}

export function useResponsiveBreakpoints(projectId: number, options?: UseQueryOptions<ResponsiveBreakpoint[]>) {
  return useQuery({
    queryKey: ['responsive-breakpoints', projectId],
    queryFn: () => autoLayoutApi.getBreakpoints(projectId),
    ...options,
  });
}

export function useAILayoutSuggestions(projectId: number, nodeIds: string[]) {
  return useQuery({
    queryKey: ['ai-layout-suggestions', projectId, nodeIds],
    queryFn: () => autoLayoutApi.getAISuggestions(projectId, nodeIds),
    enabled: nodeIds.length > 0,
  });
}

export function useUpdateAutoLayoutFrame() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ frameId, updates }: { frameId: string; updates: Partial<AutoLayoutFrame> }) =>
      autoLayoutApi.updateFrame(frameId, updates),
    onSuccess: (data, { frameId }) => {
      queryClient.invalidateQueries({ queryKey: ['auto-layout-frame', frameId] });
      queryClient.invalidateQueries({ queryKey: ['auto-layout-frames'] });
    },
  });
}

export function useApplyLayoutPreset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ frameId, presetId }: { frameId: string; presetId: string }) =>
      autoLayoutApi.applyPresetToFrame(frameId, presetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auto-layout-frames'] });
    },
  });
}

export function useAutoArrange() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, nodeIds, options }: {
      projectId: number;
      nodeIds: string[];
      options?: { spacing?: number; alignment?: string; direction?: 'horizontal' | 'vertical' };
    }) => autoLayoutApi.autoArrange(projectId, nodeIds, options),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auto-layout-frames'] });
    },
  });
}

// ==================== Component Variants Hooks ====================

export function useComponentSets(projectId: number, options?: { category?: string; search?: string }) {
  return useQuery({
    queryKey: ['component-sets', projectId, options],
    queryFn: () => componentVariantsApi.getComponentSets(projectId, options),
  });
}

export function useComponentSet(setId: string) {
  return useQuery({
    queryKey: ['component-set', setId],
    queryFn: () => componentVariantsApi.getComponentSet(setId),
    enabled: !!setId,
  });
}

export function useComponentVariants(setId: string) {
  return useQuery({
    queryKey: ['component-variants', setId],
    queryFn: () => componentVariantsApi.getVariants(setId),
    enabled: !!setId,
  });
}

export function useVariantMatrix(setId: string) {
  return useQuery({
    queryKey: ['variant-matrix', setId],
    queryFn: () => componentVariantsApi.getVariantMatrix(setId),
    enabled: !!setId,
  });
}

export function useComponentProperties(setId: string) {
  return useQuery({
    queryKey: ['component-properties', setId],
    queryFn: () => componentVariantsApi.getProperties(setId),
    enabled: !!setId,
  });
}

export function useComponentInstances(componentSetId: string) {
  return useQuery({
    queryKey: ['component-instances', componentSetId],
    queryFn: () => componentVariantsApi.getInstances(componentSetId),
    enabled: !!componentSetId,
  });
}

export function useCreateVariant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variant: Partial<ComponentVariant>) => componentVariantsApi.createVariant(variant),
    onSuccess: (_, variant) => {
      queryClient.invalidateQueries({ queryKey: ['component-variants', variant.component_set] });
      queryClient.invalidateQueries({ queryKey: ['variant-matrix', variant.component_set] });
    },
  });
}

export function useUpdateVariant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ variantId, updates }: { variantId: string; updates: Partial<ComponentVariant> }) =>
      componentVariantsApi.updateVariant(variantId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['component-variants'] });
    },
  });
}

export function useSwapComponent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ instanceId, newComponentSetId }: { instanceId: string; newComponentSetId: string }) =>
      componentVariantsApi.swapComponent(instanceId, newComponentSetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['component-instances'] });
    },
  });
}

// ==================== Design Branches Hooks ====================

export function useDesignBranches(projectId: number, options?: { status?: string; search?: string }) {
  return useQuery({
    queryKey: ['design-branches', projectId, options],
    queryFn: () => designBranchesApi.getBranches(projectId, options as { status?: 'active' | 'merged' | 'closed' | 'archived'; search?: string }),
  });
}

export function useDesignBranch(branchId: string) {
  return useQuery({
    queryKey: ['design-branch', branchId],
    queryFn: () => designBranchesApi.getBranch(branchId),
    enabled: !!branchId,
  });
}

export function useCommitHistory(branchId: string, options?: { limit?: number }) {
  return useQuery({
    queryKey: ['commit-history', branchId, options],
    queryFn: () => designBranchesApi.getCommitHistory(branchId, options),
    enabled: !!branchId,
  });
}

export function useBranchComparison(sourceBranch: string, targetBranch: string) {
  return useQuery({
    queryKey: ['branch-comparison', sourceBranch, targetBranch],
    queryFn: () => designBranchesApi.createComparison(sourceBranch, targetBranch),
    enabled: !!sourceBranch && !!targetBranch,
  });
}

export function useBranchReviews(branchId: string) {
  return useQuery({
    queryKey: ['branch-reviews', branchId],
    queryFn: () => designBranchesApi.getReviews(branchId),
    enabled: !!branchId,
  });
}

export function useBranchDiff(branchId: string, targetBranchId?: string) {
  return useQuery({
    queryKey: ['branch-diff', branchId, targetBranchId],
    queryFn: () => designBranchesApi.getDiff(branchId, targetBranchId),
    enabled: !!branchId,
  });
}

export function useCreateBranch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (branch: { project: number; name: string; description?: string; parent_branch?: string }) =>
      designBranchesApi.createBranch(branch),
    onSuccess: (_, { project }) => {
      queryClient.invalidateQueries({ queryKey: ['design-branches', project] });
    },
  });
}

export function useCreateCommit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (commit: { branch: string; message: string; description?: string; snapshot_data: Record<string, unknown> }) =>
      designBranchesApi.createCommit(commit),
    onSuccess: (_, { branch }) => {
      queryClient.invalidateQueries({ queryKey: ['commit-history', branch] });
      queryClient.invalidateQueries({ queryKey: ['design-branch', branch] });
    },
  });
}

export function useMergeBranch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ sourceBranch, targetBranch, options }: {
      sourceBranch: string;
      targetBranch: string;
      options?: { strategy?: 'merge' | 'squash' | 'rebase'; message?: string };
    }) => designBranchesApi.merge(sourceBranch, targetBranch, options || {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['design-branches'] });
      queryClient.invalidateQueries({ queryKey: ['commit-history'] });
    },
  });
}

export function useResolveConflict() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ conflictId, resolution, resolvedValue }: {
      conflictId: string;
      resolution: 'keep_source' | 'keep_target' | 'manual' | 'merge_styles';
      resolvedValue?: Record<string, unknown>;
    }) => designBranchesApi.resolveConflict(conflictId, resolution, resolvedValue),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['branch-comparison'] });
    },
  });
}

// ==================== Animation Timeline Hooks ====================

export function useAnimationProjects(projectId: number) {
  return useQuery({
    queryKey: ['animation-projects', projectId],
    queryFn: () => animationTimelineApi.getProjects(projectId),
  });
}

export function useAnimationProject(animationProjectId: string) {
  return useQuery({
    queryKey: ['animation-project', animationProjectId],
    queryFn: () => animationTimelineApi.getProject(animationProjectId),
    enabled: !!animationProjectId,
  });
}

export function useAnimationCompositions(animationProjectId: string) {
  return useQuery({
    queryKey: ['animation-compositions', animationProjectId],
    queryFn: () => animationTimelineApi.getCompositions(animationProjectId),
    enabled: !!animationProjectId,
  });
}

export function useAnimationComposition(compositionId: string) {
  return useQuery({
    queryKey: ['animation-composition', compositionId],
    queryFn: () => animationTimelineApi.getComposition(compositionId),
    enabled: !!compositionId,
  });
}

export function useAnimationLayers(compositionId: string) {
  return useQuery({
    queryKey: ['animation-layers', compositionId],
    queryFn: () => animationTimelineApi.getLayers(compositionId),
    enabled: !!compositionId,
  });
}

export function useAnimationKeyframes(trackId: string) {
  return useQuery({
    queryKey: ['animation-keyframes', trackId],
    queryFn: () => animationTimelineApi.getKeyframes(trackId),
    enabled: !!trackId,
  });
}

export function useEasingPresets(category?: string) {
  return useQuery({
    queryKey: ['easing-presets', category],
    queryFn: () => animationTimelineApi.getEasingPresets(category),
  });
}

export function useLottieExports(compositionId: string) {
  return useQuery({
    queryKey: ['lottie-exports', compositionId],
    queryFn: () => animationTimelineApi.getLottieExports(compositionId),
    enabled: !!compositionId,
  });
}

export function useCreateKeyframe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (keyframe: Partial<AnimationKeyframe>) => animationTimelineApi.createKeyframe(keyframe),
    onSuccess: (_, keyframe) => {
      queryClient.invalidateQueries({ queryKey: ['animation-keyframes', keyframe.track] });
    },
  });
}

export function useUpdateKeyframe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ keyframeId, updates }: { keyframeId: string; updates: Partial<AnimationKeyframe> }) =>
      animationTimelineApi.updateKeyframe(keyframeId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animation-keyframes'] });
    },
  });
}

export function useExportLottie() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ compositionId, options }: {
      compositionId: string;
      options?: { optimize?: boolean; include_hidden?: boolean };
    }) => animationTimelineApi.createLottieExport(compositionId, options),
    onSuccess: (_, { compositionId }) => {
      queryClient.invalidateQueries({ queryKey: ['lottie-exports', compositionId] });
    },
  });
}

export function useRenderPreview() {
  return useMutation({
    mutationFn: ({ compositionId, options }: {
      compositionId: string;
      options?: { format?: 'gif' | 'mp4' | 'webm'; quality?: 'low' | 'medium' | 'high' };
    }) => animationTimelineApi.renderPreview(compositionId, options),
  });
}

// ==================== Design QA Hooks ====================

export function useLintRuleSets(options?: { is_default?: boolean }) {
  return useQuery({
    queryKey: ['lint-rule-sets', options],
    queryFn: () => designQAApi.getRuleSets(options),
  });
}

export function useLintRuleSet(ruleSetId: string) {
  return useQuery({
    queryKey: ['lint-rule-set', ruleSetId],
    queryFn: () => designQAApi.getRuleSet(ruleSetId),
    enabled: !!ruleSetId,
  });
}

export function useLintReports(projectId: number, options?: { status?: string; limit?: number }) {
  return useQuery({
    queryKey: ['lint-reports', projectId, options],
    queryFn: () => designQAApi.getLintReports(projectId, options),
  });
}

export function useLintReport(reportId: string) {
  return useQuery({
    queryKey: ['lint-report', reportId],
    queryFn: () => designQAApi.getLintReport(reportId),
    enabled: !!reportId,
  });
}

export function useLintIssues(reportId: string, options?: { status?: 'open' | 'resolved' | 'ignored' | 'wont_fix'; severity?: 'error' | 'warning' | 'info' }) {
  return useQuery({
    queryKey: ['lint-issues', reportId, options],
    queryFn: () => designQAApi.getLintIssues(reportId, options),
    enabled: !!reportId,
  });
}

export function useAccessibilityReports(projectId: number, options?: { limit?: number }) {
  return useQuery({
    queryKey: ['accessibility-reports', projectId, options],
    queryFn: () => designQAApi.getAccessibilityReports(projectId, options),
  });
}

export function useAccessibilityReport(reportId: string) {
  return useQuery({
    queryKey: ['accessibility-report', reportId],
    queryFn: () => designQAApi.getAccessibilityReport(reportId),
    enabled: !!reportId,
  });
}

export function useQASummary(projectId: number) {
  return useQuery({
    queryKey: ['qa-summary', projectId],
    queryFn: () => designQAApi.getQASummary(projectId),
  });
}

export function useQADashboard(projectId: number) {
  return useQuery({
    queryKey: ['qa-dashboard', projectId],
    queryFn: () => designQAApi.getQADashboard(projectId),
  });
}

export function useRunLintCheck() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, options }: {
      projectId: number;
      options?: { rule_set?: string; node_ids?: string[]; fix_auto?: boolean };
    }) => designQAApi.runLintCheck(projectId, options),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['lint-reports', projectId] });
      queryClient.invalidateQueries({ queryKey: ['qa-summary', projectId] });
    },
  });
}

export function useRunAccessibilityCheck() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, options }: {
      projectId: number;
      options?: { wcag_level?: 'A' | 'AA' | 'AAA'; node_ids?: string[] };
    }) => designQAApi.runAccessibilityCheck(projectId, options),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['accessibility-reports', projectId] });
      queryClient.invalidateQueries({ queryKey: ['qa-summary', projectId] });
    },
  });
}

export function useResolveIssue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (issueId: string) => designQAApi.resolveIssue(issueId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lint-issues'] });
      queryClient.invalidateQueries({ queryKey: ['lint-report'] });
    },
  });
}

export function useAutoFixIssue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (issueId: string) => designQAApi.autoFixIssue(issueId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lint-issues'] });
    },
  });
}

// ==================== Presentation Mode Hooks ====================

export function usePresentations(projectId: number) {
  return useQuery({
    queryKey: ['presentations', projectId],
    queryFn: () => presentationModeApi.getPresentations(projectId),
  });
}

export function usePresentation(presentationId: string) {
  return useQuery({
    queryKey: ['presentation', presentationId],
    queryFn: () => presentationModeApi.getPresentation(presentationId),
    enabled: !!presentationId,
  });
}

export function usePresentationSlides(presentationId: string) {
  return useQuery({
    queryKey: ['presentation-slides', presentationId],
    queryFn: () => presentationModeApi.getSlides(presentationId),
    enabled: !!presentationId,
  });
}

export function useDevModeProject(projectId: number) {
  return useQuery({
    queryKey: ['dev-mode-project', projectId],
    queryFn: () => presentationModeApi.getDevModeProject(projectId),
  });
}

export function useNodeSpecs(projectId: number, nodeId: string, format?: string) {
  return useQuery({
    queryKey: ['node-specs', projectId, nodeId, format],
    queryFn: () => presentationModeApi.getNodeSpecs(projectId, nodeId, format as any),
    enabled: !!nodeId,
  });
}

export function useCodeExportConfigs(projectId: number) {
  return useQuery({
    queryKey: ['code-export-configs', projectId],
    queryFn: () => presentationModeApi.getCodeExportConfigs(projectId),
  });
}

export function useAssetExportQueue(projectId: number) {
  return useQuery({
    queryKey: ['asset-export-queue', projectId],
    queryFn: () => presentationModeApi.getAssetExportQueue(projectId),
  });
}

export function useStartPresentation() {
  return useMutation({
    mutationFn: (presentationId: string) => presentationModeApi.startPresentation(presentationId),
  });
}

export function useCreatePresentation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (presentation: Partial<Presentation>) => presentationModeApi.createPresentation(presentation),
    onSuccess: (_, presentation) => {
      queryClient.invalidateQueries({ queryKey: ['presentations', presentation.project] });
    },
  });
}

export function useExportCode() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ configId, nodeIds }: { configId: string; nodeIds: string[] }) =>
      presentationModeApi.exportCode(configId, nodeIds),
    onSuccess: (_, { configId }) => {
      queryClient.invalidateQueries({ queryKey: ['code-export-history', configId] });
    },
  });
}

export function useQueueAssetExport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (asset: { project: number; node_id: string; format: 'png' | 'jpg' | 'svg' | 'pdf' | 'webp'; scale?: number }) =>
      presentationModeApi.queueAssetExport(asset),
    onSuccess: (_, { project }) => {
      queryClient.invalidateQueries({ queryKey: ['asset-export-queue', project] });
    },
  });
}

// ==================== Whiteboard Hooks ====================

export function useWhiteboards(options?: { team?: number; project?: number; search?: string }) {
  return useQuery({
    queryKey: ['whiteboards', options],
    queryFn: () => whiteboardApi.getWhiteboards(options),
  });
}

export function useWhiteboard(whiteboardId: string) {
  return useQuery({
    queryKey: ['whiteboard', whiteboardId],
    queryFn: () => whiteboardApi.getWhiteboard(whiteboardId),
    enabled: !!whiteboardId,
  });
}

export function useWhiteboardElements(whiteboardId: string) {
  return useQuery({
    queryKey: ['whiteboard-elements', whiteboardId],
    queryFn: () => whiteboardApi.getElements(whiteboardId),
    enabled: !!whiteboardId,
    refetchInterval: 5000,
  });
}

export function useStickyNotes(whiteboardId: string) {
  return useQuery({
    queryKey: ['sticky-notes', whiteboardId],
    queryFn: () => whiteboardApi.getStickyNotes(whiteboardId),
    enabled: !!whiteboardId,
  });
}

export function useWhiteboardShapes(whiteboardId: string) {
  return useQuery({
    queryKey: ['whiteboard-shapes', whiteboardId],
    queryFn: () => whiteboardApi.getShapes(whiteboardId),
    enabled: !!whiteboardId,
  });
}

export function useWhiteboardComments(whiteboardId: string) {
  return useQuery({
    queryKey: ['whiteboard-comments', whiteboardId],
    queryFn: () => whiteboardApi.getComments(whiteboardId),
    enabled: !!whiteboardId,
  });
}

export function useWhiteboardTemplates(category?: string) {
  return useQuery({
    queryKey: ['whiteboard-templates', category],
    queryFn: () => whiteboardApi.getTemplates(category),
  });
}

export function useCreateWhiteboard() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (whiteboard: Partial<Whiteboard>) => whiteboardApi.createWhiteboard(whiteboard),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whiteboards'] });
    },
  });
}

export function useJoinWhiteboard() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (whiteboardId: string) => whiteboardApi.joinWhiteboard(whiteboardId),
    onSuccess: (_, whiteboardId) => {
      queryClient.invalidateQueries({ queryKey: ['whiteboard', whiteboardId] });
    },
  });
}

export function useCreateStickyNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (stickyNote: Partial<StickyNote>) => whiteboardApi.createStickyNote(stickyNote),
    onSuccess: (_, stickyNote) => {
      queryClient.invalidateQueries({ queryKey: ['sticky-notes', stickyNote.whiteboard] });
      queryClient.invalidateQueries({ queryKey: ['whiteboard-elements', stickyNote.whiteboard] });
    },
  });
}

export function useUpdateStickyNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ noteId, updates }: { noteId: string; updates: Partial<StickyNote> }) =>
      whiteboardApi.updateStickyNote(noteId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sticky-notes'] });
      queryClient.invalidateQueries({ queryKey: ['whiteboard-elements'] });
    },
  });
}

export function useCreateShape() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (shape: Partial<WhiteboardShape>) => whiteboardApi.createShape(shape),
    onSuccess: (_, shape) => {
      queryClient.invalidateQueries({ queryKey: ['whiteboard-shapes', shape.whiteboard] });
      queryClient.invalidateQueries({ queryKey: ['whiteboard-elements', shape.whiteboard] });
    },
  });
}

export function useCreateConnector() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (connector: Partial<Connector>) => whiteboardApi.createConnector(connector),
    onSuccess: (_, connector) => {
      queryClient.invalidateQueries({ queryKey: ['whiteboard-elements', connector.whiteboard] });
    },
  });
}

export function useVoteStickyNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (noteId: string) => whiteboardApi.voteStickyNote(noteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sticky-notes'] });
    },
  });
}

// ==================== Mobile API Hooks ====================

export function useMobileDevices() {
  return useQuery({
    queryKey: ['mobile-devices'],
    queryFn: () => mobileApi.getDevices(),
  });
}

export function useMobileDevice(deviceId: string) {
  return useQuery({
    queryKey: ['mobile-device', deviceId],
    queryFn: () => mobileApi.getDevice(deviceId),
    enabled: !!deviceId,
  });
}

export function useMobileSessions() {
  return useQuery({
    queryKey: ['mobile-sessions'],
    queryFn: () => mobileApi.getSessions(),
  });
}

export function useOfflineCache(deviceId: string) {
  return useQuery({
    queryKey: ['offline-cache', deviceId],
    queryFn: () => mobileApi.getCachedItems(deviceId),
    enabled: !!deviceId,
  });
}

export function useSyncStatus(deviceId: string) {
  return useQuery({
    queryKey: ['sync-status', deviceId],
    queryFn: () => mobileApi.getSyncStatus(deviceId),
    enabled: !!deviceId,
    refetchInterval: 10000,
  });
}

export function useMobileNotifications(options?: { is_read?: boolean; notification_type?: string }) {
  return useQuery({
    queryKey: ['mobile-notifications', options],
    queryFn: () => mobileApi.getNotifications(options as any),
  });
}

export function useUnreadNotificationCount() {
  return useQuery({
    queryKey: ['unread-notification-count'],
    queryFn: () => mobileApi.getUnreadCount(),
    refetchInterval: 30000,
  });
}

export function useMobilePreferences() {
  return useQuery({
    queryKey: ['mobile-preferences'],
    queryFn: () => mobileApi.getPreferences(),
  });
}

export function useRegisterDevice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (device: Parameters<typeof mobileApi.registerDevice>[0]) =>
      mobileApi.registerDevice(device),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mobile-devices'] });
    },
  });
}

export function useSyncContent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ deviceId, contentIds }: { deviceId: string; contentIds?: string[] }) =>
      mobileApi.syncContent(deviceId, contentIds),
    onSuccess: (_, { deviceId }) => {
      queryClient.invalidateQueries({ queryKey: ['offline-cache', deviceId] });
      queryClient.invalidateQueries({ queryKey: ['sync-status', deviceId] });
    },
  });
}

export function useMarkNotificationAsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (notificationId: string) => mobileApi.markAsRead(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mobile-notifications'] });
      queryClient.invalidateQueries({ queryKey: ['unread-notification-count'] });
    },
  });
}

export function useUpdateMobilePreferences() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (updates: Partial<MobilePreference>) => mobileApi.updatePreferences(updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mobile-preferences'] });
    },
  });
}

export function useCheckAppVersion() {
  return useMutation({
    mutationFn: ({ platform, currentVersion }: { platform: 'ios' | 'android' | 'web' | 'desktop'; currentVersion: string }) =>
      mobileApi.checkVersion(platform, currentVersion),
  });
}

export function useTrackAnalyticsEvent() {
  return useMutation({
    mutationFn: (event: Parameters<typeof mobileApi.trackEvent>[0]) =>
      mobileApi.trackEvent(event),
  });
}
