import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '@/hooks/useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('hello', 500));
    expect(result.current).toBe('hello');
  });

  it('debounces value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'hello', delay: 500 } }
    );

    expect(result.current).toBe('hello');

    rerender({ value: 'world', delay: 500 });
    // Value should not change immediately
    expect(result.current).toBe('hello');

    // Advance time past the delay
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(result.current).toBe('world');
  });

  it('cancels previous timer on rapid changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'a', delay: 300 } }
    );

    rerender({ value: 'b', delay: 300 });
    act(() => { vi.advanceTimersByTime(100); });
    
    rerender({ value: 'c', delay: 300 });
    act(() => { vi.advanceTimersByTime(100); });
    
    // Should still be 'a' since timers were cancelled
    expect(result.current).toBe('a');

    // After full delay, should be 'c'
    act(() => { vi.advanceTimersByTime(300); });
    expect(result.current).toBe('c');
  });

  it('handles numeric values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 0, delay: 200 } }
    );

    rerender({ value: 42, delay: 200 });
    act(() => { vi.advanceTimersByTime(200); });
    expect(result.current).toBe(42);
  });

  it('handles object values', () => {
    const initialObj = { key: 'initial' };
    const newObj = { key: 'updated' };

    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initialObj, delay: 200 } }
    );

    rerender({ value: newObj, delay: 200 });
    act(() => { vi.advanceTimersByTime(200); });
    expect(result.current).toEqual({ key: 'updated' });
  });

  afterEach(() => {
    vi.useRealTimers();
  });
});
