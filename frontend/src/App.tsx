import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { KanbanBoard } from '@/components/KanbanBoard';
import { ChatModal } from '@/components/ChatModal';
import { CardFormModal } from '@/components/CardFormModal';
import { Button } from '@/components/ui/Button';
import { Card } from '@/types';
import { MessageSquare, Settings, BarChart3 } from 'lucide-react';
import './index.css';

// Create a client
const queryClient = new QueryClient();

function App() {
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [isChatModalOpen, setIsChatModalOpen] = useState(false);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingCard, setEditingCard] = useState<Card | null>(null);

  const handleChatWithCard = (card: Card) => {
    setSelectedCard(card);
    setIsChatModalOpen(true);
  };

  const handleEditCard = (card: Card) => {
    setEditingCard(card);
    setIsFormModalOpen(true);
  };

  const handleCreateCard = () => {
    setEditingCard(null);
    setIsFormModalOpen(true);
  };

  const handleDeleteCard = async (cardId: number) => {
    if (confirm('Are you sure you want to delete this customer card?')) {
      try {
        // The KanbanBoard component will handle the actual deletion
        window.location.reload(); // Simple refresh for now
      } catch (error) {
        console.error('Failed to delete card:', error);
      }
    }
  };

  const handleFormModalClose = () => {
    setIsFormModalOpen(false);
    setEditingCard(null);
  };

  const handleFormSave = () => {
    // Refresh the board - in a real app you might use React Query invalidation
    window.location.reload();
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                    <BarChart3 className="w-6 h-6 text-white" />
                  </div>
                  <h1 className="text-2xl font-black bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent">
                    💰 Only Sales 🚀
                  </h1>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                {/* Global Chat Button */}
                <Button
                  variant="outline"
                  onClick={() => {
                    setSelectedCard(null);
                    setIsChatModalOpen(true);
                  }}
                  className="flex items-center space-x-2"
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>AI Assistant</span>
                </Button>

                {/* Settings Button */}
                <Button variant="ghost" size="icon">
                  <Settings className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <KanbanBoard
            onEditCard={handleEditCard}
            onDeleteCard={handleDeleteCard}
            onChatWithCard={handleChatWithCard}
            onCreateCard={handleCreateCard}
          />
        </main>

        {/* Modals */}
        <ChatModal
          isOpen={isChatModalOpen}
          onClose={() => setIsChatModalOpen(false)}
          selectedCard={selectedCard}
        />

        <CardFormModal
          isOpen={isFormModalOpen}
          onClose={handleFormModalClose}
          card={editingCard}
          onSave={handleFormSave}
        />

        {/* Floating Action Button for Global Chat */}
        <div className="fixed bottom-6 right-6">
          <Button
            onClick={() => {
              setSelectedCard(null);
              setIsChatModalOpen(true);
            }}
            className="w-14 h-14 rounded-full shadow-lg hover:shadow-xl transition-shadow bg-blue-600 hover:bg-blue-700"
            size="icon"
          >
            <MessageSquare className="w-6 h-6" />
          </Button>
        </div>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span className="font-bold">© 2024 💰 Only Sales 🚀</span>
                <span>•</span>
                <span className="font-medium">🤖 AI-Powered Sales Domination</span>
              </div>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>🤖 Powered by Gemini AI</span>
                <span>•</span>
                <span>📅 Google Calendar</span>
                <span>•</span>
                <span>📧 Email Integration</span>
                <span>•</span>
                <span>🏢 HubSpot CRM</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  );
}

export default App;
