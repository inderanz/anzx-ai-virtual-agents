'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Agent } from '@/lib/constants/agents';
import { getAgentTemplate, type ADKAgentTemplate } from '@/lib/google-cloud/adk-templates';
import { AgentSpaceClient, type AgentStatus } from '@/lib/google-cloud/agentspace-client';

interface InteractiveAgentCardProps {
  agent: Agent;
  href: string;
}

export function InteractiveAgentCard({ agent, href }: InteractiveAgentCardProps) {
  const [currentMessage, setCurrentMessage] = useState('');
  const [messageIndex, setMessageIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(true);
  const [isHovered, setIsHovered] = useState(false);
  const [canProvision, setCanProvision] = useState(false);
  const [isProvisioning, setIsProvisioning] = useState(false);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // Get agent template from ADK
  const agentTemplate = getAgentTemplate(agent.id as 'emma' | 'olivia' | 'jack' | 'liam');
  
  // Use real agent responses from the template
  const messages = [
    `Hi! I'm ${agent.name}, ${agent.description.toLowerCase()}`,
    `I can help with ${agent.capabilities[0].toLowerCase()}`,
    `Ready to ${agent.useCases[0].toLowerCase()}?`,
  ];

  // Check if agent can be provisioned
  useEffect(() => {
    const checkProvisioning = async () => {
      try {
        const client = new AgentSpaceClient();
        const agents = await client.listAgents();
        const existingAgent = agents.find((a) => a.name === agent.id);
        setCanProvision(!existingAgent || existingAgent.status === 'inactive');
      } catch (error) {
        console.error('Failed to check agent status:', error);
        setCanProvision(true); // Allow provisioning if check fails
      }
    };

    checkProvisioning();
  }, [agent.id]);

  // Typing animation effect
  useEffect(() => {
    if (!isTyping) return;

    const currentMsg = messages[messageIndex];

    if (charIndex < currentMsg.length) {
      typingTimeoutRef.current = setTimeout(() => {
        setCurrentMessage(currentMsg.slice(0, charIndex + 1));
        setCharIndex(charIndex + 1);
      }, 50);
    } else {
      // Message complete, pause before next message
      typingTimeoutRef.current = setTimeout(() => {
        setCharIndex(0);
        setMessageIndex((messageIndex + 1) % messages.length);
      }, 3000);
    }

    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [charIndex, messageIndex, messages, isTyping]);

  // Pause typing on hover
  useEffect(() => {
    if (isHovered) {
      setIsTyping(false);
    } else {
      setIsTyping(true);
    }
  }, [isHovered]);

  const handleProvision = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!canProvision || isProvisioning) return;

    setIsProvisioning(true);

    try {
      const client = new AgentSpaceClient();
      await client.provisionAgent({
        name: agent.id,
        displayName: agent.name,
        description: agent.description,
        model: 'gemini-1.5-pro',
        capabilities: agent.capabilities,
      });
      
      // Redirect to agent dashboard after provisioning
      window.location.href = `/dashboard/agents/${agent.id}`;
    } catch (error) {
      console.error('Failed to provision agent:', error);
      alert('Failed to provision agent. Please try again.');
      setIsProvisioning(false);
    }
  };

  const gradientColors = {
    emma: 'from-purple-500 to-pink-500',
    olivia: 'from-blue-500 to-cyan-500',
    jack: 'from-orange-500 to-red-500',
    liam: 'from-green-500 to-emerald-500',
  };

  const gradient = gradientColors[agent.id as keyof typeof gradientColors] || 'from-gray-500 to-gray-700';

  return (
    <Link href={href}>
      <div
        className={`
          relative group cursor-pointer
          bg-white/5 backdrop-blur-sm
          border border-white/10
          rounded-2xl p-6
          transition-all duration-300 ease-out
          hover:scale-[1.02] hover:shadow-2xl hover:shadow-${agent.id}/20
          ${isHovered ? 'ring-2 ring-white/20' : ''}
        `}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Gradient border effect */}
        <div
          className={`
            absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100
            bg-gradient-to-r ${gradient}
            blur-xl transition-opacity duration-300
            -z-10
          `}
        />

        {/* Avatar */}
        <div className="flex items-center gap-4 mb-4">
          <div
            className={`
              w-16 h-16 rounded-full
              bg-gradient-to-br ${gradient}
              flex items-center justify-center
              text-2xl font-bold text-white
              shadow-lg
            `}
          >
            {agent.name[0]}
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">{agent.name}</h3>
            <p className="text-sm text-gray-400">{agent.role}</p>
          </div>
        </div>

        {/* Typing message */}
        <div className="min-h-[60px] mb-4">
          <p className="text-gray-300 text-sm leading-relaxed">
            {currentMessage}
            <span className="inline-block w-0.5 h-4 bg-white/70 ml-1 animate-pulse" />
          </p>
        </div>

        {/* Capabilities */}
        <div className="flex flex-wrap gap-2 mb-4">
          {agent.capabilities.slice(0, 3).map((capability, index) => (
            <span
              key={index}
              className="px-2 py-1 text-xs rounded-full bg-white/10 text-gray-300"
            >
              {capability}
            </span>
          ))}
        </div>

        {/* Action buttons */}
        <div className="flex gap-2">
          <button
            className={`
              flex-1 px-4 py-2 rounded-lg
              bg-gradient-to-r ${gradient}
              text-white font-medium text-sm
              transition-all duration-200
              hover:shadow-lg hover:scale-105
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
            onClick={handleProvision}
            disabled={!canProvision || isProvisioning}
          >
            {isProvisioning ? 'Provisioning...' : canProvision ? 'Deploy Agent' : 'View Details'}
          </button>
          
          <button
            className="px-4 py-2 rounded-lg border border-white/20 text-white text-sm hover:bg-white/10 transition-colors"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              window.location.href = `${href}#demo`;
            }}
          >
            Try Demo
          </button>
        </div>

        {/* Status indicator */}
        {canProvision && (
          <div className="absolute top-4 right-4">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          </div>
        )}
      </div>
    </Link>
  );
}
