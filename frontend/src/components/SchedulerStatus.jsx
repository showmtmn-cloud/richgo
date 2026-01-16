import { Clock, CheckCircle, XCircle, Calendar } from 'lucide-react';

function SchedulerStatus({ schedulerStatus, isLoading }) {
  if (isLoading) {
    return (
      <div className="poe-card animate-pulse">
        <div className="h-6 bg-poe-border rounded w-32 mb-4"></div>
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-8 bg-poe-border rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!schedulerStatus) {
    return null;
  }

  return (
    <div className="poe-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-poe-gold" />
          <h2 className="text-lg font-semibold text-white">스케줄러 상태</h2>
        </div>
        <div className="flex items-center gap-2">
          {schedulerStatus.running ? (
            <>
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-sm text-green-500">실행 중</span>
            </>
          ) : (
            <>
              <XCircle className="w-4 h-4 text-red-500" />
              <span className="text-sm text-red-500">중지됨</span>
            </>
          )}
        </div>
      </div>

      {schedulerStatus.jobs && schedulerStatus.jobs.length > 0 ? (
        <div className="space-y-2">
          <div className="text-sm text-gray-400 mb-2">
            등록된 작업: {schedulerStatus.jobs_count}개
          </div>
          {schedulerStatus.jobs.map((job, index) => (
            <div 
              key={job.id || index}
              className="flex items-center justify-between bg-poe-bg rounded p-3"
            >
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-white">{job.name || job.id}</span>
              </div>
              {job.next_run && (
                <span className="text-xs text-gray-400">
                  다음 실행: {new Date(job.next_run).toLocaleString('ko-KR')}
                </span>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-400 text-sm">등록된 작업이 없습니다.</p>
      )}
    </div>
  );
}

export default SchedulerStatus;
