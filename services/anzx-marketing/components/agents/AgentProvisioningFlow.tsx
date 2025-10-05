'use client';

import { useState } from 'react';
import { Agent } from '@/lib/constants/agents';
import { getAgentTemplate, type ADKAgentTemplate } from '@/lib/google-cloud/adk-templates';
import { AgentSpaceClient } from '@/lib/google-cloud/agentspace-client';
import { getMCPClient, MCP_SERVERS } from '@/lib/google-cloud/mcp-config';

interface AgentProvisioningFlowProps {
  agent: Agent;
  onComplete?: (agentId: string) => void;
  onCancel?: () => void;
}

type ProvisioningStep = 'config' | 'integrations' | 'provisioning' | 'complete';

export function AgentProvisioningFlow({ agent, onComplete, onCancel }: AgentProvisioningFlowProps) {
  const [currentStep, setCurrentStep] = useState<ProvisioningStep>('config');
  const [selectedIntegrations, setSelectedIntegrations] = useState<string[]>([]);
  const [agentConfig, setAgentConfig] = useState({
    name: agent.name,
    description: agent.description,
    capabilities: agent.capabilities,
  });
  const [provisioningStatus, setProvisioningStatus] = useState<string>('');
  const [error, setError] = useState<string>('');

  const agentTemplate = getAgentTemplate(agent.id as 'emma' | 'olivia' | 'jack' | 'liam');

  const handleProvision = async () => {
    setCurrentStep('provisioning');
    setError('');

    try {
      const client = new AgentSpaceClient();

      // Step 1: Create agent instance
      setProvisioningStatus('Creating agent instance...');
      const agentInstance = await client.provisionAgent({
        name: agent.id,
        displayName: agentConfig.name,
        description: agentConfig.description,
        model: 'gemini-1.5-pro',
        capabilities: agentConfig.capabilities,
        configuration: {
          template: agentTemplate?.name || agent.id,
          integrations: selectedIntegrations,
        },
      });

      // Step 2: Configure integrations
      if (selectedIntegrations.length > 0) {
        setProvisioningStatus('Configuring integrations...');
        
        for (const integration of selectedIntegrations) {
          const mcpClient = getMCPClient(integration);
          const isConnected = await mcpClient.testConnection();
          
          if (!isConnected) {
            console.warn(`Integration ${integration} is not available`);
          }
        }
      }

      // Step 3: Agent is now deployed
      setProvisioningStatus('Agent deployed successfully!');

      // Step 4: Complete
      setProvisioningStatus('Agent deployed successfully!');
      setCurrentStep('complete');

      if (onComplete) {
        onComplete(agentInstance.id);
      }
    } catch (err) {
      console.error('Provisioning failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to provision agent');
      setCurrentStep('config');
    }
  };

  const toggleIntegration = (integration: string) => {
    setSelectedIntegrations((prev) =>
      prev.includes(integration)
        ? prev.filter((i) => i !== integration)
        : [...prev, integration]
    );
  };

  const renderConfigStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white mb-4">Configure {agent.name}</h3>
        <p className="text-gray-400 mb-6">
          Customize your agent's settings before deployment
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Agent Name
        </label>
        <input
          type="text"
          value={agentConfig.name}
          onChange={(e) => setAgentConfig({ ...agentConfig, name: e.target.value })}
          className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Description
        </label>
        <textarea
          value={agentConfig.description}
          onChange={(e) => setAgentConfig({ ...agentConfig, description: e.target.value })}
          rows={3}
          className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Capabilities
        </label>
        <div className="space-y-2">
          {agent.capabilities.map((capability, index) => (
            <div key={index} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={agentConfig.capabilities.includes(capability)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setAgentConfig({
                      ...agentConfig,
                      capabilities: [...agentConfig.capabilities, capability],
                    });
                  } else {
                    setAgentConfig({
                      ...agentConfig,
                      capabilities: agentConfig.capabilities.filter((c) => c !== capability),
                    });
                  }
                }}
                className="w-4 h-4 rounded border-white/20 bg-white/5"
              />
              <span className="text-gray-300 text-sm">{capability}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => setCurrentStep('integrations')}
          className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          Next: Integrations
        </button>
        {onCancel && (
          <button
            onClick={onCancel}
            className="px-6 py-3 border border-white/20 text-white rounded-lg hover:bg-white/10 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );

  const renderIntegrationsStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white mb-4">Select Integrations</h3>
        <p className="text-gray-400 mb-6">
          Choose which systems {agent.name} should connect to
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(MCP_SERVERS).map(([key, server]) => {
          const isSelected = selectedIntegrations.includes(key);
          const isRecommended = agent.integrations.some((i) =>
            i.toLowerCase().includes(key.toLowerCase())
          );

          return (
            <div
              key={key}
              onClick={() => toggleIntegration(key)}
              className={`
                p-4 rounded-lg border cursor-pointer transition-all
                ${
                  isSelected
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-white/10 bg-white/5 hover:border-white/20'
                }
              `}
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium text-white">{server.displayName}</h4>
                {isRecommended && (
                  <span className="px-2 py-1 text-xs rounded-full bg-green-500/20 text-green-400">
                    Recommended
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-400 mb-3">{server.description}</p>
              <div className="flex flex-wrap gap-2">
                {server.capabilities.slice(0, 3).map((cap, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 text-xs rounded-full bg-white/10 text-gray-300"
                  >
                    {cap}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => setCurrentStep('config')}
          className="px-6 py-3 border border-white/20 text-white rounded-lg hover:bg-white/10 transition-colors"
        >
          Back
        </button>
        <button
          onClick={handleProvision}
          className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
        >
          Deploy Agent
        </button>
      </div>
    </div>
  );

  const renderProvisioningStep = () => (
    <div className="space-y-6 text-center">
      <div className="w-16 h-16 mx-auto">
        <div className="w-full h-full border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
      <div>
        <h3 className="text-xl font-bold text-white mb-2">Provisioning Agent</h3>
        <p className="text-gray-400">{provisioningStatus}</p>
      </div>
    </div>
  );

  const renderCompleteStep = () => (
    <div className="space-y-6 text-center">
      <div className="w-16 h-16 mx-auto bg-green-500 rounded-full flex items-center justify-center">
        <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <div>
        <h3 className="text-xl font-bold text-white mb-2">Agent Deployed!</h3>
        <p className="text-gray-400 mb-6">
          {agent.name} is now ready to use
        </p>
      </div>
      <div className="flex gap-3 justify-center">
        <button
          onClick={() => window.location.href = `/dashboard/agents/${agent.id}`}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          Go to Dashboard
        </button>
        <button
          onClick={() => window.location.href = `${agent.id}/demo`}
          className="px-6 py-3 border border-white/20 text-white rounded-lg hover:bg-white/10 transition-colors"
        >
          Try Demo
        </button>
      </div>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto p-6 bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10">
      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {currentStep === 'config' && renderConfigStep()}
      {currentStep === 'integrations' && renderIntegrationsStep()}
      {currentStep === 'provisioning' && renderProvisioningStep()}
      {currentStep === 'complete' && renderCompleteStep()}
    </div>
  );
}
