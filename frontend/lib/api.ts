import axios, { AxiosError } from 'axios';
import type {
  AuthResponse,
  Event,
  EventCreatePayload,
  Participant,
  AvailabilitySubmission,
  EventDashboard,
  TimeRecommendation,
  ShareInfo,
  CalendarExport,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Axios instance
const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear tokens
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  register: async (email: string, password: string, nickname: string): Promise<AuthResponse> => {
    const { data } = await api.post<AuthResponse>('/auth/register/', {
      email,
      password,
      nickname,
    });
    return data;
  },

  login: async (email: string, password: string): Promise<AuthResponse> => {
    const { data } = await api.post<AuthResponse>('/auth/login/', {
      email,
      password,
    });
    return data;
  },

  getMe: async () => {
    const { data } = await api.get('/auth/me/');
    return data;
  },
};

// Event API
export const eventApi = {
  create: async (payload: EventCreatePayload): Promise<Event> => {
    const { data } = await api.post<Event>('/events/', payload);
    return data;
  },

  getBySlug: async (slug: string): Promise<Event> => {
    const { data } = await api.get<Event>(`/events/${slug}/`);
    return data;
  },

  getMyEvents: async (page: number = 1, pageSize: number = 10) => {
    const { data } = await api.get('/events/my/', {
      params: { page, page_size: pageSize },
    });
    return data;
  },

  update: async (id: number, payload: Partial<EventCreatePayload>): Promise<Event> => {
    const { data } = await api.patch<Event>(`/events/${id}/`, payload);
    return data;
  },

  setFinalChoice: async (eventId: number, slotId: number) => {
    const { data } = await api.post(`/events/${eventId}/final-choice`, {
      slot_id: slotId,
    });
    return data;
  },

  sendFinalEmail: async (eventId: number) => {
    const { data } = await api.post(`/events/${eventId}/final-choice/send-email`);
    return data;
  },

  getRecommendation: async (
    eventId: number,
    limit: number = 5,
    minParticipants?: number
  ): Promise<TimeRecommendation> => {
    const { data } = await api.get<TimeRecommendation>(`/events/${eventId}/recommend-time`, {
      params: { limit, min_participants: minParticipants },
    });
    return data;
  },

  getDashboard: async (
    eventId: number,
    participantId?: number,
    email?: string
  ): Promise<EventDashboard> => {
    const { data } = await api.get<EventDashboard>(`/events/${eventId}/dashboard`, {
      params: participantId && email ? { participant_id: participantId, email } : undefined,
    });
    return data;
  },

  getShareInfo: async (eventId: number): Promise<ShareInfo> => {
    const { data } = await api.get<ShareInfo>(`/events/${eventId}/share-info`);
    return data;
  },

  sendInviteEmails: async (eventId: number, emails: string[], message?: string) => {
    const { data } = await api.post(`/events/${eventId}/invite`, {
      emails,
      message,
    });
    return data;
  },

  getCalendarExport: async (eventId: number): Promise<CalendarExport> => {
    const { data } = await api.get<CalendarExport>(`/events/${eventId}/calendar-export`);
    return data;
  },
};

// Participant API
export const participantApi = {
  create: async (slug: string, nickname: string, email?: string): Promise<Participant> => {
    const { data } = await api.post<Participant>(`/events/${slug}/participants/`, {
      nickname,
      email,
    });
    return data;
  },

  list: async (eventId: number) => {
    const { data } = await api.get(`/events/${eventId}/participants`);
    return data;
  },

  submitAvailability: async (participantId: number, payload: AvailabilitySubmission) => {
    const { data } = await api.post(`/participants/${participantId}/availability/`, payload);
    return data;
  },
};

// QR Code API
export const qrCodeApi = {
  getQRCodeUrl: (eventId: number, size: number = 10): string => {
    return `${API_URL}/api/v1/events/${eventId}/qr-code?size=${size}`;
  },
};

// Calendar API
export const calendarApi = {
  getICSUrl: (eventId: number): string => {
    return `${API_URL}/api/v1/events/${eventId}/calendar.ics`;
  },
};

export default api;
