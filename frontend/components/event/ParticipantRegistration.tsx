'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { participantApi } from '@/lib/api';
import { useAuthStore, useParticipantStore } from '@/lib/store';
import { getErrorMessage } from '@/lib/utils';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { UserPlus } from 'lucide-react';
import type { Participant } from '@/types';

// Validation schema
const participantSchema = z.object({
  nickname: z
    .string()
    .min(1, '닉네임을 입력해주세요')
    .min(2, '닉네임은 최소 2자 이상이어야 합니다')
    .max(20, '닉네임은 최대 20자까지 가능합니다'),
  email: z
    .string()
    .min(1, '이메일을 입력해주세요')
    .email('올바른 이메일 형식이 아닙니다')
    .optional()
    .or(z.literal('')),
});

type ParticipantFormData = z.infer<typeof participantSchema>;

interface Props {
  eventSlug: string;
  onSuccess: (participant: Participant) => void;
}

export default function ParticipantRegistration({ eventSlug, onSuccess }: Props) {
  const { isAuthenticated, user } = useAuthStore();
  const { setParticipant } = useParticipantStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ParticipantFormData>({
    resolver: zodResolver(participantSchema),
    defaultValues: {
      nickname: user?.nickname || '',
      email: user?.email || '',
    },
  });

  const onSubmit = async (data: ParticipantFormData) => {
    setIsLoading(true);
    try {
      const participant = await participantApi.create(
        eventSlug,
        data.nickname,
        data.email || undefined
      );

      // Save participant info for anonymous users
      if (!isAuthenticated()) {
        setParticipant(
          participant.id,
          participant.email,
          participant.nickname,
          eventSlug
        );
      }

      toast.success('참가 등록이 완료되었습니다! 🎉');
      onSuccess(participant);
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
        <div className="flex items-center space-x-2">
          <UserPlus className="w-5 h-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">
            일정에 참가하기
          </h2>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          {isAuthenticated()
            ? '가능한 시간을 선택하려면 먼저 참가 등록을 해주세요'
            : '회원가입 없이도 참가할 수 있습니다'}
        </p>
      </CardHeader>
      <CardBody>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="닉네임"
            type="text"
            placeholder="홍길동"
            helperText="다른 참가자에게 표시될 이름입니다"
            error={errors.nickname?.message}
            disabled={isAuthenticated()}
            {...register('nickname')}
          />

          <Input
            label={isAuthenticated() ? '이메일' : '이메일 (선택)'}
            type="email"
            placeholder="example@email.com"
            helperText={
              isAuthenticated()
                ? '회원 이메일이 사용됩니다'
                : '확정 알림을 받고 싶다면 입력하세요'
            }
            error={errors.email?.message}
            disabled={isAuthenticated()}
            {...register('email')}
          />

          <Button
            type="submit"
            variant="primary"
            className="w-full"
            isLoading={isLoading}
          >
            참가 등록하기
          </Button>

          {!isAuthenticated() && (
            <div className="text-center text-sm text-gray-600">
              회원이신가요?{' '}
              <a
                href="/login"
                className="font-semibold text-primary-600 hover:text-primary-700"
              >
                로그인
              </a>
            </div>
          )}
        </form>
      </CardBody>
    </Card>
  );
}
