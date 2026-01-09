'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { eventApi } from '@/lib/api';
import { getErrorMessage, formatDateTimeKorean } from '@/lib/utils';
import Button from '@/components/ui/Button';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { CheckCircle, Mail, Clock } from 'lucide-react';
import type { HeatmapSlot, RecommendedSlot } from '@/types';

interface Props {
  eventId: number;
  heatmap: HeatmapSlot[];
  recommendedSlots?: RecommendedSlot[];
  onSuccess?: () => void;
}

export default function FinalChoiceSelector({
  eventId,
  heatmap,
  recommendedSlots,
  onSuccess,
}: Props) {
  const [selectedSlotId, setSelectedSlotId] = useState<number | null>(null);
  const [isConfirming, setIsConfirming] = useState(false);
  const [isSendingEmail, setIsSendingEmail] = useState(false);

  // Get top slots sorted by availability
  const topSlots = [...heatmap]
    .sort((a, b) => b.available_count - a.available_count)
    .slice(0, 5);

  const handleConfirm = async () => {
    if (!selectedSlotId) {
      toast.error('시간을 선택해주세요');
      return;
    }

    if (!confirm('이 시간으로 최종 확정하시겠습니까?')) {
      return;
    }

    setIsConfirming(true);
    try {
      await eventApi.setFinalChoice(eventId, selectedSlotId);
      toast.success('최종 시간이 확정되었습니다! 🎉');
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    } finally {
      setIsConfirming(false);
    }
  };

  const handleSendEmail = async () => {
    if (!confirm('모든 참가자에게 확정 알림을 발송하시겠습니까?')) {
      return;
    }

    setIsSendingEmail(true);
    try {
      const response = await eventApi.sendFinalEmail(eventId);
      toast.success(response.message);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    } finally {
      setIsSendingEmail(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              최종 시간 선택
            </h2>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleSendEmail}
            isLoading={isSendingEmail}
            disabled={!selectedSlotId}
          >
            <Mail className="w-4 h-4 mr-1" />
            알림 발송
          </Button>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          가장 많은 사람이 가능한 시간을 확인하고 최종 확정하세요
        </p>
      </CardHeader>
      <CardBody>
        {/* Recommended Slots */}
        <div className="space-y-3">
          <h3 className="font-medium text-gray-900">추천 시간대 (상위 5개)</h3>
          <div className="space-y-2">
            {topSlots.map((slot, index) => {
              const isSelected = selectedSlotId === slot.slot_id;
              const participants = slot.available_participants
                .map((p) => p.nickname)
                .join(', ');

              return (
                <button
                  key={slot.slot_id}
                  onClick={() => setSelectedSlotId(slot.slot_id)}
                  className={`
                    w-full p-4 rounded-lg border-2 text-left transition
                    ${
                      isSelected
                        ? 'border-primary-600 bg-primary-50'
                        : 'border-gray-200 hover:border-primary-300'
                    }
                  `}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        {index === 0 && (
                          <span className="text-lg">🥇</span>
                        )}
                        {index === 1 && (
                          <span className="text-lg">🥈</span>
                        )}
                        {index === 2 && (
                          <span className="text-lg">🥉</span>
                        )}
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="font-semibold text-gray-900">
                          {formatDateTimeKorean(slot.start_datetime_local)}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-600 mt-2">
                        <span className="font-medium text-green-600">
                          {slot.available_count}명 가능
                        </span>
                        <span>({slot.availability_rate}%)</span>
                      </div>
                      {participants && (
                        <div className="mt-2 text-sm text-gray-600">
                          <span className="font-medium">참가자:</span>{' '}
                          {participants}
                        </div>
                      )}
                    </div>
                    {isSelected && (
                      <CheckCircle className="w-6 h-6 text-primary-600 flex-shrink-0" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Confirm Button */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <Button
            variant="primary"
            className="w-full"
            onClick={handleConfirm}
            isLoading={isConfirming}
            disabled={!selectedSlotId}
          >
            최종 확정하기
          </Button>
          {selectedSlotId && (
            <p className="text-center text-sm text-gray-600 mt-2">
              선택한 시간으로 최종 확정됩니다
            </p>
          )}
        </div>

        {/* Warning */}
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-900">
            ⚠️ <strong>주의:</strong> 최종 확정 후에는 변경할 수 없습니다.
            신중하게 선택해주세요.
          </p>
        </div>
      </CardBody>
    </Card>
  );
}
