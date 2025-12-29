// Supabase Client Configuration
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Server-side client with service role key
export const createServerClient = () => {
  const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
  return createClient(supabaseUrl, supabaseServiceKey);
};

// Types for database tables
export interface Client {
  id: string;
  created_at: string;
  email: string;
  name: string;
  phone?: string;
  status: "new" | "onboarding" | "active" | "completed";
  metadata: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  client_id: string;
  created_at: string;
  updated_at: string;
  status: "active" | "completed" | "escalated";
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  metadata?: {
    tool_calls?: unknown[];
    form_data?: Record<string, unknown>;
  };
}

export interface KnowledgeItem {
  id: string;
  type: "document" | "faq" | "case_type";
  title: string;
  content: string;
  embedding?: number[];
  created_at: string;
  updated_at: string;
}

// Database helper functions
export const db = {
  clients: {
    async create(data: Partial<Client>) {
      const { data: client, error } = await supabase
        .from("clients")
        .insert(data)
        .select()
        .single();
      if (error) throw error;
      return client;
    },

    async getById(id: string) {
      const { data, error } = await supabase
        .from("clients")
        .select()
        .eq("id", id)
        .single();
      if (error) throw error;
      return data;
    },

    async update(id: string, data: Partial<Client>) {
      const { data: client, error } = await supabase
        .from("clients")
        .update(data)
        .eq("id", id)
        .select()
        .single();
      if (error) throw error;
      return client;
    },
  },

  conversations: {
    async create(clientId: string) {
      const { data, error } = await supabase
        .from("conversations")
        .insert({ client_id: clientId })
        .select()
        .single();
      if (error) throw error;
      return data;
    },

    async getByClientId(clientId: string) {
      const { data, error } = await supabase
        .from("conversations")
        .select()
        .eq("client_id", clientId)
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  },

  messages: {
    async create(data: Partial<Message>) {
      const { data: message, error } = await supabase
        .from("messages")
        .insert(data)
        .select()
        .single();
      if (error) throw error;
      return message;
    },

    async getByConversationId(conversationId: string) {
      const { data, error } = await supabase
        .from("messages")
        .select()
        .eq("conversation_id", conversationId)
        .order("created_at", { ascending: true });
      if (error) throw error;
      return data;
    },
  },

  knowledge: {
    async search(query: string, limit = 5) {
      // For semantic search, use pgvector similarity
      const { data, error } = await supabase.rpc("search_knowledge", {
        query_text: query,
        match_count: limit,
      });
      if (error) throw error;
      return data;
    },

    async getByType(type: KnowledgeItem["type"]) {
      const { data, error } = await supabase
        .from("knowledge_items")
        .select()
        .eq("type", type)
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  },
};
