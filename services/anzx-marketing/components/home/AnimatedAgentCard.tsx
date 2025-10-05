"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import type { Agent } from '@/lib/constants/agents';

interface AnimatedAgentCardProps {
    agent: Agent;
}

// Realistic typing responses for each agent
const AGENT_RESPONSES: Record<string, string[]> = {
    emma: [
        "I can help you find the perfect candidate...",
        "Screening 50+ resumes per hour...",
        "Interview scheduled for tomorrow at 2pm",
        "Found 3 qualified candidates for you",
    ],
    olivia: [
        "How can I help you today?",
        "Let me check that for you...",
        "I've resolved 127 tickets this week",
        "Your issue has been escalated to priority",
    ],
    jack: [
        "Let's discuss your business needs...",
        "I've qualified 15 leads today",
        "Scheduling a demo for next Tuesday",
        "This solution can save you 40% costs",
    ],
    liam: [
        "Running diagnostics on your system...",
        "I found the issue in your API config",
        "Let me walk you through the fix...",
        "System health check: All green ✓",
    ],
    inder: [
        "Analyzing your GCP infrastructure...",
        "Found $2,400/month in cost savings",
        "Scaling Kubernetes cluster to 12 nodes",
        "Security scan complete: 0 vulnerabilities",
    ],
    alex: [
        "Deploying to production in 3 minutes...",
        "CI/CD pipeline running: 47 tests passed",
        "GitOps sync complete: 15 resources updated",
        "Zero-downtime deployment successful ✓",
    ],
    ashish: [
        "Monitoring 247 services across 8 regions",
        "SLO compliance: 99.97% this month",
        "Incident detected and auto-resolved",
        "Performance optimized: -35ms latency",
    ],
};

export function AnimatedAgentCard({ agent }: AnimatedAgentCardProps) {
    const router = useRouter();
    const [currentResponse, setCurrentResponse] = useState(0);
    const responses = AGENT_RESPONSES[agent.id] || ["Ready to assist you..."];

    // Cycle through responses
    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentResponse((prev) => (prev + 1) % responses.length);
        }, 4000); // Change response every 4 seconds

        return () => clearInterval(interval);
    }, [responses.length]);

    const handleClick = () => {
        // Map agent IDs to their detail page routes
        const agentRoutes: Record<string, string> = {
            emma: '/en/ai-recruiting-agent',
            olivia: '/en/customer-service-ai',
            jack: '/en/ai-sales-agent-jack',
            liam: '/en/ai-support-agent',
            inder: '/en/google-cloud-agent',
            alex: '/en/devops-gitops-agent',
            ashish: '/en/sre-agent',
        };

        const route = agentRoutes[agent.id] || `/en/agents/${agent.id}`;
        router.push(route);
    };

    return (
        <div
            onClick={handleClick}
            className="group bg-white/95 backdrop-blur-sm rounded-2xl p-6 shadow-2xl hover:shadow-[0_20px_60px_rgba(20,184,166,0.5)] transition-all cursor-pointer border border-gray-100 hover:scale-105 hover:-translate-y-2 hover:bg-white"
        >
            {/* Status Header */}
            <div className="flex items-center justify-between mb-3">
                <span className={`flex items-center gap-1.5 text-xs font-semibold ${agent.id === 'emma' ? 'text-purple-600' :
                        agent.id === 'olivia' ? 'text-blue-600' :
                            agent.id === 'jack' ? 'text-orange-600' :
                                agent.id === 'liam' ? 'text-green-600' :
                                    agent.id === 'inder' ? 'text-indigo-600' :
                                        agent.id === 'alex' ? 'text-violet-600' :
                                            agent.id === 'ashish' ? 'text-rose-600' :
                                                'text-gray-600'
                    }`}>
                    <span className={`w-2 h-2 rounded-full animate-pulse ${agent.id === 'emma' ? 'bg-purple-500' :
                            agent.id === 'olivia' ? 'bg-blue-500' :
                                agent.id === 'jack' ? 'bg-orange-500' :
                                    agent.id === 'liam' ? 'bg-green-500' :
                                        agent.id === 'inder' ? 'bg-indigo-500' :
                                            agent.id === 'alex' ? 'bg-violet-500' :
                                                agent.id === 'ashish' ? 'bg-rose-500' :
                                                    'bg-gray-500'
                        }`}></span>
                    Online
                </span>
                <span className="text-xs text-gray-400 font-medium">Just now</span>
            </div>

            {/* Avatar with animated gradient */}
            <div className="relative w-16 h-16 mx-auto mb-4">
                <div className={`absolute inset-0 rounded-full animate-pulse opacity-75 ${agent.id === 'emma' ? 'bg-gradient-to-br from-purple-600 to-pink-500' :
                        agent.id === 'olivia' ? 'bg-gradient-to-br from-blue-600 to-cyan-500' :
                            agent.id === 'jack' ? 'bg-gradient-to-br from-orange-600 to-red-500' :
                                agent.id === 'liam' ? 'bg-gradient-to-br from-green-600 to-emerald-500' :
                                    agent.id === 'inder' ? 'bg-gradient-to-br from-indigo-600 to-blue-500' :
                                        agent.id === 'alex' ? 'bg-gradient-to-br from-violet-600 to-purple-500' :
                                            agent.id === 'ashish' ? 'bg-gradient-to-br from-rose-600 to-pink-500' :
                                                'bg-gradient-to-br from-gray-600 to-gray-400'
                    }`}></div>
                <div className={`relative w-full h-full rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg transition-shadow ${agent.id === 'emma' ? 'bg-gradient-to-br from-purple-600 to-pink-500 group-hover:shadow-[0_10px_30px_rgba(168,85,247,0.6)]' :
                        agent.id === 'olivia' ? 'bg-gradient-to-br from-blue-600 to-cyan-500 group-hover:shadow-[0_10px_30px_rgba(59,130,246,0.6)]' :
                            agent.id === 'jack' ? 'bg-gradient-to-br from-orange-600 to-red-500 group-hover:shadow-[0_10px_30px_rgba(249,115,22,0.6)]' :
                                agent.id === 'liam' ? 'bg-gradient-to-br from-green-600 to-emerald-500 group-hover:shadow-[0_10px_30px_rgba(34,197,94,0.6)]' :
                                    agent.id === 'inder' ? 'bg-gradient-to-br from-indigo-600 to-blue-500 group-hover:shadow-[0_10px_30px_rgba(99,102,241,0.6)]' :
                                        agent.id === 'alex' ? 'bg-gradient-to-br from-violet-600 to-purple-500 group-hover:shadow-[0_10px_30px_rgba(139,92,246,0.6)]' :
                                            agent.id === 'ashish' ? 'bg-gradient-to-br from-rose-600 to-pink-500 group-hover:shadow-[0_10px_30px_rgba(244,63,94,0.6)]' :
                                                'bg-gradient-to-br from-gray-600 to-gray-400'
                    }`}>
                    {agent.name[0]}
                    {/* Active indicator */}
                    <span className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></span>
                </div>
            </div>

            {/* Agent Info */}
            <h3 className="font-bold text-gray-900 mb-1 text-center">{agent.name}</h3>
            <p className="text-sm text-gray-600 font-medium text-center mb-3">{agent.role}</p>

            {/* Animated Response Message */}
            <div className="min-h-[40px] flex flex-col items-center justify-center">
                <div className="flex items-center justify-center gap-1 text-xs text-gray-500 italic mb-1">
                    <span className="inline-flex gap-0.5">
                        <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    </span>
                </div>
                <p className={`text-xs font-medium text-center px-2 animate-fade-in ${agent.id === 'emma' ? 'text-purple-700' :
                        agent.id === 'olivia' ? 'text-blue-700' :
                            agent.id === 'jack' ? 'text-orange-700' :
                                agent.id === 'liam' ? 'text-green-700' :
                                    agent.id === 'inder' ? 'text-indigo-700' :
                                        agent.id === 'alex' ? 'text-violet-700' :
                                            agent.id === 'ashish' ? 'text-rose-700' :
                                                'text-gray-700'
                    }`}>
                    "{responses[currentResponse]}"
                </p>
            </div>

            {/* Click hint */}
            <div className="mt-3 text-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span className={`text-xs font-semibold ${agent.id === 'emma' ? 'text-purple-600' :
                        agent.id === 'olivia' ? 'text-blue-600' :
                            agent.id === 'jack' ? 'text-orange-600' :
                                agent.id === 'liam' ? 'text-green-600' :
                                    agent.id === 'inder' ? 'text-indigo-600' :
                                        agent.id === 'alex' ? 'text-violet-600' :
                                            agent.id === 'ashish' ? 'text-rose-600' :
                                                'text-gray-600'
                    }`}>Click to learn more →</span>
            </div>

            <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(-5px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
      `}</style>
        </div>
    );
}
