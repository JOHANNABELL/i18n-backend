# Migration Postgres → MongoDB - Guide Complet

## 1. Vue d'ensemble

Cette migration transforme votre système de gestion de traductions de Postgres (modèle relationnel) vers MongoDB (modèle documentaire orienté objet). MongoDB permet une meilleure structuration des objets imbriqués et simplifie la gestion des traductions complexes.

### Avantages de MongoDB pour votre cas d'usage:
- **Schéma flexible**: Adaptation facile aux objets imbriqués
- **Performances**: Moins de jointures, requêtes optimisées
- **Scalabilité**: Sharding horizontal simplifié
- **Traductions imbriquées**: Structure naturelle pour les clés/valeurs imbriquées

---

## 2. Mapping des Tables Postgres → Collections MongoDB

### 2.1 Table `users` → Collection `users`

**Postgres:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**MongoDB:**
```javascript
// Collection: users
{
  _id: ObjectId,           // Auto-generated (ou UUID)
  id: UUID,                // Votre UUID original
  name: String,
  email: String,           // Index: unique
  password_hash: String,
  profile: {
    avatar_url: String,
    bio: String
  },
  roles: [String],         // ["admin", "translator", "lead"]
  created_at: ISODate,
  updated_at: ISODate,
  deleted_at: ISODate,     // Soft delete
  is_active: Boolean
}

// Indexes
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ id: 1 }, { unique: true })
```

---

### 2.2 Table `organizations` → Collection `organizations`

**Postgres:**
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**MongoDB:**
```javascript
// Collection: organizations
{
  _id: ObjectId,
  id: UUID,
  name: String,           // Index
  description: String,
  created_by: UUID,
  members: [              // Embedded array of member references
    {
      user_id: UUID,
      role: String,        // "ADMIN", "MEMBER", "VIEWER"
      joined_at: ISODate,
      permissions: [String]
    }
  ],
  settings: {
    language_default: String,
    timezone: String
  },
  created_at: ISODate,
  updated_at: ISODate,
  deleted_at: ISODate
}

// Indexes
db.organizations.createIndex({ created_by: 1 })
db.organizations.createIndex({ "members.user_id": 1 })
```

---

### 2.3 Table `projects` → Collection `projects`

**Postgres:**
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    source_language VARCHAR(10),
    target_languages TEXT, -- CSV
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**MongoDB:**
```javascript
// Collection: projects
{
  _id: ObjectId,
  id: UUID,
  organization_id: UUID,
  name: String,           // Index
  description: String,
  source_language: String,
  target_languages: [String],  // ["fr", "es", "pt"]
  created_by: UUID,
  members: [              // Embedded members
    {
      user_id: UUID,
      role: String,        // "LEAD", "TRANSLATOR", "REVIEWER", "ADMIN"
      joined_at: ISODate
    }
  ],
  metadata: {
    status: String,       // "active", "archived"
    is_public: Boolean,
    tags: [String]
  },
  created_at: ISODate,
  updated_at: ISODate,
  deleted_at: ISODate
}

// Indexes
db.projects.createIndex({ organization_id: 1 })
db.projects.createIndex({ created_by: 1 })
db.projects.createIndex({ "members.user_id": 1 })
```

---

### 2.4 Table `translation_files` + `messages` → Collection `translation_files` (Embedded)

**Postgres (2 tables séparées):**
```sql
CREATE TABLE translation_files (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    language_code VARCHAR(10),
    language_name VARCHAR(100),
    current_version INT DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    file_id UUID REFERENCES translation_files(id),
    key VARCHAR(500),
    value TEXT,
    comment TEXT,
    status ENUM ('PENDING', 'APPROVED', 'REJECTED'),
    created_by UUID REFERENCES users(id),
    reviewed_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**MongoDB (Structure Imbriquée - NEW!):**
```javascript
// Collection: translation_files
{
  _id: ObjectId,
  id: UUID,
  project_id: UUID,
  language_code: String,     // "fr", "es", "pt"
  language_name: String,     // "French", "Spanish", "Portuguese"
  current_version: Int,
  created_by: UUID,
  
  // OBJETS IMBRIQUÉS - Messages avec structure hiérarchique
  messages: {
    // Structure plate (clé/valeur) - Pour rétro-compatibilité
    "app.header.title": {
      id: UUID,
      key: String,
      value: String,
      comment: String,
      status: String,        // "PENDING", "APPROVED", "REJECTED"
      metadata: {
        created_by: UUID,
        reviewed_by: UUID,
        created_at: ISODate,
        updated_at: ISODate,
        ai_translated: Boolean,
        ai_confidence: Float,  // 0.0 - 1.0
        ai_model: String       // "m1800", "gpt-4", etc.
      }
    },
    "app.header.subtitle": {...},
    "app.footer.copyright": {...}
  },
  
  // OU Structure hiérarchique (optionnel)
  messages_hierarchical: {
    app: {
      header: {
        title: {
          value: String,
          status: String,
          metadata: {...}
        },
        subtitle: {...}
      },
      footer: {
        copyright: {...}
      }
    }
  },
  
  // Métadonnées du fichier
  stats: {
    total_messages: Int,
    approved_count: Int,
    pending_count: Int,
    rejected_count: Int,
    ai_translated_count: Int
  },
  
  // Historique des versions
  versions: [
    {
      version_number: Int,
      created_at: ISODate,
      created_by: UUID,
      snapshot: Object,      // Snapshot complet des messages
      changes: {
        added: [String],
        modified: [String],
        deleted: [String]
      }
    }
  ],
  
  created_at: ISODate,
  updated_at: ISODate,
  deleted_at: ISODate
}

// Indexes
db.translation_files.createIndex({ project_id: 1 })
db.translation_files.createIndex({ language_code: 1 })
db.translation_files.createIndex({ created_by: 1 })
db.translation_files.createIndex({ "messages.status": 1 })
db.translation_files.createIndex({ "messages.metadata.ai_translated": 1 })
```

---

### 2.5 Table `audit_logs` → Collection `audit_logs`

**MongoDB:**
```javascript
// Collection: audit_logs
{
  _id: ObjectId,
  id: UUID,
  user_id: UUID,
  organization_id: UUID,
  project_id: UUID,
  file_id: UUID,
  
  action: String,       // "CREATE", "UPDATE", "DELETE", "APPROVE", "TRANSLATE"
  entity_type: String,  // "PROJECT", "MESSAGE", "FILE", "TRANSLATION"
  entity_id: UUID,
  
  changes: {
    before: Object,
    after: Object,
    fields_modified: [String]
  },
  
  timestamp: ISODate,
  ip_address: String,
  user_agent: String
}

// Index
db.audit_logs.createIndex({ timestamp: -1 })
db.audit_logs.createIndex({ user_id: 1, timestamp: -1 })
db.audit_logs.createIndex({ project_id: 1, timestamp: -1 })
```

---

## 3. Plan de Migration Sécurisée

### Phase 1: Préparation (Jour 1)

1. **Créer une instance MongoDB parallèle**
   ```bash
   # En local ou cloud (Atlas, Neon, etc.)
   docker run -d -p 27017:27017 --name mongodb mongo:6.0
   ```

2. **Créer les collections avec schéma de validation**
   ```javascript
   db.createCollection("users", {
     validator: {
       $jsonSchema: {
         bsonType: "object",
         required: ["id", "email", "password_hash"],
         properties: {
           id: { bsonType: "string" },
           email: { bsonType: "string" },
           password_hash: { bsonType: "string" }
         }
       }
     }
   })
   ```

### Phase 2: Migration des Données (Jour 2-3)

1. **Script Python de migration**
   ```python
   # Voir section 4 ci-dessous
   ```

2. **Validation des données**
   ```python
   # Comparer les counts et checksums
   ```

3. **Rollback plan**
   - Garder Postgres actif pendant 30 jours
   - Transactions bidirectionnelles si nécessaire

### Phase 3: Déploiement (Jour 4)

1. Basculer la couche d'application
2. Monitorer les performances
3. Archive de Postgres après 30 jours de stabilité

---

## 4. Script Python de Migration

```python
# migration/migrate_to_mongodb.py

from pymongo import MongoClient, errors
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBMigration:
    def __init__(self, postgres_url, mongodb_url):
        self.pg_conn = psycopg2.connect(postgres_url)
        self.mongo_client = MongoClient(mongodb_url)
        self.mongo_db = self.mongo_client['i18n_db']
        
    def migrate_users(self):
        """Migrer la table users"""
        logger.info("Migrating users...")
        
        cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE deleted_at IS NULL")
        
        users_collection = self.mongo_db['users']
        
        for row in cursor:
            doc = {
                'id': str(row['id']),
                'name': row['name'],
                'email': row['email'],
                'password_hash': row['password_hash'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'is_active': True,
                'roles': [],
                'profile': {}
            }
            users_collection.insert_one(doc)
        
        # Créer les indexes
        users_collection.create_index('email', unique=True)
        users_collection.create_index('id', unique=True)
        logger.info(f"✓ Migrated {cursor.rowcount} users")
        
    def migrate_organizations(self):
        """Migrer organizations avec members imbriqués"""
        logger.info("Migrating organizations...")
        
        cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT o.*, 
                   COUNT(om.id) as member_count
            FROM organizations o
            LEFT JOIN organization_members om ON o.id = om.organization_id
            WHERE o.deleted_at IS NULL
            GROUP BY o.id
        """)
        
        orgs_collection = self.mongo_db['organizations']
        
        for row in cursor:
            # Récupérer les membres
            members_cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            members_cursor.execute("""
                SELECT om.user_id, om.role, om.created_at
                FROM organization_members om
                WHERE om.organization_id = %s
            """, (row['id'],))
            
            members = [
                {
                    'user_id': str(m['user_id']),
                    'role': m['role'],
                    'joined_at': m['created_at']
                }
                for m in members_cursor
            ]
            
            doc = {
                'id': str(row['id']),
                'name': row['name'],
                'description': row['description'],
                'created_by': str(row['created_by']),
                'members': members,
                'settings': {
                    'language_default': 'en',
                    'timezone': 'UTC'
                },
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            orgs_collection.insert_one(doc)
        
        orgs_collection.create_index('created_by')
        orgs_collection.create_index([('members.user_id', 1)])
        logger.info(f"✓ Migrated organizations with members")
        
    def migrate_projects(self):
        """Migrer projects avec members imbriqués"""
        logger.info("Migrating projects...")
        
        cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM projects WHERE deleted_at IS NULL")
        
        projects_collection = self.mongo_db['projects']
        
        for row in cursor:
            # Récupérer les membres du projet
            members_cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            members_cursor.execute("""
                SELECT pm.user_id, pm.role, pm.created_at
                FROM project_members pm
                WHERE pm.project_id = %s
            """, (row['id'],))
            
            members = [
                {
                    'user_id': str(m['user_id']),
                    'role': m['role'],
                    'joined_at': m['created_at']
                }
                for m in members_cursor
            ]
            
            doc = {
                'id': str(row['id']),
                'organization_id': str(row['organization_id']),
                'name': row['name'],
                'description': row['description'],
                'source_language': row['source_language'],
                'target_languages': row['target_languages'].split(','),
                'created_by': str(row['created_by']),
                'members': members,
                'metadata': {
                    'status': 'active',
                    'is_public': False,
                    'tags': []
                },
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            projects_collection.insert_one(doc)
        
        projects_collection.create_index('organization_id')
        projects_collection.create_index('created_by')
        logger.info(f"✓ Migrated {cursor.rowcount} projects")
        
    def migrate_translation_files(self):
        """Migrer translation_files avec messages imbriqués"""
        logger.info("Migrating translation files with messages...")
        
        cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT tf.* FROM translation_files tf
            WHERE tf.deleted_at IS NULL
        """)
        
        files_collection = self.mongo_db['translation_files']
        
        for file_row in cursor:
            file_id = file_row['id']
            
            # Récupérer les messages pour ce fichier
            messages_cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            messages_cursor.execute("""
                SELECT * FROM messages
                WHERE file_id = %s
            """, (file_id,))
            
            messages_dict = {}
            approved_count = 0
            pending_count = 0
            
            for msg in messages_cursor:
                messages_dict[msg['key']] = {
                    'id': str(msg['id']),
                    'key': msg['key'],
                    'value': msg['value'],
                    'comment': msg['comment'],
                    'status': msg['status'],
                    'metadata': {
                        'created_by': str(msg['created_by']) if msg['created_by'] else None,
                        'reviewed_by': str(msg['reviewed_by']) if msg['reviewed_by'] else None,
                        'created_at': msg['created_at'],
                        'updated_at': msg['updated_at'],
                        'ai_translated': False,
                        'ai_confidence': 0.0
                    }
                }
                
                if msg['status'] == 'APPROVED':
                    approved_count += 1
                elif msg['status'] == 'PENDING':
                    pending_count += 1
            
            doc = {
                'id': str(file_id),
                'project_id': str(file_row['project_id']),
                'language_code': file_row['language_code'],
                'language_name': file_row['language_name'],
                'current_version': file_row['current_version'],
                'created_by': str(file_row['created_by']) if file_row['created_by'] else None,
                'messages': messages_dict,
                'stats': {
                    'total_messages': len(messages_dict),
                    'approved_count': approved_count,
                    'pending_count': pending_count,
                    'rejected_count': len(messages_dict) - approved_count - pending_count,
                    'ai_translated_count': 0
                },
                'versions': [],
                'created_at': file_row['created_at'],
                'updated_at': file_row['updated_at']
            }
            
            files_collection.insert_one(doc)
        
        files_collection.create_index('project_id')
        files_collection.create_index('language_code')
        logger.info(f"✓ Migrated translation files with embedded messages")
        
    def run_migration(self):
        """Exécuter la migration complète"""
        try:
            logger.info("Starting MongoDB migration...")
            self.migrate_users()
            self.migrate_organizations()
            self.migrate_projects()
            self.migrate_translation_files()
            logger.info("✓ Migration completed successfully!")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            self.pg_conn.close()
            self.mongo_client.close()

# Usage
if __name__ == "__main__":
    migration = MongoDBMigration(
        postgres_url="postgresql://user:pass@localhost/i18n_db",
        mongodb_url="mongodb://localhost:27017"
    )
    migration.run_migration()
```

---

## 5. Configuration de la Couche d'Application

### Changer le driver de base de données

**Nouveau `database/mongo_core.py`:**
```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from contextlib import contextmanager

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "i18n_db")

class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
    
    def get_db(self):
        return self.db
    
    def close(self):
        self.client.close()
    
    def health_check(self):
        try:
            self.client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False

# FastAPI dependency
mongo_connection = MongoDBConnection()

def get_db():
    return mongo_connection.get_db()

# Type hint pour dependency injection
from typing import Annotated
from fastapi import Depends

MongoDatabase = Annotated[dict, Depends(get_db)]
```

---

## 6. Comparaison Avant/Après

| Aspect | Postgres | MongoDB |
|--------|----------|---------|
| **Modèle** | Relationnel normalisé | Document orienté objet |
| **Messages** | Table séparée, 1:N | Embedded in file |
| **Requête pour file + messages** | 2 requêtes (JOIN) | 1 requête |
| **Structure flexible** | Difficile | Native |
| **Scalabilité** | Vertical | Horizontal (sharding) |
| **Traductions imbriquées** | Complexe | Simple et naturel |

---

## 7. Checklist de Validation

- [ ] Comparer le nombre de documents avant/après
- [ ] Valider les UUIDs sont correctement migrés
- [ ] Vérifier les timestamps (timezone)
- [ ] Tester les indexes de performance
- [ ] Valider les données sensibles (passwords hashées)
- [ ] Exécuter les tests unitaires
- [ ] Load testing avec le même volume de données
- [ ] Plan de rollback en cas d'urgence

---

## 8. Prochaines Étapes

1. ✅ Migration de schéma
2. ⏭️ Redesign des objets imbriqués (voir `NESTED_OBJECTS_DESIGN.md`)
3. ⏭️ Module IA de traduction automatique (voir `ai_translation/translator.py`)
4. ⏭️ Mise à jour des services application
