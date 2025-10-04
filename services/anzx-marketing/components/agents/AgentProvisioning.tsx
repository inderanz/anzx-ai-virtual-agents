'use client';

import { useState } from 'react';
import { provisionDemoAgent, getAgentSpaceClient, type Agent } from '@/lib/google-cloud/agentspace-client';

interface AgentProvisioningProps {
    agentType: 'emma' | 'olivia' | 'jack' | 'liam';
    onSuccess?: (agent: Agent) => void;
    onError?: (error: Error) => void;
}

export function AgentProvisioning({ agentType, onSuccess, onError }: AgentProvisioningProps) {
    const [isProvisioning, setIsProvisioning] = useState(false);
    const [agent, setAgent] = useState<Agent | null>(null);
    const [error, setError] = useState<string | null>(null);

    const agentNames = {
        emma: 'Emma - AI Recruiting Agent',
        olivia: 'Olivia - Customer Service AI',
        jack: 'Jack - AI Sales Agent',
        liam: 'Liam - Support Agent',
    };

    const handleProvision = async () => {
        setIsProvisioning(true);
        setError(null);

        try {
            // In a real implementation, you would get the access token from your auth system
            const accessToken = 'demo_token'; // Replace with actual token

            const provisionedAgent = await provisionDemoAgent(agentType, accessToken);
            setAgent(provisionedAgent);

            if (onSuccess) {
                onSuccess(provisionedAgent);
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to provision agent';
            setError(errorMessage);

            if (onError) {
                onError(err instanceof Error ? err : new Error(errorMessage));
            }
        } finally {
            setIsProvisioning(false);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
                Provision {agentNames[agentType]}
            </h3>

            {!agent && !error && (
                <div>
                    <p className="text-gray-600 mb-4">
                        Click the button below to provision your AI agent on Google Cloud AgentSpace.
                    </p>
                    <button
                        onClick={handleProvision}
                        disabled={isProvisioning}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isProvisioning ? 'Provisioning...' : 'Provision Agent'}
                    </button>
                </div>
            )}

            {agent && (
                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-green-600">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                clipRule="evenodd"
                            />
                        </svg>
                        <span className="font-medium">Agent Provisioned Successfully!</span>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                        <div>
                            <span className="text-sm font-medium text-gray-700">Agent ID:</span>
                            <p className="text-sm text-gray-900 font-mono">{agent.id}</p>
                        </div>
                        <div>
                            <span className="text-sm font-medium text-gray-700">Name:</span>
                            <p className="text-sm text-gray-900">{agent.displayName}</p>
                        </div>
                        <div>
                            <span className="text-sm font-medium text-gray-700">Status:</span>
                            <p className="text-sm text-gray-900 capitalize">{agent.status}</p>
                        </div>
                        <div>
                            <span className="text-sm font-medium text-gray-700">Model:</span>
                            <p className="text-sm text-gray-900">{agent.model}</p>
                        </div>
                    </div>
                </div>
            )}

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-red-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                clipRule="evenodd"
                            />
                        </svg>
                        <div>
                            <p className="text-sm font-medium text-red-900">Provisioning Failed</p>
                            <p className="text-sm text-red-700 mt-1">{error}</p>
                        </div>
                    </div>
                    <button
                        onClick={handleProvision}
                        className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            )}
        </div>
    );
}

export default AgentProvisioning;
