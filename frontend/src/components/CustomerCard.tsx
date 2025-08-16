import React from 'react';
import { Card, CardPriority } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { formatDate, getInitials, truncateText } from '@/lib/utils';
import { 
  Calendar, 
  Mail, 
  Phone, 
  Building, 
  User, 
  MoreVertical,
  MessageSquare,
  Edit,
  Trash2
} from 'lucide-react';
import { PRIORITY_COLORS } from '@/types';

interface CustomerCardProps {
  card: Card;
  onEdit?: (card: Card) => void;
  onDelete?: (id: number) => void;
  onChat?: (card: Card) => void;
  isDragging?: boolean;
}

export const CustomerCard: React.FC<CustomerCardProps> = ({
  card,
  onEdit,
  onDelete,
  onChat,
  isDragging = false
}) => {
  const priorityColor = PRIORITY_COLORS[card.priority];
  
  return (
    <div
      className={`kanban-card bg-white rounded-lg border border-gray-200 p-4 mb-3 shadow-sm ${
        isDragging ? 'opacity-50 rotate-2' : 'hover:shadow-md'
      }`}
    >
      {/* Header with name and priority */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-medium text-sm">
            {getInitials(card.customer_name)}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">
              {truncateText(card.customer_name, 20)}
            </h3>
            {card.company && (
              <p className="text-xs text-gray-500 flex items-center mt-1">
                <Building className="w-3 h-3 mr-1" />
                {truncateText(card.company, 18)}
              </p>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-1">
          <Badge className={`text-xs ${priorityColor}`}>
            {card.priority.toUpperCase()}
          </Badge>
          <Button variant="ghost" size="icon" className="h-6 w-6">
            <MoreVertical className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {/* Contact Information */}
      <div className="space-y-2 mb-3">
        {card.email && (
          <div className="flex items-center text-xs text-gray-600">
            <Mail className="w-3 h-3 mr-2" />
            <span className="truncate">{card.email}</span>
          </div>
        )}
        {card.phone && (
          <div className="flex items-center text-xs text-gray-600">
            <Phone className="w-3 h-3 mr-2" />
            <span>{card.phone}</span>
          </div>
        )}
      </div>

      {/* Notes */}
      {card.notes && (
        <div className="mb-3">
          <p className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
            {truncateText(card.notes, 80)}
          </p>
        </div>
      )}

      {/* Dates */}
      <div className="space-y-1 mb-3 text-xs text-gray-500">
        {card.last_contact_date && (
          <div className="flex items-center">
            <Calendar className="w-3 h-3 mr-2" />
            <span>Last contact: {formatDate(card.last_contact_date)}</span>
          </div>
        )}
        {card.next_followup_date && (
          <div className="flex items-center">
            <Calendar className="w-3 h-3 mr-2" />
            <span className="text-orange-600">
              Follow-up: {formatDate(card.next_followup_date)}
            </span>
          </div>
        )}
      </div>

      {/* Assigned To */}
      {card.assigned_to && (
        <div className="flex items-center text-xs text-gray-600 mb-3">
          <User className="w-3 h-3 mr-2" />
          <span>Assigned to: {card.assigned_to}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between items-center pt-2 border-t border-gray-100">
        <div className="flex space-x-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onChat?.(card)}
            className="h-7 px-2 text-xs"
          >
            <MessageSquare className="w-3 h-3 mr-1" />
            Chat
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onEdit?.(card)}
            className="h-7 px-2 text-xs"
          >
            <Edit className="w-3 h-3 mr-1" />
            Edit
          </Button>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete?.(card.id)}
          className="h-7 px-2 text-xs text-red-600 hover:text-red-700 hover:bg-red-50"
        >
          <Trash2 className="w-3 h-3" />
        </Button>
      </div>

      {/* Updated timestamp */}
      <div className="text-xs text-gray-400 mt-2 text-center">
        Updated {formatDate(card.updated_at)}
      </div>
    </div>
  );
};
