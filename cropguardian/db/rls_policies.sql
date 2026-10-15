-- Crop Guardian — Row-Level Security policies
-- NOTE: never executed. The API uses the service-role key (bypasses RLS) for server-side
-- work; RLS protects any direct browser access with the anon key and is defence in depth.

create or replace function app_role() returns user_role
language sql stable security definer set search_path = public as $$
  select role from profiles where id = auth.uid()
$$;

create or replace function current_upazila() returns text
language sql stable security definer set search_path = public as $$
  select upazila from profiles where id = auth.uid()
$$;

-- Upazila of any user, for regional agronomist access. SECURITY DEFINER because the
-- caller's own RLS on profiles would hide other users' rows.
create or replace function upazila_of(p_user uuid) returns text
language sql stable security definer set search_path = public as $$
  select upazila from profiles where id = p_user
$$;

-- enable everywhere
alter table profiles            enable row level security;
alter table consents            enable row level security;
alter table crops               enable row level security;
alter table disease_catalog     enable row level security;
alter table farms               enable row level security;
alter table fields              enable row level security;
alter table model_versions      enable row level security;
alter table scans               enable row level security;
alter table diagnoses           enable row level security;
alter table kb_documents        enable row level security;
alter table kb_chunks           enable row level security;
alter table advisories          enable row level security;
alter table citations           enable row level security;
alter table expert_reviews      enable row level security;
alter table feedback_labels     enable row level security;
alter table alerts              enable row level security;
alter table alert_subscriptions enable row level security;
alter table audit_log           enable row level security;

-- profiles: self; admin all. Role column cannot be self-escalated (checked in update policy).
create policy profiles_self_read   on profiles for select using (id = auth.uid() or app_role() = 'admin');
create policy profiles_self_update on profiles for update using (id = auth.uid())
  -- app_role() is SECURITY DEFINER, so it bypasses RLS; a plain subquery on
  -- profiles here would trigger "infinite recursion detected in policy".
  with check (id = auth.uid() and role = app_role());

create policy consents_self on consents for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- public reference data (read-only for everyone)
create policy crops_read   on crops           for select using (true);
create policy disease_read on disease_catalog for select using (true);
create policy models_read  on model_versions  for select using (true);
create policy kbdoc_read   on kb_documents    for select using (retired_at is null);
create policy kbchunk_read on kb_chunks       for select using (true);

-- farms / fields: owner
create policy farms_owner on farms for all using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy fields_owner on fields for all
  using (exists (select 1 from farms f where f.id = farm_id and f.owner_id = auth.uid()))
  with check (exists (select 1 from farms f where f.id = farm_id and f.owner_id = auth.uid()));

-- scans: owner; agronomist reads review cases in their upazila; admin reads all
create policy scans_owner on scans for select using (user_id = auth.uid());
create policy scans_owner_insert on scans for insert with check (user_id = auth.uid());
create policy scans_agronomist on scans for select using (
  app_role() = 'agronomist'
  and upazila_of(scans.user_id) = current_upazila());
create policy scans_admin on scans for select using (app_role() = 'admin');

-- diagnoses / advisories / citations: visible if the scan is visible
create policy diagnoses_via_scan on diagnoses for select
  using (exists (select 1 from scans s where s.id = scan_id));
create policy advisories_via_diag on advisories for select
  using (exists (select 1 from diagnoses d where d.id = diagnosis_id));
create policy citations_via_adv on citations for select
  using (exists (select 1 from advisories a where a.id = advisory_id));

-- reviews: agronomist writes own; admin reads
create policy reviews_agronomist on expert_reviews for all
  using (reviewer_id = auth.uid() and app_role() = 'agronomist')
  with check (reviewer_id = auth.uid() and app_role() = 'agronomist');
create policy reviews_admin on expert_reviews for select using (app_role() = 'admin');
create policy labels_admin on feedback_labels for select using (app_role() = 'admin');

-- alerts: approved/sent are public; drafts only agronomist/admin
create policy alerts_public on alerts for select using (status in ('approved', 'sent'));
create policy alerts_staff  on alerts for select using (app_role() in ('agronomist', 'admin'));

create policy subs_self on alert_subscriptions for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- audit: admin read; writes only via audit_append() (security definer)
create policy audit_admin_read on audit_log for select using (app_role() = 'admin');

-- demo role: read-only everywhere it can see; writes go through API with demo sandboxing
