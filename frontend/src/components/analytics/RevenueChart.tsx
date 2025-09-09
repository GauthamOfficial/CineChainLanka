import React from 'react';

interface RevenueChartProps {
  data: {
    labels: string[];
    revenue_data: number[];
    creator_royalties_data: number[];
    investor_royalties_data: number[];
    platform_fees_data: number[];
  };
  type?: 'line' | 'bar';
  title?: string;
  height?: number;
}

const RevenueChart: React.FC<RevenueChartProps> = ({ 
  data, 
  type = 'line', 
  title = 'Revenue Analytics',
  height = 400 
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const maxValue = Math.max(
    ...data.revenue_data,
    ...data.creator_royalties_data,
    ...data.investor_royalties_data,
    ...data.platform_fees_data
  );

  const getBarHeight = (value: number) => {
    return maxValue > 0 ? (value / maxValue) * 100 : 0;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">{title}</h3>
      
      {type === 'bar' ? (
        <div className="space-y-4">
          {data.labels.map((label, index) => (
            <div key={index} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">{label}</span>
                <span className="text-sm text-gray-500">
                  {formatCurrency(data.revenue_data[index] || 0)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div 
                  className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                  style={{ width: `${getBarHeight(data.revenue_data[index] || 0)}%` }}
                ></div>
              </div>
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div className="text-green-600">
                  Creator: {formatCurrency(data.creator_royalties_data[index] || 0)}
                </div>
                <div className="text-yellow-600">
                  Investor: {formatCurrency(data.investor_royalties_data[index] || 0)}
                </div>
                <div className="text-red-600">
                  Platform: {formatCurrency(data.platform_fees_data[index] || 0)}
                </div>
                <div className="text-gray-600">
                  Total: {formatCurrency(data.revenue_data[index] || 0)}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {formatCurrency(data.revenue_data.reduce((a, b) => a + b, 0))}
              </div>
              <div className="text-sm text-blue-600">Total Revenue</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(data.creator_royalties_data.reduce((a, b) => a + b, 0))}
              </div>
              <div className="text-sm text-green-600">Creator Royalties</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {formatCurrency(data.investor_royalties_data.reduce((a, b) => a + b, 0))}
              </div>
              <div className="text-sm text-yellow-600">Investor Royalties</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {formatCurrency(data.platform_fees_data.reduce((a, b) => a + b, 0))}
              </div>
              <div className="text-sm text-red-600">Platform Fees</div>
            </div>
          </div>
          
          <div className="space-y-2">
            {data.labels.map((label, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">{label}</span>
                <div className="flex space-x-4 text-sm">
                  <span className="text-green-600">
                    Creator: {formatCurrency(data.creator_royalties_data[index] || 0)}
                  </span>
                  <span className="text-yellow-600">
                    Investor: {formatCurrency(data.investor_royalties_data[index] || 0)}
                  </span>
                  <span className="text-red-600">
                    Platform: {formatCurrency(data.platform_fees_data[index] || 0)}
                  </span>
                  <span className="font-medium text-gray-900">
                    Total: {formatCurrency(data.revenue_data[index] || 0)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RevenueChart;
