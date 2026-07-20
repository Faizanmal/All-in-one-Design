/**
 * Last-write-wins helpers for collaborative design sync.
 * Newer timestamps win; equal/older remote snapshots are ignored.
 */

export function shouldApplyRemoteSync(
  remoteTimestamp: number | undefined,
  lastAppliedTimestamp: number,
  lastSentTimestamp: number,
): boolean {
  const ts = typeof remoteTimestamp === 'number' ? remoteTimestamp : 0;
  if (ts <= 0) return true; // legacy payloads without timestamps
  if (ts <= lastAppliedTimestamp) return false;
  if (ts <= lastSentTimestamp) return false; // our own echo or superseded local edit
  return true;
}

export function nextSyncTimestamp(previous: number = 0): number {
  const now = Date.now();
  return now > previous ? now : previous + 1;
}
