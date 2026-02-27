import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader, CardFooter } from '@/components/ui/card';

/**
 * Skeleton for a project card in grid view
 */
export function ProjectCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="aspect-video w-full rounded" />
        <Skeleton className="h-5 w-3/4 mt-2" />
        <Skeleton className="h-4 w-1/2" />
      </CardHeader>
      <CardFooter>
        <Skeleton className="h-3 w-1/3" />
      </CardFooter>
    </Card>
  );
}

/**
 * Skeleton grid for project listings
 */
export function ProjectGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <ProjectCardSkeleton key={i} />
      ))}
    </div>
  );
}

/**
 * Skeleton for dashboard stat cards
 */
export function StatCardSkeleton() {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-16" />
          </div>
          <Skeleton className="h-10 w-10 rounded-full" />
        </div>
        <Skeleton className="h-3 w-20 mt-2" />
      </CardContent>
    </Card>
  );
}

/**
 * Skeleton for dashboard stats row
 */
export function StatsRowSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <StatCardSkeleton key={i} />
      ))}
    </div>
  );
}

/**
 * Skeleton for a table row
 */
export function TableRowSkeleton({ columns = 5 }: { columns?: number }) {
  return (
    <div className="flex items-center gap-4 p-4 border-b border-gray-100 dark:border-gray-800">
      {Array.from({ length: columns }).map((_, i) => (
        <Skeleton
          key={i}
          className={`h-4 ${i === 0 ? 'w-1/4' : i === columns - 1 ? 'w-16' : 'w-1/6'}`}
        />
      ))}
    </div>
  );
}

/**
 * Skeleton for a list/table
 */
export function TableSkeleton({ rows = 5, columns = 5 }: { rows?: number; columns?: number }) {
  return (
    <Card>
      <div className="p-4 border-b border-gray-100 dark:border-gray-800">
        <Skeleton className="h-5 w-32" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <TableRowSkeleton key={i} columns={columns} />
      ))}
    </Card>
  );
}

/**
 * Full-page loading state
 */
export function PageSkeleton() {
  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>
      {/* Stats */}
      <StatsRowSkeleton />
      {/* Content */}
      <div className="space-y-4">
        <Skeleton className="h-6 w-40" />
        <ProjectGridSkeleton count={4} />
      </div>
    </div>
  );
}

/**
 * Skeleton for settings form
 */
export function FormSkeleton({ fields = 6 }: { fields?: number }) {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-72" />
      </CardHeader>
      <CardContent className="space-y-6">
        {Array.from({ length: fields }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-10 w-full" />
          </div>
        ))}
      </CardContent>
      <CardFooter>
        <Skeleton className="h-10 w-32" />
      </CardFooter>
    </Card>
  );
}
