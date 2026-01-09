import Link from 'next/link';
import { Calendar, Users, Clock, Zap } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            🍕 Pizza Scheduler
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            친구들과 함께 일정을 조율하고 최적의 시간을 찾아보세요
          </p>

          <div className="flex gap-4 justify-center">
            <Link
              href="/events/create"
              className="px-8 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition"
            >
              이벤트 만들기
            </Link>
            <Link
              href="/login"
              className="px-8 py-3 border-2 border-primary-600 text-primary-600 rounded-lg font-semibold hover:bg-primary-50 transition"
            >
              로그인
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-24 grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <FeatureCard
            icon={<Calendar className="w-8 h-8 text-primary-600" />}
            title="간편한 일정 생성"
            description="몇 번의 클릭으로 일정 조율을 시작하세요"
          />
          <FeatureCard
            icon={<Users className="w-8 h-8 text-primary-600" />}
            title="익명 참가 가능"
            description="회원가입 없이도 일정에 참여할 수 있어요"
          />
          <FeatureCard
            icon={<Clock className="w-8 h-8 text-primary-600" />}
            title="실시간 현황 확인"
            description="누가 언제 가능한지 실시간으로 확인하세요"
          />
          <FeatureCard
            icon={<Zap className="w-8 h-8 text-primary-600" />}
            title="자동 시간 추천"
            description="가장 많은 사람이 가능한 시간을 추천해드려요"
          />
        </div>

        {/* How it works */}
        <div className="mt-24">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            사용 방법
          </h2>
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
      </div>

      {/* Footer */}
      <footer className="mt-24 py-8 border-t border-gray-200">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>© 2026 Pizza Scheduler. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}

function StepCard({ number, title, description }: { number: number; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}
