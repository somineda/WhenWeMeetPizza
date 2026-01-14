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
import { ArrowLeft, BarChart3, CheckCircle2, Lightbulb } from 'lucide-react';
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

  useEffect(() => {
    const fetchEvent = async () => {
      setIsLoading(true);
      try {
        const eventData = await eventApi.getBySlug(slug);
        setEvent(eventData);

        const savedParticipant = getParticipant();
        if (savedParticipant && savedParticipant.slug === slug) {
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
      <div className="min-h-screen bg-gradient-warm">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mb-4"></div>
          <p className="text-gray-600">로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-gradient-warm">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl">🔍</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            이벤트를 찾을 수 없습니다
          </h1>
          <p className="text-gray-600 mb-8">
            이벤트가 삭제되었거나 잘못된 링크입니다
          </p>
          <Link href="/">
            <Button variant="gradient" size="lg">홈으로 돌아가기</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-warm">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto animate-fade-in">
          {/* Navigation */}
          <div className="mb-6 flex items-center justify-between">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4" />
                <span>홈으로</span>
              </Button>
            </Link>

            {(isCreator || participant) && (
              <Link href={`/e/${slug}/dashboard`}>
                <Button variant="outline" size="sm">
                  <BarChart3 className="w-4 h-4" />
                  <span>대시보드</span>
                </Button>
              </Link>
            )}
          </div>

          {/* Final Choice Banner */}
          {event.final_choice && (
            <div className="mb-6 p-6 bg-emerald-50 border-2 border-emerald-200 rounded-2xl">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <CheckCircle2 className="w-6 h-6 text-emerald-600" />
                </div>
                <div>
                  <h3 className="font-bold text-emerald-900">최종 시간이 확정되었습니다!</h3>
                  <p className="text-emerald-700 mt-1">
                    📅{' '}
                    {new Date(event.final_choice.slot.start_datetime).toLocaleString('ko-KR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            </div>
          )}

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
              <div className="mt-8">
                <div className="flex items-center justify-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm transition-all ${
                      step === 'register'
                        ? 'bg-primary-500 text-white shadow-glow'
                        : 'bg-primary-100 text-primary-600'
                    }`}
                  >
                    1
                  </div>
                  <div className="w-12 h-1 bg-gray-200 rounded-full">
                    <div
                      className={`h-full rounded-full transition-all ${
                        step === 'select' ? 'w-full bg-primary-500' : 'w-0'
                      }`}
                    />
                  </div>
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm transition-all ${
                      step === 'select'
                        ? 'bg-primary-500 text-white shadow-glow'
                        : 'bg-gray-100 text-gray-400'
                    }`}
                  >
                    2
                  </div>
                </div>
                <div className="mt-3 text-center text-sm text-gray-600">
                  {step === 'register' ? '1단계: 참가 등록' : '2단계: 시간 선택'}
                </div>
              </div>
            </div>
          </div>

          {/* Help Text */}
          {!event.final_choice && (
            <div className="mt-8 p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-soft">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Lightbulb className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 mb-3">이렇게 진행됩니다</h3>
                  <ol className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-center gap-2">
                      <span className="w-5 h-5 bg-primary-100 text-primary-700 rounded-md flex items-center justify-center text-xs font-bold">1</span>
                      닉네임과 이메일을 입력하여 참가 등록
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-5 h-5 bg-primary-100 text-primary-700 rounded-md flex items-center justify-center text-xs font-bold">2</span>
                      가능한 시간대를 모두 선택
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-5 h-5 bg-primary-100 text-primary-700 rounded-md flex items-center justify-center text-xs font-bold">3</span>
                      주최자가 참가 현황을 확인
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-5 h-5 bg-primary-100 text-primary-700 rounded-md flex items-center justify-center text-xs font-bold">4</span>
                      가장 많은 사람이 가능한 시간으로 최종 확정
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-5 h-5 bg-primary-100 text-primary-700 rounded-md flex items-center justify-center text-xs font-bold">5</span>
                      확정 알림 이메일/SMS 수신
                    </li>
                  </ol>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
