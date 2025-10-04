'use client';

import { useEffect, useState } from 'react';
import { getAgentSpaceClient, type AgentStatus } from '@/lib/google-cloud/agentspace-client';

interface AgentStatusMonitorProps {
  agentId: string;
  refreshInterval?: number; // in milliseconds
}

export function AgentStatusMonitor({ agentId, refreshInterval = 30000 }: AgentStatusMonitorProps) {
  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const client = getAgentSpaceClient();
        const agentStatus = await client.getAgentStatus(agentId);
        setStatus(agentStatus);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch agent status');
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchStatus();

    // Set up polling
    const interval = setInterval(fetchStatus, refreshInterval);

    return () => clearInterval(interval);
  }, [agentId, refreshInterval]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-sm text-red-800">{error}</p>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  const statusColors = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    provisioning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
  };

  const healthColors = {
    healthy: 'text-green-600',
    degraded: 'text-yellow-600',
    unhealthy: 'text-red-600',
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Agent Status</h3>

      <div className="space-y-4">
        {/* Status Badge */}
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[status.status]}`}>
            {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
          </span>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${status.health === 'healthy' ? 'bg-green-500' : status.health === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'}`} />
            <span className={`text-sm font-medium ${healthColors[status.health]}`}>
              {status.health.charAt(0).toUpperCase() + status.health.slice(1)}
            </span>
          </div>
        </div>

        {/* Last Heartbeat */}
        <div>
          <span className="text-sm font-medium text-gray-700">Last Heartbeat:</span>
          <p className="text-sm text-gray-900">
            {new Date(status.lastHeartbeat).toLocaleString()}
          </p>
        </div>

        {/* Metrics */}
        {status.metrics && (
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
            <div>
              <p className="text-xs text-gray-600">Requests</p>
              <p className="text-lg font-bold text-gray-900">{status.metrics.requestCount.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600">Error Rate</p>
              <p className="text-lg font-bold text-gray-900">{(status.metrics.errorRate * 100).toFixed(2)}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-600">Avg Latency</p>
              <p className="text-lg font-bold text-gray-900">{status.metrics.averageLatency}ms</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AgentStatusMonitor;
