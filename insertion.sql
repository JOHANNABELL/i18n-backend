-- -------------------------------
-- Script SQL de seed pour i18n
-- -------------------------------

-- Insérer les utilisateurs
INSERT INTO users (id, first_name, last_name, email, password_hash, created_at)
VALUES 
  (gen_random_uuid(), 'Alice Admin', 'Admin', 'alice@example.com', 'hashed_pw1', NOW()),
  (gen_random_uuid(), 'Bob Translator', 'Admin','bob@example.com', 'hashed_pw2', NOW()),
  (gen_random_uuid(), 'Charlie Reviewer','Admin', 'charlie@example.com', 'hashed_pw3', NOW());
-- Récupérer les UUID générés pour les utilisateurs-- (nécessaire pour les relations)
WITH user_ids AS (
  SELECT id, email FROM users
)
SELECT * FROM user_ids;

-- Créer l'organisation
INSERT INTO organizations (id, name, description, created_at)
VALUES (
  gen_random_uuid(),
  'OpenAI Org',
  'Just a fantastic AI organisation',
  NOW()
);

-- Récupérer l'UUID de l'organisation
WITH org_id AS (
  SELECT id FROM organizations WHERE name='OpenAI Org'
)
SELECT * FROM org_id;

-- Ajouter les membres de l'organisation
-- Ici il faudra remplacer <org_id> et <user_id> par les vrais UUID récupérés
INSERT INTO organization_members (id, organization_id, user_id, role, created_at)
VALUES
  (gen_random_uuid(), '4d40b345-59c3-4849-b0a8-f742202f2a42', '68be437a-3be2-49f6-a084-3126ecc2561c', 'ADMIN', NOW()),
  (gen_random_uuid(), '4d40b345-59c3-4849-b0a8-f742202f2a42', '220d79cf-2bc1-4741-bb77-cd17d6d76066', 'MEMBER', NOW()),
  (gen_random_uuid(), '4d40b345-59c3-4849-b0a8-f742202f2a42', '03f760b6-364a-4082-a1f4-b3e264cca4ee', 'MEMBER', NOW());

-- Créer le projet
INSERT INTO projects (id, name, description, organization_id, source_language, target_languages, created_at)
VALUES
  (gen_random_uuid(), 
   'i18n Platform', 
   'Gestion centralisée de l''internationalisation',
   '4d40b345-59c3-4849-b0a8-f742202f2a42',
   'en',
   'fr,es,de',
   NOW()
  );

WITH project_id AS (
  SELECT id FROM projects WHERE name='i18n Platform'
)
SELECT * FROM project_id;
-- Ajouter les membres du projet
INSERT INTO project_members (id, project_id, user_id, role, created_at)
VALUES
  (gen_random_uuid(), '307b944f-6f8c-4b15-a69e-d80dd109cc32', '68be437a-3be2-49f6-a084-3126ecc2561c', 'LEAD', NOW()),
  (gen_random_uuid(), '307b944f-6f8c-4b15-a69e-d80dd109cc32', '220d79cf-2bc1-4741-bb77-cd17d6d76066', 'TRANSLATOR', NOW()),
  (gen_random_uuid(), '51bcf6b1-62dd-46a1-bab4-d7a9bfcaa512', '03f760b6-364a-4082-a1f4-b3e264cca4ee', 'REVIEWER', NOW());

-- Créer le fichier de traduction
INSERT INTO translation_files (id, project_id, filename, version, created_at)
VALUES
  (gen_random_uuid(), '307b944f-6f8c-4b15-a69e-d80dd109cc32', 'messages_en.json', '1.0.0', NOW());

-- Ajouter les messages
INSERT INTO messages (id, project_id, key, language, value, created_at)
VALUES
  (gen_random_uuid(), '307b944f-6f8c-4b15-a69e-d80dd109cc32', 'welcome_message', 'en', 'Welcome to the platform', NOW()),
  (gen_random_uuid(), '307b944f-6f8c-4b15-a69e-d80dd109cc32', 'logout_message', 'en', 'You have been logged out', NOW());