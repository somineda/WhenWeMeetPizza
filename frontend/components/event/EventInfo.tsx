'use client';

import { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import toast from 'react-hot-toast';
import { copyToClipboard, formatDate, getShareUrl } from '@/lib/utils';
import { qrCodeApi } from '@/lib/api';
import Button from '@/components/ui/Button';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import {
  Calendar,
  Clock,
  Globe,
  Share2,
  Copy,
  Check,
  QrCode,
  Users,
} from 'lucide-react';
import type { Event } from '@/types';

interface Props {
  event: Event;
}

export default function EventInfo({ event }: Props) {
  const [showQR, setShowQR] = useState(false);
  const [copied, setCopied] = useState(false);
  const shareUrl = getShareUrl(event.slug);

  const handleCopyLink = async () => {
    const success = await copyToClipboard(shareUrl);
    if (success) {
      setCopied(true);
      toast.success('링크가 복사되었습니다!');
      setTimeout(() => setCopied(false), 2000);
    } else {
      toast.error('링크 복사에 실패했습니다');
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: event.title,
          text: event.description,
          url: shareUrl,
        });
      } catch (error) {
        // User cancelled or error occurred
      }
    } else {
      handleCopyLink();
    }
  };

  return (
    <div className="space-y-4">
      {/* Event Details */}
      <Card>
        <CardBody>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {event.title}
          </h1>
          {event.description && (
            <p className="text-gray-600 mb-6">{event.description}</p>
          )}

          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="font-medium text-gray-900">날짜</div>
                <div className="text-gray-600">
                  {formatDate(event.date_start, 'yyyy년 M월 d일')} ~{' '}
                  {formatDate(event.date_end, 'yyyy년 M월 d일')}
                </div>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <Clock className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="font-medium text-gray-900">시간</div>
                <div className="text-gray-600">
                  {event.time_start} ~ {event.time_end}
                </div>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <Globe className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="font-medium text-gray-900">타임존</div>
                <div className="text-gray-600">{event.timezone}</div>
              </div>
            </div>

            {event.participants_count !== undefined && (
              <div className="flex items-start space-x-3">
                <Users className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <div className="font-medium text-gray-900">참가자</div>
                  <div className="text-gray-600">
                    {event.participants_count}명
                  </div>
                </div>
              </div>
            )}
          </div>

          {event.final_choice && (
            <div className="mt-6 p-4 bg-green-50 border-2 border-green-200 rounded-lg">
              <div className="flex items-center space-x-2 text-green-800 font-semibold mb-2">
                <Check className="w-5 h-5" />
                <span>최종 시간이 확정되었습니다!</span>
              </div>
              <div className="text-green-700">
                📅{' '}
                {new Date(
                  event.final_choice.slot.start_datetime
                ).toLocaleString('ko-KR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}{' '}
                ~{' '}
                {new Date(event.final_choice.slot.end_datetime).toLocaleString(
                  'ko-KR',
                  {
                    hour: '2-digit',
                    minute: '2-digit',
                  }
                )}
              </div>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Share Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Share2 className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">공유하기</h2>
          </div>
        </CardHeader>
        <CardBody>
          <div className="space-y-3">
            {/* Share URL */}
            <div className="flex gap-2">
              <input
                type="text"
                value={shareUrl}
                readOnly
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm"
              />
              <Button
                variant="outline"
                onClick={handleCopyLink}
                className="flex-shrink-0"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 mr-1" />
                    복사됨
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 mr-1" />
                    복사
                  </>
                )}
              </Button>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button
                variant="primary"
                onClick={handleShare}
                className="flex-1"
              >
                <Share2 className="w-4 h-4 mr-1" />
                공유하기
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowQR(!showQR)}
                className="flex-1"
              >
                <QrCode className="w-4 h-4 mr-1" />
                QR 코드
              </Button>
            </div>

            {/* QR Code */}
            {showQR && (
              <div className="flex justify-center p-4 bg-white border-2 border-gray-200 rounded-lg">
                <QRCodeSVG value={shareUrl} size={200} />
              </div>
            )}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
