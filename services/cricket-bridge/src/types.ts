/**
 * Shared types for Cricket Bridge service
 */

export interface CricketAgentRequest {
  text: string;
  source: 'whatsapp';
  team_hint?: string;
}

export interface CricketAgentResponse {
  answer: string;
  meta: {
    intent: string;
    entities: Record<string, any>;
    latency_ms: number;
    request_id: string;
    cache_hit?: boolean;
    rag_hit?: boolean;
  };
}

export interface RelayRequest {
  text: string;
  team_hint?: string;
}

export interface RelayResponse {
  success: boolean;
  response?: string;
  metadata?: any;
  error?: string;
}

export interface HealthResponse {
  ok: boolean;
  connected: boolean;
  me?: string;
  timestamp: string;
}

export interface MessageEvent {
  chatId: string;
  sender: string;
  messageText: string;
  isGroup: boolean;
  timestamp: number;
}

export interface SessionData {
  creds: any;
  keys: any;
}

export interface RateLimitEntry {
  count: number;
  resetTime: number;
}

export interface GroupFilter {
  allowedGroups?: string[];
  triggerPrefix: string;
  mentionTrigger: boolean;
}

export interface LoggerConfig {
  level: string;
  format: 'json' | 'simple';
}

export interface BridgeConfig {
  port: number;
  cricketAgentUrl: string;
  triggerPrefix: string;
  relayToken: string;
  gcsBucket?: string;
  sessionSecretName?: string;
  allowedGroups?: string[];
  logLevel: string;
}
