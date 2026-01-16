import { useState, useEffect, useCallback } from 'react';
import { apiService } from './services/api';
import Header from './components/Header';
import ExchangeRates from './components/ExchangeRates';
import StatsCards from './components/StatsCards';
import BaseItemsTable from './components/BaseItemsTable';
import ProfitOpportunities from './components/ProfitOpportunities';
import SchedulerStatus from './components/SchedulerStatus';
import { AlertCircle, Wifi, WifiOff } from 'lucide-react';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  
  // 데이터 상태
  const [stats, setStats] = useState(null);
  const [exchangeRates, setExchangeRates] = useState(null);
  const [bases, setBases] = useState(null);
  const [opportunities, setOpportunities] = useState(null);
  const [schedulerStatus, setSchedulerStatus] = useState(null);

  // 데이터 로드 함수
  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 병렬로 모든 데이터 로드
      const [
        statsData,
        ratesData,
        basesData,
        oppsData,
        schedulerData
      ] = await Promise.all([
        apiService.getStats().catch(() => null),
        apiService.getExchangeRates().catch(() => null),
        apiService.getBases(500).catch(() => null),
        apiService.getProfitOpportunities(10).catch(() => null),
        apiService.getSchedulerStatus().catch(() => null)
      ]);

      setStats(statsData);
      setExchangeRates(ratesData);
      setBases(basesData);
      setOpportunities(oppsData);
      setSchedulerStatus(schedulerData);
      setIsConnected(true);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('서버 연결 실패. 백엔드가 실행 중인지 확인하세요.');
      setIsConnected(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 초기 로드 및 자동 새로고침
  useEffect(() => {
    loadData();
    
    // 30초마다 자동 새로고침
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  return (
    <div className="min-h-screen bg-poe-bg">
      <Header 
        lastUpdated={lastUpdated}
        onRefresh={loadData}
        isLoading={isLoading}
      />

      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* 연결 상태 */}
        <div className={`flex items-center gap-2 text-sm ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
          {isConnected ? (
            <>
              <Wifi className="w-4 h-4" />
              <span>서버 연결됨</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4" />
              <span>서버 연결 안됨</span>
            </>
          )}
        </div>

        {/* 에러 메시지 */}
        {error && (
          <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <div>
              <p className="text-red-400 font-medium">{error}</p>
              <p className="text-sm text-red-400/70 mt-1">
                백엔드 서버: uvicorn main:app --host 0.0.0.0 --port 8001
              </p>
            </div>
          </div>
        )}

        {/* 통계 카드 */}
        <StatsCards stats={stats} isLoading={isLoading && !stats} />

        {/* 환율 정보 */}
        <ExchangeRates rates={exchangeRates} isLoading={isLoading && !exchangeRates} />

        {/* 2열 레이아웃 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 수익 기회 */}
          <ProfitOpportunities 
            opportunities={opportunities} 
            isLoading={isLoading && !opportunities} 
          />

          {/* 스케줄러 상태 */}
          <SchedulerStatus 
            schedulerStatus={schedulerStatus} 
            isLoading={isLoading && !schedulerStatus} 
          />
        </div>

        {/* 베이스 아이템 테이블 */}
        <BaseItemsTable bases={bases} isLoading={isLoading && !bases} />

        {/* 푸터 */}
        <footer className="text-center text-sm text-gray-500 py-4 border-t border-poe-border">
          <p>PoE2 Profit Optimizer v0.2.0</p>
          <p className="mt-1">Path of Exile 2 크래프팅 수익 최적화 시스템</p>
        </footer>
      </main>
    </div>
  );
}

export default App;
