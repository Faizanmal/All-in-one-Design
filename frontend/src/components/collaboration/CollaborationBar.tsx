'use client';

import { CollaborativeUser } from '@/hooks/useCollaborativeCanvas';

const USER_COLORS = [
  '#E4572E', '#17BEBB', '#FFC914', '#2E282A',
  '#76B041', '#3A86FF', '#8338EC', '#FF006E',
];

function colorForUser(userId: number): string {
  return USER_COLORS[Math.abs(userId) % USER_COLORS.length];
}

interface CollaborationBarProps {
  isConnected: boolean;
  activeUsers: CollaborativeUser[];
  projectId: number | null;
}

export function CollaborationBar({ isConnected, activeUsers, projectId }: CollaborationBarProps) {
  if (!projectId) return null;

  return (
    <div className="flex items-center gap-3 text-xs">
      <span
        className={`inline-flex items-center gap-1.5 rounded-md px-2 py-1 border ${
          isConnected
            ? 'border-emerald-500/40 text-emerald-700 dark:text-emerald-400'
            : 'border-amber-500/40 text-amber-700 dark:text-amber-400'
        }`}
      >
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            isConnected ? 'bg-emerald-500' : 'bg-amber-500'
          }`}
        />
        {isConnected ? 'Live' : 'Reconnecting'}
      </span>

      <div className="flex items-center -space-x-1.5">
        {activeUsers.slice(0, 5).map((user) => (
          <div
            key={user.user_id}
            title={user.username}
            className="h-6 w-6 rounded-full border-2 border-background flex items-center justify-center text-[10px] font-semibold text-white"
            style={{ backgroundColor: colorForUser(user.user_id) }}
          >
            {user.username?.slice(0, 1).toUpperCase() || '?'}
          </div>
        ))}
        {activeUsers.length > 5 && (
          <span className="pl-3 text-muted-foreground">+{activeUsers.length - 5}</span>
        )}
      </div>

      {activeUsers.length > 0 && (
        <span className="text-muted-foreground">
          {activeUsers.length} collaborator{activeUsers.length === 1 ? '' : 's'}
        </span>
      )}
    </div>
  );
}

interface CollaborationCursorsOverlayProps {
  activeUsers: CollaborativeUser[];
}

export function CollaborationCursorsOverlay({ activeUsers }: CollaborationCursorsOverlayProps) {
  const withCursor = activeUsers.filter(u => u.cursor_position);

  if (withCursor.length === 0) return null;

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden z-20">
      {withCursor.map((user) => {
        const x = user.cursor_position!.x;
        const y = user.cursor_position!.y;
        const color = colorForUser(user.user_id);
        return (
          <div
            key={user.user_id}
            className="absolute transition-transform duration-75"
            style={{ transform: `translate(${x}px, ${y}px)` }}
          >
            <svg width="16" height="20" viewBox="0 0 16 20" fill={color}>
              <path d="M0 0 L16 12 L9 13 L12 20 L9 21 L6 14 L0 18 Z" />
            </svg>
            <span
              className="ml-3 -mt-1 inline-block rounded px-1.5 py-0.5 text-[10px] font-medium text-white"
              style={{ backgroundColor: color }}
            >
              {user.username}
            </span>
          </div>
        );
      })}
    </div>
  );
}
