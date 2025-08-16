export interface Card {
  id: number;
  customer_name: string;
  company?: string;
  email?: string;
  phone?: string;
  status: CardStatus;
  priority: CardPriority;
  notes?: string;
  assigned_to?: string;
  last_contact_date?: string;
  next_followup_date?: string;
  created_at: string;
  updated_at: string;
}

export enum CardStatus {
  TO_REACH = "to_reach",
  IN_PROGRESS = "in_progress",
  REACHED_OUT = "reached_out",
  FOLLOWUP = "followup"
}

export enum CardPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high"
}

export interface CardCreate {
  customer_name: string;
  company?: string;
  email?: string;
  phone?: string;
  status?: CardStatus;
  priority?: CardPriority;
  notes?: string;
  assigned_to?: string;
  next_followup_date?: string;
}

export interface CardUpdate extends Partial<CardCreate> {}

export interface CardsResponse {
  cards: Card[];
  total: number;
  page: number;
  per_page: number;
}

export interface ChatMessage {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  status: string;
  function_calls?: any[];
  function_results?: any[];
  conversation_id?: string;
}

export interface Column {
  id: CardStatus;
  title: string;
  cards: Card[];
  color: string;
}

export const COLUMN_CONFIG: Record<CardStatus, { title: string; color: string }> = {
  [CardStatus.TO_REACH]: {
    title: "To Reach",
    color: "bg-slate-100 border-slate-300"
  },
  [CardStatus.IN_PROGRESS]: {
    title: "In Progress", 
    color: "bg-blue-100 border-blue-300"
  },
  [CardStatus.REACHED_OUT]: {
    title: "Reached Out",
    color: "bg-green-100 border-green-300"
  },
  [CardStatus.FOLLOWUP]: {
    title: "Follow-up",
    color: "bg-orange-100 border-orange-300"
  }
};

export const PRIORITY_COLORS: Record<CardPriority, string> = {
  [CardPriority.LOW]: "text-green-600 bg-green-100",
  [CardPriority.MEDIUM]: "text-yellow-600 bg-yellow-100", 
  [CardPriority.HIGH]: "text-red-600 bg-red-100"
};
