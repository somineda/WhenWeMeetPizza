import Link from 'next/link';
import { Calendar, Users, Clock, Zap, ArrowRight, Sparkles } from 'lucide-react';
import Header from '@/components/layout/Header';
import Button from '@/components/ui/Button';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-warm">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background decorations */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200/30 rounded-full blur-3xl" />
        <div className="absolute top-40 right-10 w-96 h-96 bg-amber-200/30 rounded-full blur-3xl" />

        <div className="container mx-auto px-4 py-20 relative">
          <div className="text-center max-w-4xl mx-auto animate-fade-in">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-medium mb-8">
              <Sparkles className="w-4 h-4" />
              <span>쉽고 빠른 일정 조율</span>
            </div>

            {/* Main Title */}
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              <span className="inline-block animate-float">🍕</span>
              <br />
              <span className="gradient-text">모두가 가능한 시간</span>을<br />
              찾아드립니다
            </h1>

            <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              친구들, 동료들과 함께 일정을 조율하고
              <br className="hidden md:block" />
              <strong className="text-gray-800">최적의 시간</strong>을 쉽게 찾아보세요
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/events/create">
                <Button variant="gradient" size="lg" className="shadow-glow">
                  <span>이벤트 만들기</span>
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="outline" size="lg">
                  로그인하기
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              왜 <span className="gradient-text">핏자 팟</span>인가요?
            </h2>
            <p className="text-gray-600 text-lg">
              복잡한 일정 조율을 간단하게 만들어 드립니다
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            <FeatureCard
              icon={<Calendar className="w-7 h-7" />}
              title="간편한 일정 생성"
              description="몇 번의 클릭으로 일정 조율을 시작하세요"
              color="orange"
            />
            <FeatureCard
              icon={<Users className="w-7 h-7" />}
              title="익명 참가 가능"
              description="회원가입 없이도 일정에 참여할 수 있어요"
              color="blue"
            />
            <FeatureCard
              icon={<Clock className="w-7 h-7" />}
              title="실시간 현황"
              description="누가 언제 가능한지 실시간으로 확인하세요"
              color="green"
            />
            <FeatureCard
              icon={<Zap className="w-7 h-7" />}
              title="자동 시간 추천"
              description="가장 많은 사람이 가능한 시간을 추천해드려요"
              color="purple"
            />
          </div>
        </div>
      </section>

      {/* How it works Section */}
      <section className="py-24">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              이렇게 사용하세요
            </h2>
            <p className="text-gray-600 text-lg">
              3단계로 간편하게 일정을 조율할 수 있어요
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <StepCard
              number={1}
              title="이벤트 생성"
              description="일정 제목과 가능한 날짜/시간을 입력하세요"
            />
            <StepCard
              number={2}
              title="링크 공유"
              description="생성된 링크를 친구들에게 공유하세요"
            />
            <StepCard
              number={3}
              title="시간 확정"
              description="모두의 일정을 확인하고 최적의 시간을 선택하세요"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-500 to-primary-600">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            지금 바로 시작해보세요
          </h2>
          <p className="text-primary-100 text-lg mb-8 max-w-2xl mx-auto">
            복잡한 카카오톡 설문 대신, 클릭 몇 번으로 일정을 조율하세요
          </p>
          <Link href="/events/create">
            <Button
              variant="secondary"
              size="lg"
              className="bg-white text-primary-600 hover:bg-gray-50 shadow-soft-lg"
            >
              <span>무료로 시작하기</span>
              <ArrowRight className="w-5 h-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-gray-50 border-t border-gray-100">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="text-2xl">🍕</span>
            <span className="font-semibold text-gray-900">핏자 팟</span>
          </div>
          <p className="text-sm">© 2026 핏자 팟. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  color,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: 'orange' | 'blue' | 'green' | 'purple';
}) {
  const colorClasses = {
    orange: 'bg-primary-100 text-primary-600',
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-emerald-100 text-emerald-600',
    purple: 'bg-purple-100 text-purple-600',
  };

  return (
    <div className="p-6 bg-white rounded-2xl shadow-soft hover:shadow-soft-lg hover:-translate-y-1 transition-all duration-300 group">
      <div
        className={`w-14 h-14 ${colorClasses[color]} rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}
      >
        {icon}
      </div>
      <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm leading-relaxed">{description}</p>
    </div>
  );
}

function StepCard({
  number,
  title,
  description,
}: {
  number: number;
  title: string;
  description: string;
}) {
  return (
    <div className="text-center group">
      <div className="relative inline-block mb-6">
        <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold shadow-glow group-hover:scale-110 transition-transform">
          {number}
        </div>
        {number < 3 && (
          <div className="hidden md:block absolute top-1/2 left-full w-full h-0.5 bg-gradient-to-r from-primary-300 to-transparent -translate-y-1/2 ml-4" />
        )}
      </div>
      <h3 className="text-xl font-bold text-gray-900 mb-3">{title}</h3>
      <p className="text-gray-600 leading-relaxed">{description}</p>
    </div>
  );
}
