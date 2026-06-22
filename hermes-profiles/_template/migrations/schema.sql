-- Data Schema for {{agent_name}} — {{vertical_name}} Agent
--
-- This schema defines the data layer for the vertical agent.
-- The factory generates this from the vertical's integration requirements.
-- Deploy to Supabase (or any PostgreSQL database) at setup time.

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- ===========================================================================
-- Clients (the SMB that deploys this agent)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name TEXT NOT NULL,
    company_specialty TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- Client-specific configuration (resolves template variables)
    config JSONB DEFAULT '{}'::jsonb
);

-- ===========================================================================
-- Users (the SMB's customers who interact with the agent)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    name TEXT,
    company TEXT,
    phone TEXT,
    email TEXT,
    onboarding_complete BOOLEAN DEFAULT FALSE,
    onboarding_state TEXT DEFAULT 'greeting',
    collected_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- {{case_noun_table}} (the primary work item — quotes, cases, appointments)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS {{case_noun_table}} (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    case_type TEXT,
    description TEXT,
    status TEXT DEFAULT 'new',
    deadline TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- Knowledge Base (RAG — embedded documents for the consultation mode)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    source TEXT,
    content TEXT,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding
    ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops);
