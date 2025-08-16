import React, { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { chatApi, ChatWebSocket } from '@/services/api';
import { Card } from '@/types';
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  Calendar, 
  Mail, 
  Building,
  Lightbulb,
  MessageSquare,
  X,
  Trash2
} from 'lucide-react';
import { formatDate } from '@/lib/utils';

interface ChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedCard?: Card | null;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  functionCalls?: any[];
  functionResults?: any[];
}

export const ChatModal: React.FC<ChatModalProps> = ({
  isOpen,
  onClose,
  selectedCard
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [insights, setInsights] = useState<any>(null);
  const [emailSuggestion, setEmailSuggestion] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<ChatWebSocket | null>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize chat when modal opens
  useEffect(() => {
    if (isOpen && selectedCard) {
      initializeChat();
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    };
  }, [isOpen, selectedCard]);

  const initializeChat = async () => {
    // Clear previous chat
    setMessages([]);
    setInsights(null);
    setEmailSuggestion(null);

    // Add welcome message
    const welcomeMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'assistant',
      content: selectedCard 
        ? `Hi! I'm your AI sales assistant. I can help you with ${selectedCard.customer_name} from ${selectedCard.company || 'their company'}. I can schedule meetings, send emails, fetch CRM data, and provide insights. How can I assist you today?`
        : "Hi! I'm your AI sales assistant. How can I help you today?",
      timestamp: new Date()
    };

    setMessages([welcomeMessage]);

    // Load customer insights if card is selected
    if (selectedCard) {
      loadCustomerInsights();
    }
  };

  const loadCustomerInsights = async () => {
    if (!selectedCard) return;

    try {
      const insights = await chatApi.getCustomerInsights(selectedCard.id);
      setInsights(insights);
    } catch (error) {
      console.error('Failed to load customer insights:', error);
    }
  };

  const loadEmailSuggestion = async (emailType: string = 'follow_up') => {
    if (!selectedCard) return;

    try {
      const suggestion = await chatApi.getEmailSuggestion(selectedCard.id, emailType);
      setEmailSuggestion(suggestion);
    } catch (error) {
      console.error('Failed to load email suggestion:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: inputMessage,
        conversation_id: undefined
      });

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        functionCalls: response.function_calls,
        functionResults: response.function_results
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setInsights(null);
    setEmailSuggestion(null);
    
    // Add welcome message back
    const welcomeMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'assistant',
      content: selectedCard 
        ? `Hi! I'm your AI sales assistant. I can help you with ${selectedCard.customer_name} from ${selectedCard.company || 'their company'}. I can schedule meetings, send emails, fetch CRM data, and provide insights. How can I assist you today?`
        : "Hi! I'm your AI sales assistant. How can I help you today?",
      timestamp: new Date()
    };

    setMessages([welcomeMessage]);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center space-x-2">
              <MessageSquare className="w-5 h-5 text-blue-600" />
              <span>AI Sales Assistant</span>
              {selectedCard && (
                <Badge variant="outline" className="ml-2">
                  {selectedCard.customer_name}
                </Badge>
              )}
            </DialogTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={clearChat}
              className="flex items-center space-x-1 text-gray-600 hover:text-gray-800"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear Chat</span>
            </Button>
          </div>
          <DialogDescription>
            Get AI-powered insights, schedule meetings, and manage your sales pipeline
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-1 space-x-4 overflow-hidden">
          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 rounded-lg">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] p-3 rounded-lg chat-message ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border border-gray-200'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {message.role === 'assistant' && (
                        <Bot className="w-4 h-4 mt-1 text-blue-600 flex-shrink-0" />
                      )}
                      {message.role === 'user' && (
                        <User className="w-4 h-4 mt-1 text-white flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        
                        {/* Function Results */}
                        {message.functionResults && message.functionResults.length > 0 && (
                          <div className="mt-2 space-y-2">
                            {message.functionResults.map((result, index) => (
                              <div key={index} className="bg-blue-50 p-2 rounded text-xs">
                                <strong>Action Result:</strong> {JSON.stringify(result, null, 2)}
                              </div>
                            ))}
                          </div>
                        )}
                        
                        <p className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 p-3 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Bot className="w-4 h-4 text-blue-600" />
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm text-gray-600">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex space-x-2 mt-4">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about sales, scheduling, or customer management..."
                className="flex-1"
                disabled={isLoading}
              />
              <Button onClick={sendMessage} disabled={isLoading || !inputMessage.trim()}>
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Sidebar with Customer Info and Quick Actions */}
          {selectedCard && (
            <div className="w-80 border-l border-gray-200 pl-4 space-y-4">
              {/* Customer Info */}
              <div className="bg-white p-4 rounded-lg border">
                <h3 className="font-semibold text-gray-900 mb-3">Customer Details</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <User className="w-4 h-4 mr-2 text-gray-400" />
                    <span>{selectedCard.customer_name}</span>
                  </div>
                  {selectedCard.company && (
                    <div className="flex items-center">
                      <Building className="w-4 h-4 mr-2 text-gray-400" />
                      <span>{selectedCard.company}</span>
                    </div>
                  )}
                  {selectedCard.email && (
                    <div className="flex items-center">
                      <Mail className="w-4 h-4 mr-2 text-gray-400" />
                      <span className="truncate">{selectedCard.email}</span>
                    </div>
                  )}
                  {selectedCard.last_contact_date && (
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                      <span>Last contact: {formatDate(selectedCard.last_contact_date)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-white p-4 rounded-lg border">
                <h3 className="font-semibold text-gray-900 mb-3">Quick Actions</h3>
                <div className="space-y-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => loadCustomerInsights()}
                  >
                    <Lightbulb className="w-4 h-4 mr-2" />
                    Get Insights
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => loadEmailSuggestion('follow_up')}
                  >
                    <Mail className="w-4 h-4 mr-2" />
                    Email Suggestion
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => setInputMessage('Schedule a meeting with this customer')}
                  >
                    <Calendar className="w-4 h-4 mr-2" />
                    Schedule Meeting
                  </Button>
                </div>
              </div>

              {/* AI Insights */}
              {insights && (
                <div className="bg-blue-50 p-4 rounded-lg border">
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <Lightbulb className="w-4 h-4 mr-2 text-blue-600" />
                    AI Insights
                  </h3>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {insights.insights}
                  </p>
                </div>
              )}

              {/* Email Suggestion */}
              {emailSuggestion && (
                <div className="bg-green-50 p-4 rounded-lg border">
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <Mail className="w-4 h-4 mr-2 text-green-600" />
                    Email Suggestion
                  </h3>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {emailSuggestion.email_content}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
