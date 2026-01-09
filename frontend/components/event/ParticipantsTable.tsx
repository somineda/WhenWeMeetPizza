'use client';

import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Users, CheckCircle, Clock, Mail, User } from 'lucide-react';
import { formatDateTime } from '@/lib/utils';
import type { ParticipantStatus } from '@/types';

interface Props {
  participants: ParticipantStatus[];
}

export default function ParticipantsTable({ participants }: Props) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center space-x-2">
          <Users className="w-5 h-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">참가자 현황</h2>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          총 {participants.length}명의 참가자
        </p>
      </CardHeader>
      <CardBody>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  상태
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  닉네임
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  유형
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 hidden md:table-cell">
                  이메일
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-900">
                  제출 시간
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 hidden lg:table-cell">
                  참가 시각
                </th>
              </tr>
            </thead>
            <tbody>
              {participants.map((participant) => (
                <tr
                  key={participant.participant_id}
                  className="border-b border-gray-100 hover:bg-gray-50 transition"
                >
                  <td className="px-4 py-3">
                    {participant.has_submitted ? (
                      <div className="flex items-center space-x-1 text-green-600">
                        <CheckCircle className="w-5 h-5" />
                        <span className="text-sm font-medium hidden sm:inline">
                          완료
                        </span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-1 text-orange-600">
                        <Clock className="w-5 h-5" />
                        <span className="text-sm font-medium hidden sm:inline">
                          대기
                        </span>
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <span className="font-medium text-gray-900">
                        {participant.nickname}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        participant.is_registered
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {participant.is_registered ? '회원' : '익명'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 hidden md:table-cell">
                    {participant.email ? (
                      <div className="flex items-center space-x-1">
                        <Mail className="w-4 h-4 text-gray-400" />
                        <span>{participant.email}</span>
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {participant.has_submitted ? (
                      <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                        {participant.submitted_slots_count}개
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 hidden lg:table-cell">
                    {formatDateTime(participant.joined_at, 'M/d HH:mm')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {participants.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              아직 참가자가 없습니다
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
