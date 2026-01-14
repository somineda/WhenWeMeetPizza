import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  setAuth: (user: User) => void;
  clearAuth: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      setAuth: (user) => {
        set({ user });
      },
      clearAuth: () => {
        set({ user: null });
      },
      isAuthenticated: () => {
        const state = get();
        return !!state.user;
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);

// Participant Store (for anonymous participants)
interface ParticipantState {
  participantId: number | null;
  participantEmail: string | null;
  participantNickname: string | null;
  eventSlug: string | null;
  setParticipant: (id: number, email: string, nickname: string, slug: string) => void;
  clearParticipant: () => void;
  getParticipant: () => { id: number; email: string; nickname: string; slug: string } | null;
}

export const useParticipantStore = create<ParticipantState>()(
  persist(
    (set, get) => ({
      participantId: null,
      participantEmail: null,
      participantNickname: null,
      eventSlug: null,
      setParticipant: (id, email, nickname, slug) => {
        set({
          participantId: id,
          participantEmail: email,
          participantNickname: nickname,
          eventSlug: slug,
        });
      },
      clearParticipant: () => {
        set({
          participantId: null,
          participantEmail: null,
          participantNickname: null,
          eventSlug: null,
        });
      },
      getParticipant: () => {
        const state = get();
        if (state.participantId && state.participantEmail && state.participantNickname && state.eventSlug) {
          return {
            id: state.participantId,
            email: state.participantEmail,
            nickname: state.participantNickname,
            slug: state.eventSlug,
          };
        }
        return null;
      },
    }),
    {
      name: 'participant-storage',
    }
  )
);
