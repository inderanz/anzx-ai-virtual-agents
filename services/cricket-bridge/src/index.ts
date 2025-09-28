/**
 * Cricket Bridge Service
 * Production-ready Node service using Baileys MD that relays group messages to cricket-agent
 */

import express from 'express';
import { makeWASocket, DisconnectReason, useMultiFileAuthState, ConnectionState } from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import dotenv from 'dotenv';
import qrcode from 'qrcode-terminal';
import { join } from 'path';

import { BridgeConfig, HealthResponse, RelayRequest, RelayResponse, MessageEvent } from './types';
import CricketLogger from './logger';
import { CricketForwarder } from './forwarder';
import { SessionManager } from './utils/session';
import { MessageFilters } from './utils/filters';

// Load environment variables
dotenv.config();

// Configuration
const config: BridgeConfig = {
  port: parseInt(process.env.PORT || '8003'),
  cricketAgentUrl: process.env.CRICKET_AGENT_URL || 'http://localhost:8002',
  triggerPrefix: process.env.TRIGGER_PREFIX || '!cscc',
  relayToken: process.env.RELAY_TOKEN || 'local-dev',
  gcsBucket: process.env.GCS_BUCKET,
  sessionSecretName: process.env.SESSION_SECRET_NAME,
  allowedGroups: process.env.ALLOWED_GROUPS?.split(',').filter(Boolean),
  logLevel: process.env.LOG_LEVEL || 'info'
};

// Initialize logger
const logger = new CricketLogger({ level: config.logLevel, format: 'json' });

// Initialize session manager
const sessionManager = new SessionManager(
  logger,
  config.gcsBucket,
  config.sessionSecretName
);

// Initialize forwarder
const forwarder = new CricketForwarder(
  config.cricketAgentUrl,
  config.relayToken,
  logger
);

// Initialize filters
const filters = new MessageFilters(
  {
    allowedGroups: config.allowedGroups,
    triggerPrefix: config.triggerPrefix,
    mentionTrigger: true
  },
  logger
);

// Express app
const app = express();
app.use(express.json());

// WhatsApp bot class
class CricketBridge {
  private socket: any;
  private isConnected: boolean = false;
  private me: string | undefined;
  private reconnectAttempts: number = 0;
  private readonly maxReconnectAttempts: number = 5;

  constructor() {
    this.initializeWhatsApp();
  }

  private async initializeWhatsApp() {
    try {
      logger.getWinstonLogger().info('Initializing WhatsApp connection...');
      
      // Load session data
      const sessionData = await sessionManager.loadSession();
      let authState: any;

      if (sessionData) {
        // Use loaded session data
        authState = {
          state: sessionData,
          saveCreds: async () => {
            // Save credentials when they update
            await this.saveSession();
          }
        };
      } else {
        // Use file-based auth state for development
        const sessionPath = join(process.cwd(), 'session');
        authState = await useMultiFileAuthState(sessionPath);
      }

      // Create socket
      this.socket = makeWASocket({
        auth: authState.state,
        printQRInTerminal: process.env.NODE_ENV !== 'production',
        logger: logger.getWinstonLogger(),
        browser: ['Cricket Bridge', 'Chrome', '1.0.0'],
        generateHighQualityLinkPreview: true
      });

      // Handle connection updates
      this.socket.ev.on('connection.update', (update: any) => {
        this.handleConnectionUpdate(update);
      });

      // Handle credentials update
      this.socket.ev.on('creds.update', authState.saveCreds);

      // Handle incoming messages
      this.socket.ev.on('messages.upsert', async (m: any) => {
        await this.handleIncomingMessage(m);
      });

      // Handle QR code for development
      this.socket.ev.on('qr', (qr: string) => {
        if (process.env.NODE_ENV !== 'production') {
          console.log('QR Code for WhatsApp login:');
          qrcode.generate(qr, { small: true });
        }
      });

    } catch (error) {
      logger.error('Failed to initialize WhatsApp', error as Error);
      setTimeout(() => this.initializeWhatsApp(), 10000);
    }
  }

  private handleConnectionUpdate(update: any) {
    const { connection, lastDisconnect, qr } = update;
    
    if (connection === 'close') {
      const shouldReconnect = (lastDisconnect?.error as Boom)?.output?.statusCode !== DisconnectReason.loggedOut;
      
      if (shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
        logger.getWinstonLogger().info('Connection closed, attempting reconnect...', { 
          attempt: this.reconnectAttempts + 1 
        });
        this.reconnectAttempts++;
        this.isConnected = false;
        setTimeout(() => this.initializeWhatsApp(), 5000);
      } else {
        logger.disconnect('Connection closed permanently');
        this.isConnected = false;
      }
    } else if (connection === 'open') {
      logger.connect(this.me);
      this.isConnected = true;
      this.reconnectAttempts = 0;
    }
  }

  private async handleIncomingMessage(messageUpdate: any) {
    try {
      const { messages, type } = messageUpdate;
      
      if (type !== 'notify') return;

      for (const message of messages) {
        const messageText = message.message?.conversation || 
                          message.message?.extendedTextMessage?.text || '';
        
        if (!messageText) continue;

        const chatId = message.key.remoteJid;
        const isGroup = chatId?.endsWith('@g.us');
        const sender = message.key.participant || message.key.remoteJid;
        const messageId = message.key.id;
        
        logger.messageReceived(chatId, sender, messageText.length, isGroup);

        // Check if message should be processed
        if (!filters.shouldProcessMessage(chatId, messageText, isGroup, messageId, this.me)) {
          continue;
        }

        // Process the message
        await this.processMessage({
          chatId,
          sender,
          messageText,
          isGroup,
          timestamp: Date.now()
        });
      }
    } catch (error) {
      logger.error('Error handling incoming message', error as Error);
    }
  }

  private async processMessage(event: MessageEvent) {
    try {
      const startTime = Date.now();
      
      // Clean message text
      const cleanText = filters.cleanMessage(event.messageText, this.me);
      
      if (!cleanText) {
        await this.sendMessage(event.chatId, 'Please ask a cricket-related question.');
        return;
      }

      logger.messageForwarded(event.chatId, cleanText.length, 0);

      // Forward to cricket agent
      const response = await forwarder.forwardMessage({
        text: cleanText,
        source: 'whatsapp',
        team_hint: event.isGroup ? event.chatId : undefined
      });

      const forwardMs = Date.now() - startTime;
      const agentLatencyMs = response.meta?.latency_ms || 0;

      logger.replySent(event.chatId, response.answer.length, agentLatencyMs);

      // Send response back to WhatsApp
      await this.sendMessage(event.chatId, response.answer);

    } catch (error) {
      logger.error('Error processing message', error as Error, {
        chatId: event.chatId,
        messageLength: event.messageText.length
      });
      
      const errorMessage = 'Sorry, I encountered an error processing your cricket question. Please try again.';
      await this.sendMessage(event.chatId, errorMessage);
    }
  }

  private async sendMessage(chatId: string, message: string) {
    try {
      await this.socket.sendMessage(chatId, { text: message });
      logger.getWinstonLogger().info('Message sent successfully', { 
        chatId: logger['anonymizeJid'](chatId), 
        messageLength: message.length 
      });
    } catch (error) {
      logger.error('Failed to send message', error as Error, { chatId });
    }
  }

  private async saveSession() {
    try {
      if (sessionManager.isStorageAvailable()) {
        const sessionData = {
          creds: this.socket.authState.creds,
          keys: this.socket.authState.keys
        };
        await sessionManager.saveSession(sessionData);
      }
    } catch (error) {
      logger.error('Failed to save session', error as Error);
    }
  }

  public async sendToGroup(groupId: string, message: string) {
    await this.sendMessage(groupId, message);
  }

  public isWhatsAppConnected(): boolean {
    return this.isConnected;
  }

  public getMe(): string | undefined {
    return this.me;
  }
}

// Initialize bridge
const cricketBridge = new CricketBridge();

// Health check endpoint
app.get('/healthz', async (req, res) => {
  const health: HealthResponse = {
    ok: true,
    connected: cricketBridge.isWhatsAppConnected(),
    me: cricketBridge.getMe(),
    timestamp: new Date().toISOString()
  };
  
  logger.healthCheck(health.connected, health.me);
  res.json(health);
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  try {
    const metrics = logger.getMetrics();
    const prometheusLines = [
      '# HELP cricket_bridge_messages_total Total number of messages received',
      '# TYPE cricket_bridge_messages_total counter',
      `cricket_bridge_messages_total ${metrics.messageCount}`,
      '',
      '# HELP cricket_bridge_forwards_total Total number of messages forwarded',
      '# TYPE cricket_bridge_forwards_total counter',
      `cricket_bridge_forwards_total ${metrics.forwardCount}`,
      '',
      '# HELP cricket_bridge_replies_total Total number of replies sent',
      '# TYPE cricket_bridge_replies_total counter',
      `cricket_bridge_replies_total ${metrics.replyCount}`,
      '',
      '# HELP cricket_bridge_errors_total Total number of errors',
      '# TYPE cricket_bridge_errors_total counter',
      `cricket_bridge_errors_total ${metrics.errorCount}`,
      '',
      '# HELP cricket_bridge_avg_forward_duration_ms Average forward duration in milliseconds',
      '# TYPE cricket_bridge_avg_forward_duration_ms gauge',
      `cricket_bridge_avg_forward_duration_ms ${metrics.avgForwardMs}`,
      '',
      '# HELP cricket_bridge_avg_agent_latency_ms Average agent latency in milliseconds',
      '# TYPE cricket_bridge_avg_agent_latency_ms gauge',
      `cricket_bridge_avg_agent_latency_ms ${metrics.avgAgentLatencyMs}`
    ];
    
    res.set('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
    res.send(prometheusLines.join('\n'));
  } catch (error) {
    logger.error('Failed to get metrics', error as Error);
    res.status(500).json({ error: 'Failed to retrieve metrics' });
  }
});

// Relay endpoint for external forwarding
app.post('/relay', async (req, res) => {
  try {
    // Validate bearer token
    const token = req.headers['x-relay-token'];
    if (!token || token !== config.relayToken) {
      logger.getWinstonLogger().warn('Invalid relay token', { 
        provided: token ? '***' : 'none' 
      });
      return res.status(401).json({
        success: false,
        error: 'Invalid or missing X-Relay-Token header'
      });
    }

    const { text, team_hint }: RelayRequest = req.body;
    
    if (!text) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: text'
      });
    }

    logger.getWinstonLogger().info('Relay request received', { 
      textLength: text.length,
      teamHint: team_hint 
    });
    
    // Forward to cricket agent
    const response = await forwarder.forwardMessage({
      text,
      source: 'whatsapp',
      team_hint
    });
    
    const relayResponse: RelayResponse = {
      success: true,
      response: response.answer,
      metadata: response.meta
    };
    
    res.json(relayResponse);
    
  } catch (error) {
    logger.error('Relay error', error as Error);
    const relayResponse: RelayResponse = {
      success: false,
      error: 'Failed to process message'
    };
    res.status(500).json(relayResponse);
  }
});

// Start Express server
const server = app.listen(config.port, () => {
  logger.getWinstonLogger().info('Cricket Bridge service started', {
    port: config.port,
    cricketAgentUrl: config.cricketAgentUrl,
    triggerPrefix: config.triggerPrefix,
    storageType: sessionManager.getStorageType(),
    allowedGroups: config.allowedGroups?.length || 0
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.getWinstonLogger().info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.getWinstonLogger().info('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.getWinstonLogger().info('SIGINT received, shutting down gracefully');
  server.close(() => {
    logger.getWinstonLogger().info('Server closed');
    process.exit(0);
  });
});

export default cricketBridge;