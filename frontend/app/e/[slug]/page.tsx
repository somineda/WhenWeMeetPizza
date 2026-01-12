'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { eventApi } from '@/lib/api';
import { useAuthStore, useParticipantStore } from '@/lib/store';
import { getErrorMessage } from '@/lib/utils';
import Button from '@/components/ui/Button';
import Header from '@/components/layout/Header';
import EventInfo from '@/components/event/EventInfo';
import ParticipantRegistration from '@/components/event/ParticipantRegistration';
import TimeSlotSelector from '@/components/event/TimeSlotSelector';
import { ArrowLeft, BarChart3 } from 'lucide-react';
import type { Event, Participant } from '@/types';

export default function EventDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const { isAuthenticated, user } = useAuthStore();
  const { getParticipant } = useParticipantStore();
  const [event, setEvent] = useState<Event | null>(null);
  const [participant, setParticipant] = useState<Participant | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [step, setStep] = useState<'register' | 'select'>('register');

  // Fetch event data
  useEffect(() => {
    const fetchEvent = async () => {
      setIsLoading(true);
      try {
        const eventData = await eventApi.getBySlug(slug);
        setEvent(eventData);

        // Check if user already participated
        const savedParticipant = getParticipant();
        if (savedParticipant && savedParticipant.slug === slug) {
          // User already registered for this event
          setParticipant({
            id: savedParticipant.id,
            nickname: savedParticipant.nickname,
            email: savedParticipant.email,
          } as Participant);
          setStep('select');
        }
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvent();
  }, [slug, getParticipant]);

  const handleParticipantSuccess = (newParticipant: Participant) => {
    setParticipant(newParticipant);
    setStep('select');
  };

  const handleTimeSlotSuccess = () => {
    toast.success('제출이 완료되었습니다!');
    // Refresh event data
    const fetchEvent = async () => {
      try {
        const eventData = await eventApi.getBySlug(slug);
        setEvent(eventData);
      } catch (error) {
        // Ignore error
      }
    };
    fetchEvent();
  };

  const isCreator = isAuthenticated() && event && user && (
    event.created_by === user.id ||
    (event as any).organizer_id === user.id
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            이벤트를 찾을 수 없습니다
          </h1>
          <p className="text-gray-600 mb-6">
            이벤트가 삭제되었거나 잘못된 링크입니다
          </p>
          <Link href="/">
            <Button variant="primary">홈으로 돌아가기</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Back Button */}
          <div className="mb-6 flex items-center justify-between">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-1" />
                홈으로
              </Button>
            </Link>

            {(isCreator || participant) && (
              <Link href={`/e/${slug}/dashboard`}>
                <Button variant="outline" size="sm">
                  <BarChart3 className="w-4 h-4 mr-1" />
                  대시보드
                </Button>
              </Link>
            )}
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Left Column - Event Info */}
            <div>
              <EventInfo event={event} />
            </div>

            {/* Right Column - Participation */}
            <div>
              {step === 'register' ? (
                <ParticipantRegistration
                  eventSlug={slug}
                  onSuccess={handleParticipantSuccess}
                />
              ) : participant && (event.time_slots || (event as any).slots) ? (
                <TimeSlotSelector
                  participant={participant}
                  timeSlots={event.time_slots || (event as any).slots}
                  onSuccess={handleTimeSlotSuccess}
                />
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-600">
                    참가자 정보를 불러오는 중...
                  </p>
                </div>
              )}

              {/* Steps Indicator */}
              <div className="mt-6 flex items-center justify-center space-x-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    step === 'register' ? 'bg-primary-600' : 'bg-gray-300'
                  }`}
                />
                <div className="w-8 h-0.5 bg-gray-300" />
                <div
                  className={`w-3 h-3 rounded-full ${
                    step === 'select' ? 'bg-primary-600' : 'bg-gray-300'
                  }`}
                />
              </div>
              <div className="mt-2 text-center text-sm text-gray-600">
                {step === 'register' ? '1단계: 참가 등록' : '2단계: 시간 선택'}
              </div>
            </div>
          </div>

          {/* Help Text */}
          {!event.final_choice && (
            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">
                💡 이렇게 진행됩니다
              </h3>
              <ol className="space-y-1 text-sm text-blue-800 list-decimal list-inside">
                <li>닉네임과 이메일을 입력하여 참가 등록</li>
                <li>가능한 시간대를 모두 선택</li>
                <li>주최자가 참가 현황을 확인</li>
                <li>가장 많은 사람이 가능한 시간으로 최종 확정</li>
                <li>확정 알림 이메일 수신</li>
              </ol>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
