# API Réponses Détaillées - Documentation

## Vue d'ensemble

Les endpoints détaillés (`/detailed`) retournent les données principales avec leurs relations imbriquées. Cela permet au frontend d'obtenir toutes les données nécessaires en une seule requête.

## 1. Organizations

### GET `/organizations/{org_id}`
Retourne une organisation simple sans les membres.

**Réponse:**
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "description": "Our awesome company",
  "created_at": "2024-03-01T10:00:00Z",
  "created_by": "uuid"
}
```

### GET `/organizations/{org_id}/detailed`
Retourne une organisation **avec tous les membres** (users de organization_member).

**Réponse:**
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "description": "Our awesome company",
  "created_at": "2024-03-01T10:00:00Z",
  "created_by": "uuid",
  "members": [
    {
      "id": "user_uuid_1",
      "name": "Jean Dupont",
      "email": "jean@example.com"
    },
    {
      "id": "user_uuid_2",
      "name": "Marie Martin",
      "email": "marie@example.com"
    }
  ]
}
```

### GET `/organizations/user/{user_id}`
Liste toutes les organisations créées par l'utilisateur (sans members).

### GET `/organizations/user/{user_id}/detailed`
Liste toutes les organisations créées par l'utilisateur **avec tous les membres**.

**Réponse:**
```json
[
  {
    "id": "uuid",
    "name": "Acme Corp",
    "description": "Our awesome company",
    "created_at": "2024-03-01T10:00:00Z",
    "created_by": "user_uuid",
    "members": [
      {
        "id": "user_uuid_1",
        "name": "Jean Dupont",
        "email": "jean@example.com"
      }
    ]
  }
]
```

## 2. Projects

### GET `/projects/{project_id}`
Retourne un projet simple sans les membres.

**Réponse:**
```json
{
  "id": "uuid",
  "name": "i18n Translation Project",
  "description": "Multi-language support",
  "organization_id": "org_uuid",
  "created_by": "user_uuid",
  "source_language": "en",
  "target_languages": ["fr", "es", "de"],
  "created_at": "2024-03-01T10:00:00Z",
  "updated_at": "2024-03-05T15:30:00Z"
}
```

### GET `/projects/{project_id}/detailed`
Retourne un projet **avec tous les membres** (users de project_member).

**Réponse:**
```json
{
  "id": "uuid",
  "name": "i18n Translation Project",
  "description": "Multi-language support",
  "organization_id": "org_uuid",
  "created_by": "user_uuid",
  "source_language": "en",
  "target_languages": ["fr", "es", "de"],
  "created_at": "2024-03-01T10:00:00Z",
  "updated_at": "2024-03-05T15:30:00Z",
  "members": [
    {
      "id": "user_uuid_1",
      "name": "Project Lead",
      "email": "lead@example.com"
    },
    {
      "id": "user_uuid_2",
      "name": "Translator",
      "email": "translator@example.com"
    }
  ]
}
```

### GET `/projects?organization_id={org_id}`
Liste tous les projets d'une organisation (sans members).

### GET `/projects/organization/{organization_id}/detailed`
Liste tous les projets d'une organisation **avec tous les membres**.

**Réponse:**
```json
[
  {
    "id": "project_uuid_1",
    "name": "Project 1",
    ...
    "members": [...]
  },
  {
    "id": "project_uuid_2",
    "name": "Project 2",
    ...
    "members": [...]
  }
]
```

### GET `/projects/user/projects`
Liste tous les projets de l'utilisateur courant (sans members).

### GET `/projects/user/projects/detailed`
Liste tous les projets de l'utilisateur courant **avec tous les membres**.

## 3. Translation Files

### GET `/projects/{project_id}/files/{file_id}`
Retourne un fichier de traduction simple sans les messages.

**Réponse:**
```json
{
  "id": "uuid",
  "project_id": "project_uuid",
  "created_by": "user_uuid",
  "language_code": "fr",
  "language_name": "Français",
  "current_version": 3,
  "created_at": "2024-03-01T10:00:00Z",
  "updated_at": "2024-03-05T15:30:00Z"
}
```

### GET `/projects/{project_id}/files/{file_id}/detailed`
Retourne un fichier de traduction **avec tous les messages**.

**Réponse:**
```json
{
  "id": "uuid",
  "project_id": "project_uuid",
  "created_by": "user_uuid",
  "language_code": "fr",
  "language_name": "Français",
  "current_version": 3,
  "created_at": "2024-03-01T10:00:00Z",
  "updated_at": "2024-03-05T15:30:00Z",
  "messages": [
    {
      "id": "msg_uuid_1",
      "file_id": "uuid",
      "key": "app.title",
      "value": "Mon Application",
      "created_by": "user_uuid_1",
      "reviewed_by": "user_uuid_2"
    },
    {
      "id": "msg_uuid_2",
      "file_id": "uuid",
      "key": "app.description",
      "value": "Description en français",
      "created_by": "user_uuid_1",
      "reviewed_by": null
    }
  ]
}
```

### GET `/projects/{project_id}/files`
Liste tous les fichiers de traduction d'un projet (sans messages).

### GET `/projects/{project_id}/files/detailed`
Liste tous les fichiers de traduction d'un projet **avec tous les messages**.

**Réponse:**
```json
[
  {
    "id": "file_uuid_1",
    "project_id": "project_uuid",
    "language_code": "fr",
    "language_name": "Français",
    ...
    "messages": [...]
  },
  {
    "id": "file_uuid_2",
    "project_id": "project_uuid",
    "language_code": "es",
    "language_name": "Español",
    ...
    "messages": [...]
  }
]
```

## Frontend Usage Examples

### Récupérer une organisation avec tous ses membres

```typescript
// Au lieu de faire 2 requêtes (org + members)
const org = await api.get(`/organizations/${orgId}/detailed`);

// Accès aux données imbriquées
org.members.forEach(member => {
  console.log(`${member.name} (${member.email})`);
});
```

### Charger un projet complet avec ses membres

```typescript
const project = await api.get(`/projects/${projectId}/detailed`);

// Utiliser les données pour afficher la liste des membres
const memberList = project.members.map(m => `${m.name}`).join(', ');
console.log(`Membres du projet: ${memberList}`);
```

### Charger tous les fichiers de traduction avec leurs messages

```typescript
const files = await api.get(`/projects/${projectId}/files/detailed`);

files.forEach(file => {
  console.log(`Fichier ${file.language_name}: ${file.messages.length} messages`);
  
  // Compter les messages approuvés
  const approved = file.messages.filter(m => m.reviewed_by !== null).length;
  console.log(`  Approuvés: ${approved}/${file.messages.length}`);
});
```

## Résumé des Endpoints

| Resource | Simple | Detailed |
|----------|--------|----------|
| **Organization** | `/organizations/{id}` | `/organizations/{id}/detailed` |
| | `/organizations/user/{id}` | `/organizations/user/{id}/detailed` |
| **Project** | `/projects/{id}` | `/projects/{id}/detailed` |
| | `/projects?org={id}` | `/projects/organization/{id}/detailed` |
| | `/projects/user/projects` | `/projects/user/projects/detailed` |
| **TranslationFile** | `/files/{id}` | `/files/{id}/detailed` |
| | `/files?project={id}` | `/files/detailed?project={id}` |

## Notes Importantes

- Les endpoints détaillés incluent **TOUTES** les relations (members/messages)
- Utilisez l'endpoint `/detailed` pour réduire le nombre de requêtes HTTP
- Les relations sont populées dynamiquement depuis les tables `*_member` et `message`
- Les deux `id` et `email` sont inclus pour chaque utilisateur dans les listes de membres
