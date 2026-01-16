import { Package, Search } from 'lucide-react';
import { useState } from 'react';

function BaseItemsTable({ bases, isLoading }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  if (isLoading) {
    return (
      <div className="poe-card animate-pulse">
        <div className="h-6 bg-poe-border rounded w-40 mb-4"></div>
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-10 bg-poe-border rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!bases || !bases.bases || bases.bases.length === 0) {
    return (
      <div className="poe-card">
        <div className="flex items-center gap-2 mb-4">
          <Package className="w-5 h-5 text-poe-gold" />
          <h2 className="text-lg font-semibold text-white">베이스 아이템</h2>
        </div>
        <p className="text-gray-400 text-center py-8">
          베이스 아이템 데이터가 없습니다.
        </p>
      </div>
    );
  }

  // 검색 필터링
  const filteredBases = bases.bases.filter(base =>
    base.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 페이지네이션
  const totalPages = Math.ceil(filteredBases.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedBases = filteredBases.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="poe-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Package className="w-5 h-5 text-poe-gold" />
          <h2 className="text-lg font-semibold text-white">
            베이스 아이템 ({bases.count}개)
          </h2>
        </div>
        
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="검색..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className="poe-input pl-9 w-48"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-poe-border">
              <th className="text-left py-2 px-3 text-sm text-gray-400">ID</th>
              <th className="text-left py-2 px-3 text-sm text-gray-400">이름</th>
              <th className="text-right py-2 px-3 text-sm text-gray-400">요구 레벨</th>
            </tr>
          </thead>
          <tbody>
            {paginatedBases.map((base) => (
              <tr 
                key={base.id} 
                className="border-b border-poe-border hover:bg-poe-bg transition-colors"
              >
                <td className="py-2 px-3 text-sm text-gray-500">{base.id}</td>
                <td className="py-2 px-3 text-poe-rare">{base.name}</td>
                <td className="py-2 px-3 text-right text-sm">
                  {base.required_level || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-poe-border">
          <span className="text-sm text-gray-400">
            {filteredBases.length}개 중 {startIndex + 1}-{Math.min(startIndex + itemsPerPage, filteredBases.length)}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 bg-poe-bg border border-poe-border rounded text-sm disabled:opacity-50"
            >
              이전
            </button>
            <span className="px-3 py-1 text-sm">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 bg-poe-bg border border-poe-border rounded text-sm disabled:opacity-50"
            >
              다음
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default BaseItemsTable;
