import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { Card, CardStatus, COLUMN_CONFIG } from '@/types';
import { CustomerCard } from '@/components/CustomerCard';
import { cardsApi } from '@/services/api';
import { Button } from '@/components/ui/Button';
import { Plus, Search, Filter } from 'lucide-react';
import { Input } from '@/components/ui/Input';

interface KanbanBoardProps {
  onEditCard?: (card: Card) => void;
  onDeleteCard?: (id: number) => void;
  onChatWithCard?: (card: Card) => void;
  onCreateCard?: () => void;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  onEditCard,
  onDeleteCard,
  onChatWithCard,
  onCreateCard
}) => {
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<CardStatus | ''>('');

  // Load cards from API
  useEffect(() => {
    loadCards();
  }, [searchTerm, filterStatus]);

  const loadCards = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (searchTerm) params.search = searchTerm;
      if (filterStatus) params.status = filterStatus;
      
      const response = await cardsApi.getCards(params);
      setCards(response.cards);
    } catch (error) {
      console.error('Failed to load cards:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle drag and drop
  const handleDragEnd = async (result: DropResult) => {
    console.log('Drag ended:', result); // Debug log
    
    const { destination, source, draggableId } = result;

    // If dropped outside a droppable area
    if (!destination) {
      console.log('No destination - drag cancelled');
      return;
    }

    // If dropped in the same position
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      console.log('Dropped in same position');
      return;
    }

    const cardId = parseInt(draggableId);
    const newStatus = destination.droppableId as CardStatus;
    
    console.log(`Moving card ${cardId} from ${source.droppableId} to ${newStatus}`);

    try {
      // Optimistically update UI
      setCards(prevCards =>
        prevCards.map(card =>
          card.id === cardId ? { ...card, status: newStatus } : card
        )
      );

      // Update on server
      const updatedCard = await cardsApi.updateCardStatus(cardId, newStatus);
      console.log('Card updated successfully:', updatedCard);
    } catch (error) {
      console.error('Failed to update card status:', error);
      // Revert optimistic update
      loadCards();
    }
  };

  // Group cards by status
  const groupedCards = cards.reduce((acc, card) => {
    if (!acc[card.status]) {
      acc[card.status] = [];
    }
    acc[card.status].push(card);
    return acc;
  }, {} as Record<CardStatus, Card[]>);

  // Ensure all columns exist
  Object.values(CardStatus).forEach(status => {
    if (!groupedCards[status]) {
      groupedCards[status] = [];
    }
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sales Pipeline</h1>
          <p className="text-gray-600">Manage your customer relationships</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search customers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-64"
            />
          </div>

          {/* Filter */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as CardStatus | '')}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            {Object.entries(COLUMN_CONFIG).map(([status, config]) => (
              <option key={status} value={status}>
                {config.title}
              </option>
            ))}
          </select>

          {/* Add Card Button */}
          <Button onClick={onCreateCard}>
            <Plus className="w-4 h-4 mr-2" />
            Add Customer
          </Button>
        </div>
      </div>

      {/* Kanban Board */}
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-4 gap-6 h-full">
          {Object.entries(COLUMN_CONFIG).map(([status, config]) => (
            <div key={status} className="flex flex-col">
              {/* Column Header */}
              <div className={`kanban-column rounded-lg p-4 ${config.color}`}>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-semibold text-gray-800">{config.title}</h2>
                  <span className="bg-white rounded-full px-2 py-1 text-xs font-medium text-gray-600">
                    {groupedCards[status as CardStatus]?.length || 0}
                  </span>
                </div>

                {/* Droppable Area */}
                <Droppable droppableId={status}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`min-h-[500px] ${
                        snapshot.isDraggingOver ? 'bg-blue-50 rounded-lg' : ''
                      }`}
                    >
                      {groupedCards[status as CardStatus]?.map((card, index) => (
                        <Draggable
                          key={card.id}
                          draggableId={card.id.toString()}
                          index={index}
                        >
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                            >
                              <CustomerCard
                                card={card}
                                onEdit={onEditCard}
                                onDelete={onDeleteCard}
                                onChat={onChatWithCard}
                                isDragging={snapshot.isDragging}
                              />
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}

                      {/* Empty State */}
                      {groupedCards[status as CardStatus]?.length === 0 && (
                        <div className="flex items-center justify-center h-32 text-gray-400 text-sm">
                          No customers in this stage
                        </div>
                      )}
                    </div>
                  )}
                </Droppable>
              </div>
            </div>
          ))}
        </div>
      </DragDropContext>
    </div>
  );
};
