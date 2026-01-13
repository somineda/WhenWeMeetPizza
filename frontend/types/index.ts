// User Types
export interface User {
  id: number;
  email: string;
  nickname: string;
}

export interface AuthResponse {
  user: {
    id: number;
    email: string;
    nickname: string;
  };
  tokens: {
    access: string;
    refresh: string;
  };
}

// Event Types
export interface TimeSlot {
  id: number;
  start_datetime: string;
  end_datetime: string;
}

export interface Event {
  id: number;
  title: string;
  slug: string;
  description: string;
  date_start: string;
  date_end: string;
  time_start: string;
  time_end: string;
  timezone: string;
  created_by: number | { id: number; nickname: string };
  created_at: string;
  time_slots?: TimeSlot[];
  participants_count?: number;
  final_choice?: FinalChoice;
}

export interface EventCreatePayload {
  title: string;
  description: string;
  date_start: string;
  date_end: string;
  time_start: string;
  time_end: string;
  timezone: string;
}

export interface FinalChoice {
  id: number;
  slot: TimeSlot;
  chosen_by: {
    id: number;
    nickname: string;
  };
  created_at: string;
}

// Participant Types
export interface Participant {
  id: number;
  nickname: string;
  email: string;
  phone?: string;
  is_registered: boolean;
  created_at: string;
}

export interface ParticipantAvailability {
  time_slot_id: number;
  is_available: boolean;
}

export interface AvailabilitySubmission {
  available_slot_ids: number[];
}

// Dashboard Types
export interface ParticipantStatus {
  participant_id: number;
  nickname: string;
  email: string | null;
  is_registered: boolean;
  has_submitted: boolean;
  submitted_slots_count: number;
  joined_at: string;
}

export interface HeatmapSlot {
  slot_id: number;
  start_datetime: string;
  end_datetime: string;
  start_datetime_local: string;
  end_datetime_local: string;
  available_count: number;
  available_participants: { participant_id: number; nickname: string }[];
  availability_rate: number;
}

export interface DashboardStats {
  total_participants: number;
  submitted_participants: number;
  pending_participants: number;
  submission_rate: number;
  total_time_slots: number;
  most_popular_slot: {
    slot_id: number;
    start_datetime_local: string;
    available_count: number;
    availability_rate: number;
  } | null;
}

export interface EventDashboard {
  event_id: number;
  event_title: string;
  stats: DashboardStats;
  participants: ParticipantStatus[];
  heatmap: HeatmapSlot[];
}

// Recommendation Types
export interface RecommendedSlot {
  slot_id: number;
  start_datetime: string;
  end_datetime: string;
  start_datetime_local: string;
  end_datetime_local: string;
  available_count: number;
  total_participants: number;
  available_percentage: number;
  available_participants: string[];
}

export interface TimeRecommendation {
  event_id: number;
  event_title: string;
  total_participants: number;
  total_time_slots: number;
  recommended_slots: RecommendedSlot[];
  message: string;
}

// Share Types
export interface ShareInfo {
  event_id: number;
  event_title: string;
  event_slug: string;
  share_url: string;
  qr_code_url: string;
  kakao_title: string;
  kakao_description: string;
  kakao_image_url: string | null;
  kakao_template: any;
  email_subject: string;
  email_body: string;
}

// Calendar Export Types
export interface CalendarExport {
  event_id: number;
  event_title: string;
  has_final_choice: boolean;
  final_start_datetime: string | null;
  final_end_datetime: string | null;
  final_start_datetime_local: string | null;
  final_end_datetime_local: string | null;
  google_calendar_url: string | null;
  ics_download_url: string;
  message: string;
}
