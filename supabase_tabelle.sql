-- In Supabase: SQL Editor öffnen, alles einfügen und auf "Run" klicken.

create table if not exists loehne (
  id bigint generated always as identity primary key,
  erstellt timestamptz default now(),
  funktion text,
  branche text,
  region text,
  erfahrung int,
  alter_jahre int,
  ausbildung text,
  pensum int,
  lohn_jahr numeric,
  firmengroesse text,
  zufriedenheit int,
  stress int,
  lernen int,
  weiterbildung boolean,
  aufstieg boolean,
  testdaten boolean default false
);

-- Falls die Tabelle schon früher angelegt wurde: Spalte für das Alter nachrüsten
alter table loehne add column if not exists alter_jahre int;

alter table loehne enable row level security;

drop policy if exists "Eintragen erlaubt" on loehne;
drop policy if exists "Lesen erlaubt" on loehne;
create policy "Eintragen erlaubt" on loehne for insert to anon with check (true);
create policy "Lesen erlaubt" on loehne for select to anon using (true);
