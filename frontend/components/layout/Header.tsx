'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import Button from '../ui/Button';
import { Menu, X } from 'lucide-react';

export default function Header() {
  const router = useRouter();
  const { user, isAuthenticated, clearAuth } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    setMounted(true);

    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    clearAuth();
    router.push('/');
  };

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-white/80 backdrop-blur-lg shadow-soft'
          : 'bg-white/50 backdrop-blur-sm'
      }`}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2 group">
            <span className="text-3xl group-hover:animate-float">🍕</span>
            <span className="text-xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
              Pizza Scheduler
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-3">
            {!mounted ? (
              <>
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    로그인
                  </Button>
                </Link>
                <Link href="/register">
                  <Button variant="gradient" size="sm">
                    회원가입
                  </Button>
                </Link>
              </>
            ) : isAuthenticated() ? (
              <>
                <span className="text-sm text-gray-600 px-3 py-2 bg-primary-50 rounded-full">
                  👋 <strong className="text-primary-700">{user?.nickname}</strong>님
                </span>
                <Link href="/events/create">
                  <Button variant="gradient" size="sm">
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
                  <Button variant="gradient" size="sm">
                    회원가입
                  </Button>
                </Link>
              </>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 rounded-xl hover:bg-gray-100 transition-colors"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6 text-gray-700" />
            ) : (
              <Menu className="w-6 h-6 text-gray-700" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <nav className="md:hidden mt-4 pb-4 border-t border-gray-100 pt-4 space-y-2 animate-fade-in">
            {mounted && isAuthenticated() ? (
              <>
                <div className="text-sm text-gray-600 px-4 py-3 bg-primary-50 rounded-xl mb-3">
                  👋 안녕하세요, <strong className="text-primary-700">{user?.nickname}</strong>님
                </div>
                <Link href="/events/create" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="gradient" className="w-full justify-center">
                    이벤트 만들기
                  </Button>
                </Link>
                <Link href="/events/my" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="ghost" className="w-full justify-center">
                    내 이벤트
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  className="w-full justify-center"
                  onClick={() => {
                    handleLogout();
                    setMobileMenuOpen(false);
                  }}
                >
                  로그아웃
                </Button>
              </>
            ) : (
              <>
                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="ghost" className="w-full justify-center">
                    로그인
                  </Button>
                </Link>
                <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="gradient" className="w-full justify-center">
                    회원가입
                  </Button>
                </Link>
              </>
            )}
          </nav>
        )}
      </div>
    </header>
  );
}
