'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { eventApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { getErrorMessage, formatDate, getShareUrl } from '@/lib/utils';
import Button from '@/components/ui/Button';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import Header from '@/components/layout/Header';
import { Calendar, Users, Clock, Plus, ExternalLink } from 'lucide-react';
import type { Event } from '@/types';

export default function MyEventsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  // Check authentication
  useEffect(() => {
    if (!isAuthenticated()) {
      toast.error('로그인이 필요합니다');
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Fetch events
  useEffect(() => {
    if (!isAuthenticated()) return;

    const fetchEvents = async () => {
      setIsLoading(true);
      try {
        const response = await eventApi.getMyEvents(page, 10);
        setEvents(response.results);
        setHasMore(response.next !== null);
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        toast.error(errorMessage);
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
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Page Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                내 이벤트
              </h1>
              <p className="text-gray-600">
                내가 만든 일정 조율 이벤트 목록입니다
              </p>
            </div>
            <Link href="/events/create">
              <Button variant="primary">
                <Plus className="w-4 h-4 mr-2" />
                새 이벤트
              </Button>
            </Link>
          </div>

          {/* Events List */}
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              <p className="mt-4 text-gray-600">로딩 중...</p>
            </div>
          ) : events.length === 0 ? (
            <Card>
              <CardBody className="text-center py-12">
                <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  아직 이벤트가 없습니다
                </h3>
                <p className="text-gray-600 mb-6">
                  첫 번째 일정 조율 이벤트를 만들어보세요!
                </p>
                <Link href="/events/create">
                  <Button variant="primary">
                    <Plus className="w-4 h-4 mr-2" />
                    이벤트 만들기
                  </Button>
                </Link>
              </CardBody>
            </Card>
          ) : (
            <div className="space-y-4">
              {events.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}

              {/* Pagination */}
              {hasMore && (
                <div className="text-center pt-4">
                  <Button
                    variant="outline"
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

function EventCard({ event }: { event: Event }) {
  const shareUrl = getShareUrl(event.slug);

  return (
    <Card className="hover:shadow-md transition">
      <CardBody>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <Link href={`/e/${event.slug}`}>
              <h3 className="text-xl font-semibold text-gray-900 hover:text-primary-600 transition">
                {event.title}
              </h3>
            </Link>
            {event.description && (
              <p className="text-gray-600 mt-1 line-clamp-2">
                {event.description}
              </p>
            )}

            <div className="flex flex-wrap gap-4 mt-4 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4" />
                <span>
                  {formatDate(event.date_start, 'M월 d일')} ~{' '}
                  {formatDate(event.date_end, 'M월 d일')}
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>
                  {event.time_start} ~ {event.time_end}
                </span>
              </div>

              {event.participants_count !== undefined && (
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4" />
                  <span>{event.participants_count}명 참가</span>
                </div>
              )}
            </div>

            {event.final_choice && (
              <div className="mt-3 inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                ✅ 최종 시간 확정됨
              </div>
            )}
          </div>

          <div className="flex flex-col gap-2 ml-4">
            <Link href={`/e/${event.slug}`} target="_blank">
              <Button variant="outline" size="sm">
                <ExternalLink className="w-4 h-4 mr-1" />
                보기
              </Button>
            </Link>
            <Link href={`/e/${event.slug}/dashboard`}>
              <Button variant="ghost" size="sm">
                대시보드
              </Button>
            </Link>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
