-- SYNTHETIC SEED DATA — for demo and tests only. Not real farmers, not real results.
-- Every UI surface showing these rows displays the "SYNTHETIC DEMO DATA" banner.
-- NOTE: never executed. Demo auth users are created through the Supabase Admin API first;
-- their UUIDs replace the placeholders below.

insert into crops (id, code, name_bn, name_en) values
  (1, 'rice', 'ধান', 'Rice');

-- Classes = unified taxonomy in docs/data/datasets.md §4. Bangla names pending agronomist check.
insert into disease_catalog (id, crop_id, code, name_bn, name_en, pathogen, is_notifiable) values
  (1, 1, 'healthy',               'সুস্থ পাতা',                 'Healthy',               'healthy',   false),
  (2, 1, 'bacterial_leaf_blight', 'ব্যাকটেরিয়াজনিত পাতা পোড়া', 'Bacterial leaf blight', 'bacterial', true),
  (3, 1, 'brown_spot',            'বাদামী দাগ',                 'Brown spot',            'fungal',    false),
  (4, 1, 'narrow_brown_spot',     'সরু বাদামী দাগ',             'Narrow brown spot',     'fungal',    false),
  (5, 1, 'blast',                 'ব্লাস্ট',                     'Blast',                 'fungal',    true),
  (6, 1, 'sheath_blight',         'খোল পোড়া',                  'Sheath blight',         'fungal',    false),
  (7, 1, 'tungro',                'টুংরো',                      'Tungro',                'viral',     true);

-- Placeholder model row: eval_summary deliberately EMPTY until a real evaluation exists.
insert into model_versions (name, semver, architecture, onnx_sha256, threshold, temperature, eval_summary, is_active)
values ('crop-disease-classifier', '0.0.0-placeholder', 'tbd',
        repeat('0', 64), 0.70, 1.0, '{"status": "not trained"}', true);

-- Demo profiles (replace UUIDs with the auth users created for /demo-user and /demo-admin)
-- insert into profiles (id, role, display_name, locale, district, upazila) values
--   ('00000000-0000-0000-0000-00000000d001', 'demo',       'ডেমো কৃষক (Synthetic)',       'bn', 'Dhaka', 'Savar'),
--   ('00000000-0000-0000-0000-00000000d002', 'admin',      'Demo Admin (Synthetic)',      'en', 'Dhaka', 'Savar'),
--   ('00000000-0000-0000-0000-00000000d003', 'agronomist', 'ডেমো কৃষি কর্মকর্তা (Synthetic)', 'bn', 'Dhaka', 'Savar');
