-- Supabase Migration: Create debate_history table
-- Created: 2025-12-22

-- Enable pgcrypto for gen_random_uuid() (Supabase 預設已啟用，但明確宣告更安全)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE debate_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic TEXT NOT NULL CHECK (char_length(topic) > 0),
  messages JSONB NOT NULL DEFAULT '[]'::jsonb,
  max_rounds INTEGER NOT NULL DEFAULT 3,
  rounds_completed INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for faster queries by creation date
CREATE INDEX idx_debate_history_created_at ON debate_history(created_at DESC);

-- Row Level Security
-- Public read, service role write (backend uses service_role_key to bypass RLS)
ALTER TABLE debate_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public_read" ON debate_history 
  FOR SELECT 
  USING (true);

-- No INSERT/UPDATE/DELETE policies
-- Backend uses SUPABASE_SERVICE_ROLE_KEY which bypasses RLS
