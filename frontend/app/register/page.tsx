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
import { Mail, Lock, User, ShieldCheck } from 'lucide-react';

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

      setAuth({
        id: response.user.id,
        email: response.user.email,
        nickname: response.user.nickname,
      });

      toast.success('회원가입 완료! 환영합니다 🎉');
      router.push('/events/create');
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
      <div className="absolute top-10 right-20 w-72 h-72 bg-amber-200/30 rounded-full blur-3xl" />
      <div className="absolute bottom-10 left-10 w-96 h-96 bg-primary-200/30 rounded-full blur-3xl" />

      <div className="w-full max-w-md relative animate-fade-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 group">
            <span className="text-5xl group-hover:animate-float transition-transform">🍕</span>
            <span className="text-2xl font-bold text-gray-900">
              핏자 팟
            </span>
          </Link>
          <p className="mt-3 text-gray-600">새 계정을 만드세요</p>
        </div>

        {/* Register Form */}
        <Card className="shadow-soft-lg">
          <CardHeader className="text-center border-b-0 pb-0">
            <h1 className="text-2xl font-bold text-gray-900">회원가입</h1>
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
                label="닉네임"
                type="text"
                placeholder="홍길동"
                icon={<User className="w-5 h-5" />}
                helperText="다른 사람에게 표시될 이름입니다"
                error={errors.nickname?.message}
                {...register('nickname')}
              />

              <Input
                label="비밀번호"
                type="password"
                placeholder="••••••••"
                icon={<Lock className="w-5 h-5" />}
                helperText="최소 6자 이상"
                error={errors.password?.message}
                {...register('password')}
              />

              <Input
                label="비밀번호 확인"
                type="password"
                placeholder="••••••••"
                icon={<ShieldCheck className="w-5 h-5" />}
                error={errors.confirmPassword?.message}
                {...register('confirmPassword')}
              />

              <Button
                type="submit"
                variant="gradient"
                className="w-full"
                size="lg"
                isLoading={isLoading}
              >
                회원가입
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

            {/* Login Link */}
            <div className="text-center">
              <p className="text-gray-600">
                이미 계정이 있으신가요?{' '}
                <Link
                  href="/login"
                  className="font-semibold text-primary-600 hover:text-primary-700 underline-offset-4 hover:underline"
                >
                  로그인
                </Link>
              </p>
            </div>

            {/* Privacy Notice */}
            <div className="mt-8 p-4 bg-gray-50 rounded-xl">
              <p className="text-xs text-gray-600 text-center leading-relaxed">
                회원가입을 진행하시면{' '}
                <a href="#" className="text-primary-600 hover:underline font-medium">
                  이용약관
                </a>
                과{' '}
                <a href="#" className="text-primary-600 hover:underline font-medium">
                  개인정보처리방침
                </a>
                에 동의하는 것으로 간주됩니다.
              </p>
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
