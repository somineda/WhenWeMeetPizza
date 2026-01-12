'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { getErrorMessage } from '@/lib/utils';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';

// Validation schema
const registerSchema = z
  .object({
    email: z
      .string()
      .min(1, '이메일을 입력해주세요')
      .email('올바른 이메일 형식이 아닙니다'),
    nickname: z
      .string()
      .min(1, '닉네임을 입력해주세요')
      .min(2, '닉네임은 최소 2자 이상이어야 합니다')
      .max(20, '닉네임은 최대 20자까지 가능합니다'),
    password: z
      .string()
      .min(1, '비밀번호를 입력해주세요')
      .min(6, '비밀번호는 최소 6자 이상이어야 합니다')
      .max(128, '비밀번호는 최대 128자까지 가능합니다'),
    confirmPassword: z.string().min(1, '비밀번호 확인을 입력해주세요'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: '비밀번호가 일치하지 않습니다',
    path: ['confirmPassword'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    try {
      const response = await authApi.register(
        data.email,
        data.password,
        data.confirmPassword,
        data.nickname
      );

      // Save auth state
      setAuth(
        {
          id: response.id,
          email: response.email,
          nickname: response.nickname,
        },
        response.tokens.access,
        response.tokens.refresh
      );

      toast.success('회원가입 완료! 환영합니다 🎉');

      // Redirect to home or create event page
      router.push('/events/create');
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2">
            <span className="text-4xl">🍕</span>
            <span className="text-2xl font-bold text-gray-900">
              Pizza Scheduler
            </span>
          </Link>
          <p className="mt-2 text-gray-600">새 계정을 만드세요</p>
        </div>

        {/* Register Form */}
        <Card>
          <CardHeader>
            <h1 className="text-2xl font-bold text-gray-900">회원가입</h1>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input
                label="이메일"
                type="email"
                placeholder="example@email.com"
                error={errors.email?.message}
                {...register('email')}
              />

              <Input
                label="닉네임"
                type="text"
                placeholder="홍길동"
                helperText="다른 사람에게 표시될 이름입니다"
                error={errors.nickname?.message}
                {...register('nickname')}
              />

              <Input
                label="비밀번호"
                type="password"
                placeholder="••••••••"
                helperText="최소 6자 이상"
                error={errors.password?.message}
                {...register('password')}
              />

              <Input
                label="비밀번호 확인"
                type="password"
                placeholder="••••••••"
                error={errors.confirmPassword?.message}
                {...register('confirmPassword')}
              />

              <Button
                type="submit"
                variant="primary"
                className="w-full"
                isLoading={isLoading}
              >
                회원가입
              </Button>
            </form>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">또는</span>
              </div>
            </div>

            {/* Login Link */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                이미 계정이 있으신가요?{' '}
                <Link
                  href="/login"
                  className="font-semibold text-primary-600 hover:text-primary-700"
                >
                  로그인
                </Link>
              </p>
            </div>

            {/* Privacy Notice */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-600">
                회원가입을 진행하시면{' '}
                <a href="#" className="text-primary-600 hover:underline">
                  이용약관
                </a>
                과{' '}
                <a href="#" className="text-primary-600 hover:underline">
                  개인정보처리방침
                </a>
                에 동의하는 것으로 간주됩니다.
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link
            href="/"
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            ← 홈으로 돌아가기
          </Link>
        </div>
      </div>
    </div>
  );
}
