'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { participantApi } from '@/lib/api';
import { getErrorMessage, formatDate, formatDateTime } from '@/lib/utils';
import Button from '@/components/ui/Button';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Clock, Check, X } from 'lucide-react';
import type { TimeSlot, Participant } from '@/types';

interface Props {
  participant: Participant;
  timeSlots: TimeSlot[];
  onSuccess?: () => void;
}

interface GroupedSlots {
  [date: string]: TimeSlot[];
}

export default function TimeSlotSelector({ participant, timeSlots, onSuccess }: Props) {
  const [selectedSlots, setSelectedSlots] = useState<Set<number>>(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [groupedSlots, setGroupedSlots] = useState<GroupedSlots>({});

  // Group slots by date
  useEffect(() => {
    const grouped: GroupedSlots = {};
    timeSlots.forEach((slot) => {
      // Handle both API formats: { start_datetime } or { date, start_time }
      const slotAny = slot as any;
      const date = slot.start_datetime
        ? slot.start_datetime.split('T')[0]
        : slotAny.date;

      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(slot);
    });
    setGroupedSlots(grouped);
  }, [timeSlots]);

  const toggleSlot = (slotId: number) => {
    const newSelected = new Set(selectedSlots);
    if (newSelected.has(slotId)) {
      newSelected.delete(slotId);
    } else {
      newSelected.add(slotId);
    }
    setSelectedSlots(newSelected);
  };

  const selectAll = () => {
    setSelectedSlots(new Set(timeSlots.map((slot) => (slot.id || (slot as any).slot_id))));
  };

  const clearAll = () => {
    setSelectedSlots(new Set());
  };

  const handleSubmit = async () => {
    if (selectedSlots.size === 0) {
      toast.error('최소 1개 이상의 시간대를 선택해주세요');
      return;
    }

    setIsLoading(true);
    try {
      const availabilities = timeSlots.map((slot) => {
        const slotId = slot.id || (slot as any).slot_id;
        return {
          time_slot_id: slotId,
          is_available: selectedSlots.has(slotId),
        };
      });

      await participantApi.submitAvailability(participant.id, {
        availabilities,
      });

      toast.success('가능 시간을 제출했습니다! ✅');
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              가능한 시간 선택
            </h2>
          </div>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={selectAll}
              type="button"
            >
              <Check className="w-4 h-4 mr-1" />
              전체 선택
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAll}
              type="button"
            >
              <X className="w-4 h-4 mr-1" />
              전체 해제
            </Button>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          참가 가능한 시간대를 모두 선택해주세요 (선택: {selectedSlots.size}개)
        </p>
      </CardHeader>
      <CardBody>
        <div className="space-y-6">
          {Object.entries(groupedSlots).map(([date, slots]) => (
            <div key={date}>
              <h3 className="font-semibold text-gray-900 mb-3">
                {formatDate(date, 'M월 d일 (E)')}
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                {slots.map((slot) => {
                  const slotAny = slot as any;
                  const slotId = slot.id || slotAny.slot_id;
                  const isSelected = selectedSlots.has(slotId);

                  // Handle both API formats
                  let startTime: string;
                  if (slot.start_datetime) {
                    startTime = new Date(slot.start_datetime)
                      .toLocaleTimeString('ko-KR', {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false,
                      });
                  } else {
                    startTime = slotAny.start_time;
                  }

                  return (
                    <button
                      key={slotId}
                      type="button"
                      onClick={() => toggleSlot(slotId)}
                      className={`
                        px-3 py-2 rounded-lg border-2 text-sm font-medium transition
                        ${
                          isSelected
                            ? 'bg-primary-600 border-primary-600 text-white'
                            : 'bg-white border-gray-300 text-gray-700 hover:border-primary-300'
                        }
                      `}
                    >
                      {startTime}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <Button
            variant="primary"
            className="w-full"
            onClick={handleSubmit}
            isLoading={isLoading}
            disabled={selectedSlots.size === 0}
          >
            제출하기 ({selectedSlots.size}개 선택됨)
          </Button>
        </div>

        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-900">
            💡 <strong>팁:</strong> 가능한 시간을 많이 선택할수록 다른 참가자와
            일정을 맞추기 쉬워집니다!
          </p>
        </div>
      </CardBody>
    </Card>
  );
}
