import { TrendingUp, Clock } from 'lucide-react';

function ExchangeRates({ rates, isLoading }) {
  if (isLoading) {
    return (
      <div className="poe-card animate-pulse">
        <div className="h-6 bg-poe-border rounded w-32 mb-4"></div>
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-poe-border rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!rates || rates.message) {
    return (
      <div className="poe-card">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-poe-gold" />
          <h2 className="text-lg font-semibold text-white">환율 정보</h2>
        </div>
        <p className="text-gray-400 text-center py-4">
          환율 데이터가 없습니다. 스케줄러가 데이터를 수집 중입니다.
        </p>
      </div>
    );
  }

  return (
    <div className="poe-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-poe-gold" />
          <h2 className="text-lg font-semibold text-white">환율 정보</h2>
        </div>
        {rates.last_updated && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            {new Date(rates.last_updated).toLocaleString('ko-KR')}
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-poe-bg rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-poe-gold">
            {rates.divine_to_exalt?.toFixed(1) || '-'}
          </div>
          <div className="text-sm text-gray-400 mt-1">
            Divine → Exalt
          </div>
          <div className="text-xs text-poe-currency mt-2">
            1 Divine = {rates.divine_to_exalt?.toFixed(1)} Exalted
          </div>
        </div>
        
        <div className="bg-poe-bg rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-poe-gold">
            {rates.divine_to_chaos?.toFixed(0) || '-'}
          </div>
          <div className="text-sm text-gray-400 mt-1">
            Divine → Chaos
          </div>
          <div className="text-xs text-poe-currency mt-2">
            1 Divine = {rates.divine_to_chaos?.toFixed(0)} Chaos
          </div>
        </div>
        
        <div className="bg-poe-bg rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-poe-gold">
            {rates.exalt_to_chaos?.toFixed(1) || '-'}
          </div>
          <div className="text-sm text-gray-400 mt-1">
            Exalt → Chaos
          </div>
          <div className="text-xs text-poe-currency mt-2">
            1 Exalted = {rates.exalt_to_chaos?.toFixed(1)} Chaos
          </div>
        </div>
      </div>
    </div>
  );
}

export default ExchangeRates;
