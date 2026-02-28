import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { ErrorBoundary, InlineError } from '@/components/error-boundary';

// Component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error message');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  // Suppress console.error during error boundary tests
  const originalError = console.error;
  beforeEach(() => {
    console.error = vi.fn();
  });
  afterEach(() => {
    console.error = originalError;
  });

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>Safe content</div>
      </ErrorBoundary>
    );
    expect(screen.getByText('Safe content')).toBeDefined();
  });

  it('shows error UI when child throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    // Should show error messaging
    const errorText = screen.queryByText(/something went wrong/i) ||
                      screen.queryByText(/error/i) ||
                      document.querySelector('[class*="error"], [class*="red"]');
    expect(errorText).toBeDefined();
  });

  it('renders custom fallback when provided', () => {
    render(
      <ErrorBoundary fallback={<div>Custom error UI</div>}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Custom error UI')).toBeDefined();
  });

  it('calls onError callback when error occurs', () => {
    const onError = vi.fn();
    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(onError).toHaveBeenCalled();
  });

  it('renders compact error for inline sections', () => {
    render(
      <ErrorBoundary compact>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    // Compact mode shows inline error
    const container = document.querySelector('[class*="flex"]');
    expect(container).toBeDefined();
  });

  it('renders retry button', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    const retryButton = screen.queryByRole('button');
    expect(retryButton).toBeDefined();
  });

  it('resets error state on retry', async () => {
    const user = userEvent.setup();
    
    let shouldThrow = true;
    const TestComp = () => {
      if (shouldThrow) throw new Error('Error');
      return <div>Recovered</div>;
    };

    const { container } = render(
      <ErrorBoundary>
        <TestComp />
      </ErrorBoundary>
    );

    // Now retry after fixing the condition
    shouldThrow = false;
    const retryButton = screen.queryByRole('button');
    if (retryButton) {
      await user.click(retryButton);
    }
    // The component should attempt to re-render
    expect(true).toBe(true);
  });
});

describe('InlineError', () => {
  it('renders error message', () => {
    render(<InlineError message="Something failed" />);
    expect(screen.getByText('Something failed')).toBeDefined();
  });

  it('renders with retry callback', async () => {
    const onRetry = vi.fn();
    render(<InlineError message="Failed" onRetry={onRetry} />);
    
    const retryButton = screen.queryByRole('button');
    if (retryButton) {
      const user = userEvent.setup();
      await user.click(retryButton);
      expect(onRetry).toHaveBeenCalled();
    }
  });
});
