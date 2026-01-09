'use client';

import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { BarChart3 } from 'lucide-react';
import { formatDate, formatDateTime } from '@/lib/utils';
import type { HeatmapSlot } from '@/types';

interface Props {
  heatmap: HeatmapSlot[];
  onSlotClick?: (slotId: number) => void;
}

interface GroupedHeatmap {
  [date: string]: HeatmapSlot[];
}

export default function HeatmapChart({ heatmap, onSlotClick }: Props) {
  // Group by date
  const groupedHeatmap: GroupedHeatmap = {};
  heatmap.forEach((slot) => {
    const date = slot.start_datetime_local.split('T')[0];
    if (!groupedHeatmap[date]) {
      groupedHeatmap[date] = [];
    }
    groupedHeatmap[date].push(slot);
  });

  const getColorClass = (rate: number) => {
    if (rate >= 80) return 'bg-green-500 hover:bg-green-600';
    if (rate >= 60) return 'bg-green-400 hover:bg-green-500';
    if (rate >= 40) return 'bg-yellow-400 hover:bg-yellow-500';
    if (rate >= 20) return 'bg-orange-400 hover:bg-orange-500';
    return 'bg-red-400 hover:bg-red-500';
  };

  const getTextColorClass = (rate: number) => {
    if (rate >= 80) return 'text-green-700';
    if (rate >= 60) return 'text-green-600';
    if (rate >= 40) return 'text-yellow-700';
    if (rate >= 20) return 'text-orange-700';
    return 'text-red-700';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">
            시간대별 가능 인원 (히트맵)
          </h2>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          색이 진할수록 더 많은 사람이 가능한 시간입니다
        </p>
      </CardHeader>
      <CardBody>
        <div className="space-y-6">
          {Object.entries(groupedHeatmap).map(([date, slots]) => (
            <div key={date}>
              <h3 className="font-semibold text-gray-900 mb-3">
                {formatDate(date, 'M월 d일 (E)')}
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
                {slots.map((slot) => {
                  const time = new Date(slot.start_datetime_local)
                    .toLocaleTimeString('ko-KR', {
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: false,
                    });

                  return (
                    <button
                      key={slot.slot_id}
                      onClick={() => onSlotClick && onSlotClick(slot.slot_id)}
                      className={`
                        relative p-3 rounded-lg transition cursor-pointer
                        ${getColorClass(slot.availability_rate)}
                        ${onSlotClick ? 'hover:scale-105' : ''}
                      `}
                      title={`${slot.available_count}명 가능 (${slot.availability_rate}%)`}
                    >
                      <div className="text-white font-semibold text-sm">
                        {time}
                      </div>
                      <div className="text-white text-xs mt-1">
                        {slot.available_count}명
                      </div>
                      <div className="text-white text-xs opacity-90">
                        {slot.availability_rate}%
                      </div>

                      {/* Tooltip on hover */}
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap z-10">
                        {slot.available_participants.length > 0 ? (
                          slot.available_participants
                            .map((p) => p.nickname)
                            .join(', ')
                        ) : (
                          '없음'
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-400 rounded"></div>
              <span className="text-gray-600">0-20%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-orange-400 rounded"></div>
              <span className="text-gray-600">20-40%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-400 rounded"></div>
              <span className="text-gray-600">40-60%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-400 rounded"></div>
              <span className="text-gray-600">60-80%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span className="text-gray-600">80-100%</span>
            </div>
          </div>
        </div>

        {/* Participants List for Selected Slot */}
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-900">
            💡 <strong>팁:</strong> 시간대를 클릭하면 해당 시간에 가능한
            참가자를 확인할 수 있습니다
          </p>
        </div>
      </CardBody>
    </Card>
  );
}
