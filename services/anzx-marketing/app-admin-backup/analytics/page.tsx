'use client';

import { useEffect, useState } from 'react';
import { getAttributionReport, getStoredConversions, type AttributionReport, type ConversionData } from '@/lib/analytics/attribution';
import { RealTimeVisitors } from '@/components/analytics/RealTimeVisitors';

export default function AnalyticsDashboard() {
  const [report, setReport] = useState<AttributionReport | null>(null);
  const [conversions, setConversions] = useState<ConversionData[]>([]);
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | 'all'>('7d');

  useEffect(() => {
    // Load analytics data
    const attributionReport = getAttributionReport();
    const allConversions = getStoredConversions();

    // Filter by time range
    const now = Date.now();
    const timeRanges = {
      '24h': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000,
      '30d': 30 * 24 * 60 * 60 * 1000,
      'all': Infinity,
    };

    const filteredConversions = allConversions.filter(
      (c) => now - new Date(c.timestamp).getTime() < timeRanges[timeRange]
    );

    setConversions(filteredConversions);
    setReport(attributionReport);
  }, [timeRange]);

  if (!report) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
              <p className="text-gray-600 mt-2">Track conversions and attribution data</p>
            </div>
            <RealTimeVisitors />
          </div>
        </div>

        {/* Time Range Selector */}
        <div className="mb-6 flex gap-2">
          {(['24h', '7d', '30d', 'all'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {range === '24h' && 'Last 24 Hours'}
              {range === '7d' && 'Last 7 Days'}
              {range === '30d' && 'Last 30 Days'}
              {range === 'all' && 'All Time'}
            </button>
          ))}
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Conversions"
            value={conversions.length}
            icon="📊"
          />
          <MetricCard
            title="Total Value"
            value={`$${report.totalValue.toFixed(2)}`}
            icon="💰"
          />
          <MetricCard
            title="Avg. Value"
            value={`$${(report.totalValue / (conversions.length || 1)).toFixed(2)}`}
            icon="📈"
          />
          <MetricCard
            title="Conversion Rate"
            value="N/A"
            subtitle="Requires traffic data"
            icon="🎯"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Conversions by Source */}
          <ChartCard title="Conversions by Source">
            <BarChart data={report.conversionsBySource} />
          </ChartCard>

          {/* Conversions by Medium */}
          <ChartCard title="Conversions by Medium">
            <BarChart data={report.conversionsByMedium} />
          </ChartCard>

          {/* Conversions by Type */}
          <ChartCard title="Conversions by Type">
            <BarChart data={report.conversionsByType} />
          </ChartCard>

          {/* Conversions by Campaign */}
          <ChartCard title="Conversions by Campaign">
            <BarChart data={report.conversionsByCampaign} />
          </ChartCard>
        </div>

        {/* Recent Conversions Table */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Conversions</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Type</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Source</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Medium</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Campaign</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Value</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
                </tr>
              </thead>
              <tbody>
                {conversions.slice(0, 20).map((conversion, index) => (
                  <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-gray-900">{conversion.type}</td>
                    <td className="py-3 px-4 text-gray-600">{conversion.attribution.source}</td>
                    <td className="py-3 px-4 text-gray-600">{conversion.attribution.medium}</td>
                    <td className="py-3 px-4 text-gray-600">{conversion.attribution.campaign || '-'}</td>
                    <td className="py-3 px-4 text-gray-900">
                      {conversion.value ? `$${conversion.value}` : '-'}
                    </td>
                    <td className="py-3 px-4 text-gray-600">
                      {new Date(conversion.timestamp).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  title,
  value,
  subtitle,
  icon,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-2">
        <p className="text-gray-600 text-sm font-medium">{title}</p>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">{title}</h3>
      {children}
    </div>
  );
}

function BarChart({ data }: { data: Record<string, number> }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const maxValue = Math.max(...entries.map(([, value]) => value), 1);

  if (entries.length === 0) {
    return <p className="text-gray-500 text-center py-8">No data available</p>;
  }

  return (
    <div className="space-y-3">
      {entries.map(([label, value]) => (
        <div key={label}>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">{label}</span>
            <span className="text-sm font-bold text-gray-900">{value}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(value / maxValue) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
