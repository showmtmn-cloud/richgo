import { Activity, RefreshCw } from 'lucide-react';

function Header({ lastUpdated, onRefresh, isLoading }) {
  return (
    <header className="bg-poe-card border-b border-poe-border px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="w-8 h-8 text-poe-gold" />
          <div>
            <h1 className="text-xl font-bold text-white">
              PoE2 Profit Optimizer
            </h1>
            <p className="text-xs text-gray-500">
              Path of Exile 2 크래프팅 수익 최적화 시스템
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {lastUpdated && (
            <span className="text-sm text-gray-400">
              마지막 업데이트: {new Date(lastUpdated).toLocaleTimeString('ko-KR')}
            </span>
          )}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="poe-button flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            새로고침
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
