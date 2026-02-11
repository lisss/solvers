-- Run this in Supabase SQL Editor to create tables
-- Go to: https://supabase.com/dashboard/project/_/sql/new

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS requests (
    id TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security (RLS) but allow all operations for now
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE requests ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations (you can restrict later)
CREATE POLICY "Allow all operations on agents" ON agents FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on requests" ON requests FOR ALL USING (true) WITH CHECK (true);
