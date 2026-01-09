'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import Button from '../ui/Button';

export default function Header() {
  const router = useRouter();
  const { user, isAuthenticated, clearAuth } = useAuthStore();

  const handleLogout = () => {
    clearAuth();
    router.push('/');
  };

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-2xl">🍕</span>
          <span className="text-xl font-bold text-gray-900">
            Pizza Scheduler
          </span>
        </Link>

        <nav className="flex items-center space-x-4">
          {isAuthenticated() ? (
            <>
              <span className="text-sm text-gray-600 hidden md:inline">
                안녕하세요, <strong>{user?.nickname}</strong>님
              </span>
              <Link href="/events/create">
                <Button variant="primary" size="sm">
                  이벤트 만들기
                </Button>
              </Link>
              <Link href="/events/my">
                <Button variant="ghost" size="sm">
                  내 이벤트
                </Button>
              </Link>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                로그아웃
              </Button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  로그인
                </Button>
              </Link>
              <Link href="/register">
                <Button variant="primary" size="sm">
                  회원가입
                </Button>
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
