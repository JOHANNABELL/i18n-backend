# Exemples cURL - Endpoints Détaillés

## Configuration

Remplacez les variables avant d'exécuter:
- `{BASE_URL}` = votre URL API (ex: `http://localhost:8000`)
- `{TOKEN}` = votre JWT token
- `{ORG_ID}` = ID de l'organisation
- `{PROJECT_ID}` = ID du projet
- `{FILE_ID}` = ID du fichier de traduction
- `{USER_ID}` = ID de l'utilisateur

```bash
BASE_URL="http://localhost:8000"
TOKEN="your_jwt_token_here"
ORG_ID="550e8400-e29b-41d4-a716-446655440000"
PROJECT_ID="660e8400-e29b-41d4-a716-446655440000"
FILE_ID="770e8400-e29b-41d4-a716-446655440000"
USER_ID="880e8400-e29b-41d4-a716-446655440000"
```

---

## 1. Organizations

### 1.1 GET Organisation Simple
```bash
curl -X GET "$BASE_URL/organizations/$ORG_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 1.2 GET Organisation avec Membres ⭐
```bash
curl -X GET "$BASE_URL/organizations/$ORG_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Réponse:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Acme Corp",
  "description": "Our awesome company",
  "created_at": "2024-03-01T10:00:00Z",
  "created_by": "880e8400-e29b-41d4-a716-446655440000",
  "members": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "name": "Jean Dupont",
      "email": "jean@example.com"
    },
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440000",
      "name": "Marie Martin",
      "email": "marie@example.com"
    }
  ]
}
```

### 1.3 GET Organisations par Utilisateur (Simple)
```bash
curl -X GET "$BASE_URL/organizations/user/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 1.4 GET Organisations par Utilisateur avec Membres ⭐
```bash
curl -X GET "$BASE_URL/organizations/user/$USER_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Réponse:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Acme Corp",
    "description": "Main organization",
    "created_at": "2024-03-01T10:00:00Z",
    "created_by": "880e8400-e29b-41d4-a716-446655440000",
    "members": [...]
  },
  {
    "id": "551e8400-e29b-41d4-a716-446655440000",
    "name": "Dev Team",
    "description": "Development team org",
    "created_at": "2024-03-02T10:00:00Z",
    "created_by": "880e8400-e29b-41d4-a716-446655440000",
    "members": [...]
  }
]
```

### 1.5 CREATE Organisation
```bash
curl -X POST "$BASE_URL/organizations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Organization",
    "description": "Description of the new organization"
  }'
```

### 1.6 UPDATE Organisation
```bash
curl -X PUT "$BASE_URL/organizations/$ORG_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Organization Name",
    "description": "Updated description"
  }'
```

### 1.7 DELETE Organisation
```bash
curl -X DELETE "$BASE_URL/organizations/$ORG_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

---

## 2. Projects

### 2.1 GET Projet Simple
```bash
curl -X GET "$BASE_URL/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 2.2 GET Projet avec Membres ⭐
```bash
curl -X GET "$BASE_URL/projects/$PROJECT_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Réponse:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "name": "i18n Translation Project",
  "description": "Multi-language support",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_by": "880e8400-e29b-41d4-a716-446655440000",
  "source_language": "en",
  "target_languages": ["fr", "es", "de"],
  "created_at": "2024-03-01T10:00:00Z",
  "updated_at": "2024-03-05T15:30:00Z",
  "members": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "name": "Project Lead",
      "email": "lead@example.com"
    },
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440000",
      "name": "Translator",
      "email": "translator@example.com"
    }
  ]
}
```

### 2.3 LIST Projets par Organisation (Simple)
```bash
curl -X GET "$BASE_URL/projects?organization_id=$ORG_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 2.4 LIST Projets par Organisation avec Membres ⭐
```bash
curl -X GET "$BASE_URL/projects/organization/$ORG_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Réponse:**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "name": "Project 1",
    "description": "First project",
    ...
    "members": [...]
  },
  {
    "id": "661e8400-e29b-41d4-a716-446655440000",
    "name": "Project 2",
    "description": "Second project",
    ...
    "members": [...]
  }
]
```

### 2.5 LIST Projets de l'Utilisateur (Simple)
```bash
curl -X GET "$BASE_URL/projects/user/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 2.6 LIST Projets de l'Utilisateur avec Membres ⭐
```bash
curl -X GET "$BASE_URL/projects/user/projects/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 2.7 CREATE Projet
```bash
curl -X POST "$BASE_URL/projects?organization_id=$ORG_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Translation Project",
    "description": "Project description",
    "source_language": "en",
    "target_languages": ["fr", "es", "de"]
  }'
```

### 2.8 UPDATE Projet
```bash
curl -X PATCH "$BASE_URL/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Project Name",
    "description": "Updated description",
    "source_language": "en",
    "target_languages": ["fr", "es", "de", "it"]
  }'
```

---

## 3. Translation Files

### 3.1 GET Fichier Simple
```bash
curl -X GET "$BASE_URL/projects/$PROJECT_ID/files/$FILE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 3.2 GET Fichier avec Messages ⭐
```bash
curl -X GET "$BASE_URL/projects/$PROJECT_ID/files/$FILE_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Réponse:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "created_by": "880e8400-e29b-41d4-a716-446655440000",
  "language_code": "fr",
  "language_name": "Français",
  "current_version": 3,
  "created_at": "2024-03-01T10:00:00Z",
  "updated_at": "2024-03-05T15:30:00Z",
  "messages": [
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440000",
      "file_id": "770e8400-e29b-41d4-a716-446655440000",
      "key": "app.title",
      "value": "Mon Application",
      "created_by": "880e8400-e29b-41d4-a716-446655440000",
      "reviewed_by": "990e8400-e29b-41d4-a716-446655440000"
    },
    {
      "id": "cc0e8400-e29b-41d4-a716-446655440000",
      "file_id": "770e8400-e29b-41d4-a716-446655440000",
      "key": "app.subtitle",
      "value": "Sous-titre en français",
      "created_by": "880e8400-e29b-41d4-a716-446655440000",
      "reviewed_by": null
    }
  ]
}
```

### 3.3 LIST Fichiers d'un Projet (Simple)
```bash
curl -X GET "$BASE_URL/projects/$PROJECT_ID/files" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 3.4 LIST Fichiers d'un Projet avec Messages ⭐
```bash
curl -X GET "$BASE_URL/projects/$PROJECT_ID/files/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Réponse:**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "language_code": "fr",
    "language_name": "Français",
    ...
    "messages": [...]
  },
  {
    "id": "771e8400-e29b-41d4-a716-446655440000",
    "language_code": "es",
    "language_name": "Español",
    ...
    "messages": [...]
  }
]
```

### 3.5 CREATE Fichier de Traduction
```bash
curl -X POST "$BASE_URL/projects/$PROJECT_ID/files" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "language_code": "de",
    "language_name": "Deutsch"
  }'
```

### 3.6 UPDATE Fichier
```bash
curl -X PATCH "$BASE_URL/projects/$PROJECT_ID/files/$FILE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "language_name": "German"
  }'
```

### 3.7 DELETE Fichier
```bash
curl -X DELETE "$BASE_URL/projects/$PROJECT_ID/files/$FILE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 3.8 EXPORT Fichier
```bash
curl -X GET "$BASE_URL/projects/$PROJECT_ID/files/$FILE_ID/export" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Réponse:**
```json
{
  "language_code": "fr",
  "language_name": "Français",
  "version": 3,
  "messages": [
    {
      "key": "app.title",
      "value": "Mon Application",
      "status": "reviewed",
      "comment": null
    },
    {
      "key": "app.subtitle",
      "value": "Sous-titre",
      "status": "pending",
      "comment": "À réviser"
    }
  ],
  "exported_at": "2024-03-05T15:30:00Z"
}
```

---

## Scripts Utiles

### Test rapide avec jq (affiche les membres)
```bash
curl -s -X GET "$BASE_URL/organizations/$ORG_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | \
  jq '.members[] | {name, email}'
```

### Compter les messages approuvés
```bash
curl -s -X GET "$BASE_URL/projects/$PROJECT_ID/files/$FILE_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | \
  jq '[.messages[] | select(.reviewed_by != null)] | length'
```

### Exporter tous les fichiers en JSON
```bash
for FILE_ID in $(curl -s -X GET "$BASE_URL/projects/$PROJECT_ID/files" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.[].id'); do
  echo "Exporting $FILE_ID..."
  curl -s -X GET "$BASE_URL/projects/$PROJECT_ID/files/$FILE_ID/export" \
    -H "Authorization: Bearer $TOKEN" > "export_$FILE_ID.json"
done
```

---

## Debugging

### Vérifier les headers requis
```bash
# Sans Authorization header (doit échouer avec 401)
curl -X GET "$BASE_URL/organizations/$ORG_ID/detailed" \
  -H "Content-Type: application/json" \
  -v
```

### Voir tous les headers de réponse
```bash
curl -X GET "$BASE_URL/organizations/$ORG_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -i
```

### Formatage Pretty JSON
```bash
curl -s -X GET "$BASE_URL/organizations/$ORG_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### Mesurer le temps de réponse
```bash
curl -w "\nTime: %{time_total}s\n" \
  -X GET "$BASE_URL/organizations/$ORG_ID/detailed" \
  -H "Authorization: Bearer $TOKEN"
```
