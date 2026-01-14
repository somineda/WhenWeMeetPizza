'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { eventApi } from '@/lib/api';
import { useAuthStore, useParticipantStore } from '@/lib/store';
import { getErrorMessage } from '@/lib/utils';
import Button from '@/components/ui/Button';
import Header from '@/components/layout/Header';
import DashboardStats from '@/components/event/DashboardStats';
import ParticipantsTable from '@/components/event/ParticipantsTable';
import HeatmapChart from '@/components/event/HeatmapChart';
import FinalChoiceSelector from '@/components/event/FinalChoiceSelector';
import { Card, CardBody } from '@/components/ui/Card';
import { ArrowLeft, ExternalLink, RefreshCw, PartyPopper, Send, Lightbulb } from 'lucide-react';
import type { EventDashboard, Event } from '@/types';

export default function DashboardPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;
  const { isAuthenticated, user } = useAuthStore();
  const { getParticipant } = useParticipantStore();
  const [dashboard, setDashboard] = useState<EventDashboard | null>(null);
  const [event, setEvent] = useState<Event | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSlotId, setSelectedSlotId] = useState<number | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const eventData = await eventApi.getBySlug(slug);
      setEvent(eventData);

      const isCreator = isAuthenticated() && user && (
        eventData.created_by === user.id ||
        (eventData as any).organizer_id === user.id
      );
      const savedParticipant = getParticipant();

      let dashboardData: EventDashboard;

      if (isCreator) {
        dashboardData = await eventApi.getDashboard(eventData.id);
      } else if (savedParticipant && savedParticipant.slug === slug) {
        dashboardData = await eventApi.getDashboard(
          eventData.id,
          savedParticipant.id,
          savedParticipant.email
        );
      } else {
        toast.error('대시보드에 접근할 권한이 없습니다');
        router.push(`/e/${slug}`);
        return;
      }

      setDashboard(dashboardData);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
      router.push(`/e/${slug}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [slug]);

  const handleRefresh = () => {
    fetchData();
    toast.success('새로고침 완료');
  };

  const handleSlotClick = (slotId: number) => {
    setSelectedSlotId(slotId);
    const slot = dashboard?.heatmap.find((s) => s.slot_id === slotId);
    if (slot) {
      const participants = slot.available_participants
        .map((p) => p.nickname)
        .join(', ');
      toast(
        <div>
          <div className="font-semibold">가능한 참가자 ({slot.available_count}명)</div>
          <div className="text-sm mt-1">{participants || '없음'}</div>
        </div>,
        { duration: 4000 }
      );
    }
  };

  const handleFinalChoiceSuccess = () => {
    fetchData();
  };

  const isCreator =
    isAuthenticated() && event && user && (
      event.created_by === user.id ||
      (event as any).organizer_id === user.id
    );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-warm">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mb-4"></div>
          <p className="text-gray-600">대시보드 로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!dashboard || !event) {
    return (
      <div className="min-h-screen bg-gradient-warm">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl">🔒</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            대시보드를 불러올 수 없습니다
          </h1>
          <p className="text-gray-600 mb-8">권한이 없거나 잘못된 접근입니다</p>
          <Link href={`/e/${slug}`}>
            <Button variant="gradient" size="lg">이벤트로 돌아가기</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-warm">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto animate-fade-in">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
            <div className="flex items-center gap-4">
              <Link href={`/e/${slug}`}>
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4" />
                  <span>이벤트로</span>
                </Button>
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {dashboard.event_title}
                </h1>
                <p className="text-sm text-gray-600">참가 현황 대시보드</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={handleRefresh}>
                <RefreshCw className="w-4 h-4" />
                <span>새로고침</span>
              </Button>
              <Link href={`/e/${slug}`} target="_blank">
                <Button variant="outline" size="sm">
                  <ExternalLink className="w-4 h-4" />
                  <span>이벤트 보기</span>
                </Button>
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="mb-8">
            <DashboardStats stats={dashboard.stats} />
          </div>

          {/* Main Content */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-6">
              {/* Participants Table */}
              <ParticipantsTable participants={dashboard.participants} />

              {/* Additional Info */}
              {!event.final_choice && dashboard.stats.submission_rate < 100 && (
                <Card className="bg-blue-50 border-blue-100">
                  <CardBody>
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Lightbulb className="w-4 h-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-blue-900">
                          아직 {dashboard.stats.pending_participants}명이 시간을 제출하지 않았습니다
                        </p>
                        <p className="text-sm text-blue-700 mt-1">
                          제출률이 높을수록 더 정확한 일정 조율이 가능합니다
                        </p>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* Heatmap */}
              <HeatmapChart
                heatmap={dashboard.heatmap}
                onSlotClick={handleSlotClick}
              />

              {/* Final Choice Selector (Creator Only) */}
              {isCreator && !event.final_choice && (
                <FinalChoiceSelector
                  eventId={event.id}
                  heatmap={dashboard.heatmap}
                  onSuccess={handleFinalChoiceSuccess}
                />
              )}

              {/* Final Choice Confirmed */}
              {event.final_choice && (
                <Card className="overflow-hidden">
                  <CardBody className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-2 border-emerald-200">
                    <div className="text-center py-4">
                      <div className="w-16 h-16 bg-emerald-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <PartyPopper className="w-8 h-8 text-emerald-700" />
                      </div>
                      <h3 className="text-xl font-bold text-emerald-900 mb-2">
                        최종 시간이 확정되었습니다!
                      </h3>
                      <p className="text-emerald-700 text-lg mb-6">
                        📅{' '}
                        {new Date(
                          event.final_choice.slot.start_datetime
                        ).toLocaleString('ko-KR', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                      {isCreator && (
                        <Button
                          variant="gradient"
                          onClick={async () => {
                            try {
                              const response = await eventApi.sendFinalEmail(
                                event.id
                              );
                              toast.success(response.message);
                            } catch (error) {
                              toast.error(getErrorMessage(error));
                            }
                          }}
                        >
                          <Send className="w-4 h-4" />
                          <span>확정 알림 발송</span>
                        </Button>
                      )}
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
