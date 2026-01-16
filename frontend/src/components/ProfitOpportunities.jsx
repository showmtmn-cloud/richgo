import { TrendingUp, AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';

function ProfitOpportunities({ opportunities, isLoading }) {
  if (isLoading) {
    return (
      <div className="poe-card animate-pulse">
        <div className="h-6 bg-poe-border rounded w-40 mb-4"></div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-poe-border rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!opportunities || !opportunities.opportunities || opportunities.opportunities.length === 0) {
    return (
      <div className="poe-card">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-poe-gold" />
          <h2 className="text-lg font-semibold text-white">수익 기회</h2>
        </div>
        <div className="text-center py-8">
          <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-400">
            아직 수익 기회 데이터가 없습니다.
          </p>
          <p className="text-sm text-gray-500 mt-2">
            시스템이 더 많은 데이터를 수집하면 수익 기회가 표시됩니다.
          </p>
        </div>
      </div>
    );
  }

  const getRiskIcon = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'low':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'medium':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getRiskClass = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'low':
        return 'risk-low';
      case 'medium':
        return 'risk-medium';
      case 'high':
        return 'risk-high';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div className="poe-card">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-poe-gold" />
        <h2 className="text-lg font-semibold text-white">
          TOP 수익 기회 ({opportunities.count}개)
        </h2>
      </div>

      <div className="space-y-4">
        {opportunities.opportunities.map((opp, index) => (
          <div 
            key={opp.id} 
            className="bg-poe-bg rounded-lg p-4 border border-poe-border hover:border-poe-gold transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl font-bold text-poe-gold">
                  #{index + 1}
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    {getRiskIcon(opp.risk)}
                    <span className={`text-sm ${getRiskClass(opp.risk)}`}>
                      {opp.risk || 'Unknown'} Risk
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-2xl font-bold text-green-500">
                  +{opp.net_profit?.toFixed(1) || '?'} Div
                </div>
                <div className="text-sm text-gray-400">
                  ROI: {opp.roi?.toFixed(0) || '?'}%
                </div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-poe-border">
              <div>
                <div className="text-xs text-gray-500">베이스 비용</div>
                <div className="text-poe-currency">
                  {opp.base_cost?.toFixed(1) || '?'} Div
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">크래프팅 비용</div>
                <div className="text-poe-currency">
                  {opp.crafting_cost?.toFixed(1) || '?'} Div
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">예상 판매가</div>
                <div className="text-poe-rare">
                  {opp.sale_price?.toFixed(1) || '?'} Div
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">성공률</div>
                <div className="text-white">
                  {((opp.success_rate || 0) * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProfitOpportunities;
