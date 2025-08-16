import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Card, CardCreate, CardUpdate, CardStatus, CardPriority } from '@/types';
import { cardsApi } from '@/services/api';
import { 
  User, 
  Building, 
  Mail, 
  Phone, 
  FileText, 
  Calendar,
  UserCheck
} from 'lucide-react';

interface CardFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  card?: Card | null;
  onSave: () => void;
}

export const CardFormModal: React.FC<CardFormModalProps> = ({
  isOpen,
  onClose,
  card,
  onSave
}) => {
  const [formData, setFormData] = useState<CardCreate>({
    customer_name: '',
    company: '',
    email: '',
    phone: '',
    status: CardStatus.TO_REACH,
    priority: CardPriority.MEDIUM,
    notes: '',
    assigned_to: '',
    next_followup_date: ''
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Initialize form when modal opens or card changes
  useEffect(() => {
    if (isOpen) {
      if (card) {
        // Edit mode - populate form with card data
        setFormData({
          customer_name: card.customer_name,
          company: card.company || '',
          email: card.email || '',
          phone: card.phone || '',
          status: card.status,
          priority: card.priority,
          notes: card.notes || '',
          assigned_to: card.assigned_to || '',
          next_followup_date: card.next_followup_date 
            ? new Date(card.next_followup_date).toISOString().split('T')[0] 
            : ''
        });
      } else {
        // Create mode - reset form
        setFormData({
          customer_name: '',
          company: '',
          email: '',
          phone: '',
          status: CardStatus.TO_REACH,
          priority: CardPriority.MEDIUM,
          notes: '',
          assigned_to: '',
          next_followup_date: ''
        });
      }
      setErrors({});
    }
  }, [isOpen, card]);

  const handleInputChange = (field: keyof CardCreate, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.customer_name.trim()) {
      newErrors.customer_name = 'Customer name is required';
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      // Prepare data for API
      const apiData = {
        ...formData,
        next_followup_date: formData.next_followup_date 
          ? new Date(formData.next_followup_date).toISOString()
          : undefined
      };

      if (card) {
        // Update existing card
        await cardsApi.updateCard(card.id, apiData as CardUpdate);
      } else {
        // Create new card
        await cardsApi.createCard(apiData);
      }

      onSave();
      onClose();
    } catch (error) {
      console.error('Failed to save card:', error);
      // Handle API errors here
    } finally {
      setIsLoading(false);
    }
  };

  const isEditMode = !!card;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {isEditMode ? 'Edit Customer' : 'Add New Customer'}
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-4">
            {/* Customer Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User className="w-4 h-4 inline mr-2" />
                Customer Name *
              </label>
              <Input
                value={formData.customer_name}
                onChange={(e) => handleInputChange('customer_name', e.target.value)}
                placeholder="Enter customer name"
                className={errors.customer_name ? 'border-red-500' : ''}
              />
              {errors.customer_name && (
                <p className="text-red-500 text-xs mt-1">{errors.customer_name}</p>
              )}
            </div>

            {/* Company */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Building className="w-4 h-4 inline mr-2" />
                Company
              </label>
              <Input
                value={formData.company}
                onChange={(e) => handleInputChange('company', e.target.value)}
                placeholder="Enter company name"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline mr-2" />
                Email
              </label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="Enter email address"
                className={errors.email ? 'border-red-500' : ''}
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1">{errors.email}</p>
              )}
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Phone className="w-4 h-4 inline mr-2" />
                Phone
              </label>
              <Input
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                placeholder="Enter phone number"
              />
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-4">
            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => handleInputChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={CardStatus.TO_REACH}>To Reach</option>
                <option value={CardStatus.IN_PROGRESS}>In Progress</option>
                <option value={CardStatus.REACHED_OUT}>Reached Out</option>
                <option value={CardStatus.FOLLOWUP}>Follow-up</option>
              </select>
            </div>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => handleInputChange('priority', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={CardPriority.LOW}>Low</option>
                <option value={CardPriority.MEDIUM}>Medium</option>
                <option value={CardPriority.HIGH}>High</option>
              </select>
            </div>

            {/* Assigned To */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <UserCheck className="w-4 h-4 inline mr-2" />
                Assigned To
              </label>
              <Input
                value={formData.assigned_to}
                onChange={(e) => handleInputChange('assigned_to', e.target.value)}
                placeholder="Enter assignee name"
              />
            </div>

            {/* Next Follow-up Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-2" />
                Next Follow-up Date
              </label>
              <Input
                type="date"
                value={formData.next_followup_date}
                onChange={(e) => handleInputChange('next_followup_date', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Notes - Full Width */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <FileText className="w-4 h-4 inline mr-2" />
            Notes
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => handleInputChange('notes', e.target.value)}
            placeholder="Add any additional notes..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={isLoading}>
            {isLoading ? 'Saving...' : (isEditMode ? 'Update Customer' : 'Add Customer')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
