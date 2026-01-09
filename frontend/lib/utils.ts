import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, parseISO } from 'date-fns';
import { ko } from 'date-fns/locale';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Date formatting utilities
export function formatDate(date: string | Date, formatStr: string = 'yyyy-MM-dd'): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, formatStr, { locale: ko });
}

export function formatTime(time: string): string {
  const [hours, minutes] = time.split(':');
  return `${hours}:${minutes}`;
}

export function formatDateTime(datetime: string, formatStr: string = 'yyyy-MM-dd HH:mm'): string {
  return format(parseISO(datetime), formatStr, { locale: ko });
}

export function formatDateTimeKorean(datetime: string): string {
  return format(parseISO(datetime), 'M월 d일 (E) a h:mm', { locale: ko });
}

// Copy to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
}

// Share URL
export function getShareUrl(slug: string): string {
  const baseUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000';
  return `${baseUrl}/e/${slug}`;
}

// Validation
export function isValidEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Error handling
export function getErrorMessage(error: any): string {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.response?.data) {
    const data = error.response.data;
    const firstKey = Object.keys(data)[0];
    if (Array.isArray(data[firstKey])) {
      return data[firstKey][0];
    }
    return data[firstKey];
  }
  if (error.message) {
    return error.message;
  }
  return '알 수 없는 오류가 발생했습니다';
}
