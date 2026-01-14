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
import { Mail, Lock, Sparkles } from 'lucide-react';

const loginSchema = z.object({
  email: z
    .string()
    .min(1, '이메일을 입력해주세요')
    .email('올바른 이메일 형식이 아닙니다'),
  password: z
    .string()
    .min(1, '비밀번호를 입력해주세요')
    .min(6, '비밀번호는 최소 6자 이상이어야 합니다'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      const response = await authApi.login(data.email, data.password);
      setAuth(
        {
          id: response.user.id,
          email: response.user.email,
          nickname: response.user.nickname,
        },
        response.tokens.access,
        response.tokens.refresh
      );
      toast.success('로그인 성공!');
      router.push('/events/my');
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-warm flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200/30 rounded-full blur-3xl" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-amber-200/30 rounded-full blur-3xl" />

      <div className="w-full max-w-md relative animate-fade-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 group">
            <span className="text-5xl group-hover:animate-float transition-transform">🍕</span>
            <span className="text-2xl font-bold text-gray-900">
              Pizza Scheduler
            </span>
          </Link>
          <p className="mt-3 text-gray-600">계정에 로그인하세요</p>
        </div>

        {/* Login Form */}
        <Card className="shadow-soft-lg">
          <CardHeader className="text-center border-b-0 pb-0">
            <h1 className="text-2xl font-bold text-gray-900">로그인</h1>
          </CardHeader>
          <CardBody className="pt-2">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              <Input
                label="이메일"
                type="email"
                placeholder="example@email.com"
                icon={<Mail className="w-5 h-5" />}
                error={errors.email?.message}
                {...register('email')}
              />

              <Input
                label="비밀번호"
                type="password"
                placeholder="••••••••"
                icon={<Lock className="w-5 h-5" />}
                error={errors.password?.message}
                {...register('password')}
              />

              <Button
                type="submit"
                variant="gradient"
                className="w-full"
                size="lg"
                isLoading={isLoading}
              >
                로그인
              </Button>
            </form>

            {/* Divider */}
            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">또는</span>
              </div>
            </div>

            {/* Register Link */}
            <div className="text-center">
              <p className="text-gray-600">
                계정이 없으신가요?{' '}
                <Link
                  href="/register"
                  className="font-semibold text-primary-600 hover:text-primary-700 underline-offset-4 hover:underline"
                >
                  회원가입
                </Link>
              </p>
            </div>

            {/* Guest Access Info */}
            <div className="mt-8 p-4 bg-primary-50 rounded-xl border border-primary-100">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-primary-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-primary-900">
                    익명 참가 가능
                  </p>
                  <p className="text-sm text-primary-700 mt-1">
                    회원가입 없이도 공유받은 링크로 바로 참가할 수 있어요!
                  </p>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Back to Home */}
        <div className="mt-8 text-center">
          <Link
            href="/"
            className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
          >
            ← 홈으로 돌아가기
          </Link>
        </div>
      </div>
    </div>
  );
}
