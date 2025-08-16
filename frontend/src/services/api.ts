import axios from 'axios';
import { Card, CardCreate, CardUpdate, CardsResponse, ChatMessage, ChatResponse, CardStatus } from '@/types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Cards API
export const cardsApi = {
  // Get all cards with optional filtering
  getCards: async (params?: {
    page?: number;
    per_page?: number;
    status?: CardStatus;
    assigned_to?: string;
    search?: string;
  }): Promise<CardsResponse> => {
    const response = await api.get('/cards', { params });
    return response.data;
  },

  // Get specific card
  getCard: async (id: number): Promise<Card> => {
    const response = await api.get(`/cards/${id}`);
    return response.data;
  },

  // Create new card
  createCard: async (card: CardCreate): Promise<Card> => {
    const response = await api.post('/cards', card);
    return response.data;
  },

  // Update card
  updateCard: async (id: number, updates: CardUpdate): Promise<Card> => {
    const response = await api.put(`/cards/${id}`, updates);
    return response.data;
  },

  // Update card status
  updateCardStatus: async (id: number, status: CardStatus): Promise<Card> => {
    console.log(`API: Updating card ${id} to status ${status}`);
    try {
      const response = await api.patch(`/cards/${id}/status`, { status });
      console.log('API: Card status updated successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('API: Failed to update card status:', error);
      throw error;
    }
  },

  // Delete card
  deleteCard: async (id: number): Promise<void> => {
    await api.delete(`/cards/${id}`);
  },

  // Get cards summary statistics
  getCardsSummary: async (): Promise<any> => {
    const response = await api.get('/cards/stats/summary');
    return response.data;
  },
};

// Chat API
export const chatApi = {
  // Send message to AI assistant
  sendMessage: async (message: ChatMessage): Promise<ChatResponse> => {
    const response = await api.post('/chat/message', message);
    return response.data;
  },

  // Get customer insights
  getCustomerInsights: async (customerId: number): Promise<any> => {
    const response = await api.post(`/chat/insights/${customerId}`);
    return response.data;
  },

  // Get email suggestions
  getEmailSuggestion: async (customerId: number, emailType: string = 'follow_up'): Promise<any> => {
    const response = await api.post(`/chat/email-suggestion/${customerId}?email_type=${emailType}`);
    return response.data;
  },
};

// WebSocket connection for real-time chat
export class ChatWebSocket {
  private ws: WebSocket | null = null;
  private messageHandlers: ((message: string) => void)[] = [];

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/chat/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
          console.log('WebSocket connected');
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          this.messageHandlers.forEach(handler => handler(event.data));
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
        
        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  sendMessage(message: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(message);
    }
  }

  onMessage(handler: (message: string) => void): void {
    this.messageHandlers.push(handler);
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.messageHandlers = [];
  }
}

export default api;
