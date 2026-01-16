import { Database, Coins, Package, Settings, CheckCircle, XCircle } from 'lucide-react';

function StatsCards({ stats, isLoading }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="poe-card animate-pulse">
            <div className="h-8 bg-poe-border rounded w-16 mx-auto mb-2"></div>
            <div className="h-4 bg-poe-border rounded w-20 mx-auto"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const statItems = [
    { label: '리그', value: stats.leagues || 0, icon: Database },
    { label: '커런시', value: stats.currencies || 0, icon: Coins },
    { label: '베이스 아이템', value: stats.bases || 0, icon: Package },
    { label: '모디파이어', value: stats.modifiers || 0, icon: Settings },
    { label: '환율 기록', value: stats.exchange_rates || 0, icon: Database },
    { 
      label: '스케줄러', 
      value: stats.scheduler_active ? '활성' : '비활성',
      icon: stats.scheduler_active ? CheckCircle : XCircle,
      isStatus: true,
      isActive: stats.scheduler_active
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {statItems.map((item, index) => {
        const Icon = item.icon;
        return (
          <div key={index} className="stat-card">
            <Icon className={`w-5 h-5 mb-2 ${
              item.isStatus 
                ? (item.isActive ? 'text-green-500' : 'text-red-500')
                : 'text-poe-gold'
            }`} />
            <div className={`stat-value ${
              item.isStatus 
                ? (item.isActive ? 'text-green-500' : 'text-red-500')
                : ''
            }`}>
              {item.value}
            </div>
            <div className="stat-label">{item.label}</div>
          </div>
        );
      })}
    </div>
  );
}

export default StatsCards;
