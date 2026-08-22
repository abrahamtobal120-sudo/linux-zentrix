-- Zentrix Parental Control Cloud schema (initial secure foundation)
-- Apply in Supabase SQL editor. This file never contains service_role secrets.

create extension if not exists pgcrypto;

create table if not exists public.zentrix_families (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 1 and 120),
  owner_user_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create table if not exists public.zentrix_family_members (
  family_id uuid not null references public.zentrix_families(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('owner','parent')),
  created_at timestamptz not null default now(),
  primary key (family_id, user_id)
);

create table if not exists public.zentrix_devices (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.zentrix_families(id) on delete cascade,
  name text not null,
  device_public_id text unique not null,
  paired boolean not null default false,
  paired_at timestamptz,
  last_seen timestamptz,
  status text not null default 'offline',
  created_at timestamptz not null default now()
);

create table if not exists public.zentrix_device_pairings (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.zentrix_families(id) on delete cascade,
  device_id uuid not null references public.zentrix_devices(id) on delete cascade,
  code_hash text not null,
  expires_at timestamptz not null,
  used_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.zentrix_device_policies (
  device_id uuid primary key references public.zentrix_devices(id) on delete cascade,
  family_id uuid not null references public.zentrix_families(id) on delete cascade,
  version bigint not null default 1,
  policy jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists public.zentrix_remote_commands (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.zentrix_families(id) on delete cascade,
  device_id uuid not null references public.zentrix_devices(id) on delete cascade,
  command_type text not null check (command_type in (
    'lock','unlock','extra_time','pause_internet','resume_internet',
    'school_mode','normal_mode','apply_policy'
  )),
  payload jsonb not null default '{}'::jsonb,
  state text not null default 'pending' check (state in ('pending','received','executed','failed','expired')),
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default (now() + interval '30 minutes'),
  received_at timestamptz,
  executed_at timestamptz,
  error text
);

create table if not exists public.zentrix_device_status (
  device_id uuid primary key references public.zentrix_devices(id) on delete cascade,
  family_id uuid not null references public.zentrix_families(id) on delete cascade,
  status text not null default 'offline',
  controlled_user text,
  daily_used_minutes integer not null default 0,
  weekly_used_minutes integer not null default 0,
  remaining_minutes integer not null default 0,
  weekly_remaining_minutes integer not null default 0,
  updated_at timestamptz not null default now()
);

create table if not exists public.zentrix_extra_time_requests (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.zentrix_families(id) on delete cascade,
  device_id uuid not null references public.zentrix_devices(id) on delete cascade,
  controlled_user text not null,
  requested_minutes integer not null check (requested_minutes between 1 and 1440),
  approved_minutes integer,
  state text not null default 'pending' check (state in ('pending','approved','rejected')),
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);

create or replace function public.zentrix_is_family_member(target_family uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.zentrix_family_members m
    where m.family_id = target_family
      and m.user_id = auth.uid()
  ) or exists (
    select 1
    from public.zentrix_families f
    where f.id = target_family
      and f.owner_user_id = auth.uid()
  );
$$;

alter table public.zentrix_families enable row level security;
alter table public.zentrix_family_members enable row level security;
alter table public.zentrix_devices enable row level security;
alter table public.zentrix_device_pairings enable row level security;
alter table public.zentrix_device_policies enable row level security;
alter table public.zentrix_remote_commands enable row level security;
alter table public.zentrix_device_status enable row level security;
alter table public.zentrix_extra_time_requests enable row level security;

-- Parents can only see families they own/belong to.
drop policy if exists zentrix_families_select on public.zentrix_families;
create policy zentrix_families_select on public.zentrix_families
for select to authenticated
using (owner_user_id = auth.uid() or public.zentrix_is_family_member(id));

drop policy if exists zentrix_families_insert on public.zentrix_families;
create policy zentrix_families_insert on public.zentrix_families
for insert to authenticated
with check (owner_user_id = auth.uid());

drop policy if exists zentrix_family_members_all on public.zentrix_family_members;
create policy zentrix_family_members_all on public.zentrix_family_members
for all to authenticated
using (public.zentrix_is_family_member(family_id))
with check (public.zentrix_is_family_member(family_id));

drop policy if exists zentrix_devices_all on public.zentrix_devices;
create policy zentrix_devices_all on public.zentrix_devices
for all to authenticated
using (public.zentrix_is_family_member(family_id))
with check (public.zentrix_is_family_member(family_id));

drop policy if exists zentrix_pairings_all on public.zentrix_device_pairings;
create policy zentrix_pairings_all on public.zentrix_device_pairings
for all to authenticated
using (public.zentrix_is_family_member(family_id))
with check (public.zentrix_is_family_member(family_id));

drop policy if exists zentrix_policies_all on public.zentrix_device_policies;
create policy zentrix_policies_all on public.zentrix_device_policies
for all to authenticated
using (public.zentrix_is_family_member(family_id))
with check (public.zentrix_is_family_member(family_id));

drop policy if exists zentrix_commands_all on public.zentrix_remote_commands;
create policy zentrix_commands_all on public.zentrix_remote_commands
for all to authenticated
using (public.zentrix_is_family_member(family_id))
with check (public.zentrix_is_family_member(family_id));

drop policy if exists zentrix_status_all on public.zentrix_device_status;
create policy zentrix_status_all on public.zentrix_device_status
for all to authenticated
using (public.zentrix_is_family_member(family_id))
with check (public.zentrix_is_family_member(family_id));

drop policy if exists zentrix_requests_all on public.zentrix_extra_time_requests;
create policy zentrix_requests_all on public.zentrix_extra_time_requests
for all to authenticated
using (public.zentrix_is_family_member(family_id))
with check (public.zentrix_is_family_member(family_id));

-- Realtime tables used by Zentrix Parent/device sync.
alter publication supabase_realtime add table public.zentrix_remote_commands;
alter publication supabase_realtime add table public.zentrix_device_policies;
alter publication supabase_realtime add table public.zentrix_device_status;
alter publication supabase_realtime add table public.zentrix_extra_time_requests;
