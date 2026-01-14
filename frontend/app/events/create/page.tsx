'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { eventApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { getErrorMessage } from '@/lib/utils';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import { Card, CardBody } from '@/components/ui/Card';
import Header from '@/components/layout/Header';
import { Calendar, Clock, Globe, ArrowRight, FileText, Lightbulb } from 'lucide-react';

const TIMEZONE_OPTIONS = [
  { value: 'Asia/Seoul', label: '한국 (서울)' },
  { value: 'Asia/Tokyo', label: '일본 (도쿄)' },
  { value: 'Asia/Shanghai', label: '중국 (상하이)' },
  { value: 'Asia/Hong_Kong', label: '홍콩' },
  { value: 'Asia/Singapore', label: '싱가포르' },
  { value: 'America/New_York', label: '미국 동부 (뉴욕)' },
  { value: 'America/Los_Angeles', label: '미국 서부 (LA)' },
  { value: 'Europe/London', label: '영국 (런던)' },
  { value: 'Europe/Paris', label: '프랑스 (파리)' },
  { value: 'UTC', label: 'UTC' },
];

const eventSchema = z
  .object({
    title: z
      .string()
      .min(1, '제목을 입력해주세요')
      .max(100, '제목은 최대 100자까지 가능합니다'),
    description: z
      .string()
      .max(500, '설명은 최대 500자까지 가능합니다')
      .optional(),
    date_start: z.string().min(1, '시작 날짜를 선택해주세요'),
    date_end: z.string().min(1, '종료 날짜를 선택해주세요'),
    time_start: z.string().min(1, '시작 시간을 선택해주세요'),
    time_end: z.string().min(1, '종료 시간을 선택해주세요'),
    timezone: z.string().min(1, '타임존을 선택해주세요'),
  })
  .refine(
    (data) => {
      const start = new Date(data.date_start);
      const end = new Date(data.date_end);
      return start <= end;
    },
    {
      message: '종료 날짜는 시작 날짜보다 이후여야 합니다',
      path: ['date_end'],
    }
  )
  .refine(
    (data) => {
      if (data.date_start === data.date_end) {
        const [startHour, startMin] = data.time_start.split(':').map(Number);
        const [endHour, endMin] = data.time_end.split(':').map(Number);
        const startMinutes = startHour * 60 + startMin;
        const endMinutes = endHour * 60 + endMin;
        return startMinutes < endMinutes;
      }
      return true;
    },
    {
      message: '종료 시간은 시작 시간보다 이후여야 합니다',
      path: ['time_end'],
    }
  );

type EventFormData = z.infer<typeof eventSchema>;

export default function CreateEventPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      toast.error('로그인이 필요합니다');
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const today = new Date().toISOString().split('T')[0];

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<EventFormData>({
    resolver: zodResolver(eventSchema),
    defaultValues: {
      timezone: 'Asia/Seoul',
      date_start: today,
      date_end: today,
      time_start: '14:00',
      time_end: '16:00',
    },
  });

  const dateStart = watch('date_start');

  const onSubmit = async (data: EventFormData) => {
    setIsLoading(true);
    try {
      const event = await eventApi.create({
        title: data.title,
        description: data.description || '',
        date_start: data.date_start,
        date_end: data.date_end,
        time_start: data.time_start,
        time_end: data.time_end,
        timezone: data.timezone,
      });

      toast.success('이벤트가 생성되었습니다! 🎉');
      router.push(`/e/${event.slug}`);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-warm">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto animate-fade-in">
          {/* Page Header */}
          <div className="mb-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-2xl mb-4">
              <Calendar className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              새 이벤트 만들기
            </h1>
            <p className="text-gray-600">
              친구들과 일정을 조율할 이벤트를 만들어보세요
            </p>
          </div>

          {/* Form Card */}
          <Card className="shadow-soft-lg">
            <CardBody className="p-8">
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
                {/* Basic Information */}
                <div className="space-y-5">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
                      <FileText className="w-5 h-5 text-primary-600" />
                    </div>
                    <h2 className="text-lg font-bold text-gray-900">기본 정보</h2>
                  </div>

                  <Input
                    label="이벤트 제목"
                    type="text"
                    placeholder="피자 파티 일정 조율"
                    error={errors.title?.message}
                    {...register('title')}
                  />

                  <Textarea
                    label="설명 (선택)"
                    placeholder="맛있는 피자를 먹으며 즐거운 시간을 보내요!"
                    rows={3}
                    error={errors.description?.message}
                    helperText="이벤트에 대한 간단한 설명을 입력하세요"
                    {...register('description')}
                  />
                </div>

                {/* Date Range */}
                <div className="space-y-5">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                      <Calendar className="w-5 h-5 text-blue-600" />
                    </div>
                    <h2 className="text-lg font-bold text-gray-900">날짜 범위</h2>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <Input
                      label="시작 날짜"
                      type="date"
                      min={today}
                      error={errors.date_start?.message}
                      {...register('date_start')}
                    />

                    <Input
                      label="종료 날짜"
                      type="date"
                      min={dateStart || today}
                      error={errors.date_end?.message}
                      {...register('date_end')}
                    />
                  </div>

                  <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-xl">
                    <Lightbulb className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-blue-800">
                      선택한 날짜 범위 동안 30분 단위로 타임슬롯이 자동 생성됩니다
                    </p>
                  </div>
                </div>

                {/* Time Range */}
                <div className="space-y-5">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
                      <Clock className="w-5 h-5 text-emerald-600" />
                    </div>
                    <h2 className="text-lg font-bold text-gray-900">시간 범위</h2>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <Input
                      label="시작 시간"
                      type="time"
                      error={errors.time_start?.message}
                      {...register('time_start')}
                    />

                    <Input
                      label="종료 시간"
                      type="time"
                      error={errors.time_end?.message}
                      {...register('time_end')}
                    />
                  </div>

                  <div className="flex items-start gap-3 p-4 bg-emerald-50 rounded-xl">
                    <Lightbulb className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-emerald-800">
                      매일 이 시간 범위 내에서 타임슬롯이 생성됩니다
                    </p>
                  </div>
                </div>

                {/* Timezone */}
                <div className="space-y-5">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                      <Globe className="w-5 h-5 text-purple-600" />
                    </div>
                    <h2 className="text-lg font-bold text-gray-900">타임존</h2>
                  </div>

                  <Select
                    label="타임존 선택"
                    options={TIMEZONE_OPTIONS}
                    error={errors.timezone?.message}
                    {...register('timezone')}
                  />
                </div>

                {/* Submit Button */}
                <div className="pt-6 border-t border-gray-100">
                  <div className="flex gap-4">
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => router.back()}
                      className="flex-1"
                      size="lg"
                    >
                      취소
                    </Button>
                    <Button
                      type="submit"
                      variant="gradient"
                      isLoading={isLoading}
                      className="flex-1"
                      size="lg"
                    >
                      <span>이벤트 만들기</span>
                      <ArrowRight className="w-5 h-5" />
                    </Button>
                  </div>
                </div>
              </form>
            </CardBody>
          </Card>

          {/* Help Text */}
          <div className="mt-8 p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-soft">
            <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-xl">📋</span>
              다음 단계는?
            </h3>
            <ol className="space-y-3 text-sm text-gray-600">
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-primary-100 text-primary-700 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0">1</span>
                <span>이벤트를 만들면 공유 링크가 생성됩니다</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-primary-100 text-primary-700 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0">2</span>
                <span>링크를 친구들에게 공유하세요</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-primary-100 text-primary-700 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0">3</span>
                <span>친구들이 가능한 시간을 선택합니다</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-primary-100 text-primary-700 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0">4</span>
                <span>대시보드에서 결과를 확인하고 최종 시간을 선택하세요</span>
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
