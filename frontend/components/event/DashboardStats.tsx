'use client';

import { Card, CardBody } from '@/components/ui/Card';
import { Users, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import { formatDateTimeKorean } from '@/lib/utils';
import type { DashboardStats as StatsType } from '@/types';

interface Props {
  stats: StatsType;
}

export default function DashboardStats({ stats }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Participants */}
      <Card>
        <CardBody>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">전체 참가자</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.total_participants}명
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Submitted */}
      <Card>
        <CardBody>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">제출 완료</p>
              <p className="text-2xl font-bold text-green-600">
                {stats.submitted_participants}명
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Pending */}
      <Card>
        <CardBody>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">제출 대기</p>
              <p className="text-2xl font-bold text-orange-600">
                {stats.pending_participants}명
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Clock className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Submission Rate */}
      <Card>
        <CardBody>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">제출률</p>
              <p className="text-2xl font-bold text-primary-600">
                {stats.submission_rate}%
              </p>
            </div>
            <div className="p-3 bg-primary-100 rounded-full">
              <TrendingUp className="w-6 h-6 text-primary-600" />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Most Popular Slot */}
      {stats.most_popular_slot && (
        <Card className="md:col-span-2 lg:col-span-4">
          <CardBody>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">
                  ⭐ 가장 인기 있는 시간
                </p>
                <p className="text-xl font-semibold text-gray-900">
                  {formatDateTimeKorean(
                    stats.most_popular_slot.start_datetime_local
                  )}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">가능 인원</p>
                <p className="text-2xl font-bold text-green-600">
                  {stats.most_popular_slot.available_count}명
                </p>
                <p className="text-sm text-gray-600">
                  ({stats.most_popular_slot.availability_rate}%)
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
