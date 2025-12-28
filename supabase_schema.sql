create table if not exists public.uploads (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  filename text not null,
  blob_url text not null,
  task_type text not null,
  target_column text,
  row_count integer not null,
  -- Store a small preview of the results for UX/debugging
  result_preview jsonb,
  -- Optionally, you can add user_id if you enable auth
  user_id uuid
);

-- Optional: enable row-level security and policies later if you add auth
-- alter table public.uploads enable row level security;