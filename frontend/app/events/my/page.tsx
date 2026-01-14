'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { eventApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { getErrorMessage, formatDate } from '@/lib/utils';
import Button from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import Header from '@/components/layout/Header';
import { Calendar, Users, Clock, Plus, Trash2, Eye, BarChart3, CheckCircle2 } from 'lucide-react';
import type { Event } from '@/types';

export default function MyEventsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      toast.error('로그인이 필요합니다');
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    if (!isAuthenticated()) return;

    const fetchEvents = async () => {
      setIsLoading(true);
      try {
        const response = await eventApi.getMyEvents(page, 10);
        setEvents(response.items || []);
        setHasMore((response.page * response.size) < response.total);
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        toast.error(errorMessage);
        setEvents([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvents();
  }, [isAuthenticated, page]);

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-warm">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto animate-fade-in">
          {/* Page Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                내 이벤트
              </h1>
              <p className="text-gray-600">
                내가 만든 일정 조율 이벤트 목록입니다
              </p>
            </div>
            <Link href="/events/create">
              <Button variant="gradient" size="lg">
                <Plus className="w-5 h-5" />
                <span>새 이벤트</span>
              </Button>
            </Link>
          </div>

          {/* Events List */}
          {isLoading ? (
            <div className="text-center py-16">
              <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-primary-500 mb-4"></div>
              <p className="text-gray-600">로딩 중...</p>
            </div>
          ) : !events || events.length === 0 ? (
            <Card className="shadow-soft-lg">
              <CardBody className="text-center py-16">
                <div className="w-20 h-20 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Calendar className="w-10 h-10 text-primary-500" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  아직 이벤트가 없습니다
                </h3>
                <p className="text-gray-600 mb-8">
                  첫 번째 일정 조율 이벤트를 만들어보세요!
                </p>
                <Link href="/events/create">
                  <Button variant="gradient" size="lg">
                    <Plus className="w-5 h-5" />
                    <span>이벤트 만들기</span>
                  </Button>
                </Link>
              </CardBody>
            </Card>
          ) : (
            <div className="space-y-4">
              {events.map((event) => (
                <EventCard
                  key={event.id}
                  event={event}
                  onDelete={(id) => setEvents(events.filter(e => e.id !== id))}
                />
              ))}

              {/* Pagination */}
              {hasMore && (
                <div className="text-center pt-6">
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => setPage((p) => p + 1)}
                  >
                    더 보기
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function EventCard({ event, onDelete }: { event: Event; onDelete: (id: number) => void }) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm(`'${event.title}' 이벤트를 삭제하시겠습니까?\n\n삭제된 이벤트는 복구할 수 없습니다.`)) {
      return;
    }

    setIsDeleting(true);
    try {
      await eventApi.delete(event.id);
      toast.success('이벤트가 삭제되었습니다');
      onDelete(event.id);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Card className="shadow-soft hover:shadow-soft-lg transition-all duration-300">
      <CardBody>
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <Link href={`/e/${event.slug}`}>
              <h3 className="text-xl font-bold text-gray-900 hover:text-primary-600 transition-colors truncate">
                {event.title}
              </h3>
            </Link>
            {event.description && (
              <p className="text-gray-600 mt-1 line-clamp-2">
                {event.description}
              </p>
            )}

            <div className="flex flex-wrap gap-4 mt-4 text-sm text-gray-500">
              {event.date_start && event.date_end && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-primary-500" />
                  <span>
                    {formatDate(event.date_start, 'M월 d일')} ~{' '}
                    {formatDate(event.date_end, 'M월 d일')}
                  </span>
                </div>
              )}

              {event.time_start && event.time_end && (
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-primary-500" />
                  <span>
                    {event.time_start} ~ {event.time_end}
                  </span>
                </div>
              )}

              {(event.participants_count !== undefined || (event as any).participant_count !== undefined) && (
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-primary-500" />
                  <span>{event.participants_count || (event as any).participant_count}명 참가</span>
                </div>
              )}
            </div>

            {event.final_choice && (
              <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium">
                <CheckCircle2 className="w-4 h-4" />
                최종 시간 확정됨
              </div>
            )}
          </div>

          <div className="flex md:flex-col gap-2 flex-shrink-0">
            <Link href={`/e/${event.slug}`}>
              <Button variant="outline" size="sm" className="w-full">
                <Eye className="w-4 h-4" />
                <span>보기</span>
              </Button>
            </Link>
            <Link href={`/e/${event.slug}/dashboard`}>
              <Button variant="ghost" size="sm" className="w-full">
                <BarChart3 className="w-4 h-4" />
                <span>대시보드</span>
              </Button>
            </Link>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              isLoading={isDeleting}
              className="text-rose-600 hover:text-rose-700 hover:bg-rose-50"
            >
              <Trash2 className="w-4 h-4" />
              <span>삭제</span>
            </Button>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
