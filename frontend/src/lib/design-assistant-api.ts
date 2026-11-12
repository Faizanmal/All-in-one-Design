import apiClient from '@/lib/design-api';
import { isAxiosError } from 'axios';

export async function requestDesignAssistant<T extends Record<string, unknown>>(
  action: string,
  payload: Record<string, unknown>,
): Promise<T> {
  let data: T;
  try {
    ({ data } = await apiClient.post<T>(`/ai/${action}/`, payload));
  } catch (error) {
    if (isAxiosError(error)) {
      const message = error.response?.data?.error ?? error.response?.data?.detail;
      if (typeof message === 'string') throw new Error(message);
    }
    throw error;
  }
  if (data.success === false) {
    throw new Error(typeof data.error === 'string' ? data.error : 'The AI service could not complete this request. Please try again.');
  }
  return data;
}
