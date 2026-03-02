# Modélisation des Objets Imbriqués pour Traductions

## 1. Vue d'ensemble

Cette section décrit comment structurer les messages de traduction en objets imbriqués pour MongoDB, permettant une gestion flexible, extensible et performante des clés de traduction hierarchisées.

---

## 2. Stratégies de Structuration

### 2.1 Approche 1: Structure Plate (Simple Clé/Valeur)

**Cas d'usage**: Applications simples, peu de messages, requêtes par clé unique.

```javascript
{
  _id: ObjectId,
  id: UUID,
  project_id: UUID,
  language_code: "fr",
  language_name: "French",
  
  messages: {
    "app.header.title": {
      value: "Titre de l'Application",
      status: "APPROVED",
      metadata: {
        created_by: UUID,
        ai_translated: false,
        ai_model: null,
        ai_confidence: 0
      }
    },
    "app.header.subtitle": {
      value: "Sous-titre",
      status: "PENDING",
      metadata: {...}
    },
    "app.footer.copyright": {
      value: "© 2024",
      status: "APPROVED",
      metadata: {...}
    }
  }
}
```

**Avantages**:
- Simple à implémenter
- Accès rapide par clé (O(1))
- Facile à exporter en JSON plate

**Inconvénients**:
- Noms de clés très longs ("app.header.menu.item1.label")
- Difficile de requêter par module ("tous les messages app.header.*")

---

### 2.2 Approche 2: Structure Hiérarchique (Imbriquée Profonde)

**Cas d'usage**: Applications complexes avec modules/sous-modules, gestion granulaire.

```javascript
{
  _id: ObjectId,
  id: UUID,
  project_id: UUID,
  language_code: "fr",
  language_name: "French",
  
  messages: {
    app: {
      header: {
        title: {
          value: "Titre de l'Application",
          status: "APPROVED",
          metadata: {...}
        },
        subtitle: {
          value: "Sous-titre",
          status: "PENDING",
          metadata: {...}
        },
        menu: {
          home: {
            label: "Accueil",
            status: "APPROVED",
            metadata: {...}
          },
          about: {
            label: "À propos",
            status: "APPROVED",
            metadata: {...}
          }
        }
      },
      footer: {
        copyright: {
          value: "© 2024",
          status: "APPROVED",
          metadata: {...}
        },
        links: {
          privacy: {
            value: "Politique de Confidentialité",
            status: "APPROVED",
            metadata: {...}
          }
        }
      }
    },
    auth: {
      login: {
        title: "Connexion",
        button_submit: "Se Connecter",
        error_invalid_credentials: "Identifiants invalides"
      }
    }
  }
}
```

**Avantages**:
- Logique organisationnelle claire
- Noms de clés plus courts
- Facile de requêter par module

**Inconvénients**:
- Plus profond à naviguer en code
- Requêtes dot-notation plus complexes

---

### 2.3 Approche 3: Hybride (Recommandée)

**Combinaison des deux approches**: clés simples mais organisées par module.

```javascript
{
  _id: ObjectId,
  id: UUID,
  project_id: UUID,
  language_code: "fr",
  
  // Stockage flat pour requêtes rapides
  messages: {
    "header.title": { value: "...", status: "APPROVED", metadata: {...} },
    "header.subtitle": { value: "...", status: "PENDING", metadata: {...} },
    "header.menu.home": { value: "Accueil", status: "APPROVED", metadata: {...} },
    "footer.copyright": { value: "...", status: "APPROVED", metadata: {...} }
  },
  
  // Index hiérarchique pour navigation
  structure: {
    header: ["title", "subtitle", "menu.home", "menu.about"],
    footer: ["copyright", "links.privacy"],
    auth: ["login.title", "login.button", "login.error"]
  }
}
```

**Avantages**:
- Requêtes O(1) par clé
- Index de structure pour navigation
- Facile de lister les clés d'un module
- Flexible et extensible

---

## 3. Schéma Détaillé Recommandé

```javascript
// Collection: translation_files
{
  // Identifiants
  _id: ObjectId,
  id: UUID,                        // UUID original
  project_id: UUID,
  
  // Métadonnées du fichier
  language_code: String,           // "fr", "es", "pt"
  language_name: String,           // "French", "Spanish"
  current_version: Int,            // Incrément pour versions
  
  // Auteur et timestamps
  created_by: UUID,
  created_at: ISODate,
  updated_at: ISODate,
  
  // MESSAGES IMBRIQUÉS - Cœur du système
  messages: {
    // Clés simples (flat)
    "key.path": {
      // Contenu
      value: String,               // Valeur traduite
      comment: String,             // Note pour traducteur
      context: String,             // Contexte d'utilisation
      
      // État et approbation
      status: String,              // "PENDING", "APPROVED", "REJECTED", "IN_REVIEW"
      review_note: String,         // Note du relecteur
      
      // Métadonnées de traduction
      metadata: {
        // Création
        created_by: UUID,
        created_at: ISODate,
        
        // Révision
        reviewed_by: UUID,
        reviewed_at: ISODate,
        
        // IA et Traduction automatique
        ai_translated: Boolean,
        ai_model: String,          // "m1800", "gpt-4", "claude"
        ai_version: String,        // Version du modèle
        ai_confidence: Float,      // 0.0 - 1.0
        ai_generated_at: ISODate,
        
        // Traçabilité
        translation_time_ms: Int,  // Temps de traduction
        word_count: Int,           // Nombre de mots
        character_count: Int
      },
      
      // Historique des modifications
      history: [
        {
          version: Int,
          value: String,
          modified_by: UUID,
          modified_at: ISODate,
          reason: String
        }
      ],
      
      // Tags pour organisation
      tags: [String],              // ["ui", "error", "critical"]
      priority: String,            // "low", "medium", "high"
      
      // Liens et références
      linked_keys: [String],       // ["auth.error.message"]
      plurals: {                   // Gestion du pluriel
        one: String,
        other: String
      }
    }
  },
  
  // Index de structure pour navigation
  structure: {
    "module_name": [
      "key1",
      "key2.subkey"
    ]
  },
  
  // Statistiques
  stats: {
    total_keys: Int,
    approved: Int,
    pending: Int,
    rejected: Int,
    in_review: Int,
    ai_translated: Int,
    last_modified_by: UUID,
    last_modified_at: ISODate
  },
  
  // Historique des versions complet
  versions: [
    {
      version_number: Int,
      created_at: ISODate,
      created_by: UUID,
      changelog: String,
      changes: {
        added: Int,
        modified: Int,
        deleted: Int
      },
      snapshot: Object  // Snapshot complet des messages
    }
  ],
  
  // Configuration
  config: {
    allow_empty_values: Boolean,
    require_context: Boolean,
    require_review: Boolean,
    auto_approval_rules: {
      ai_confidence_threshold: Float,
      auto_approve_above: Float
    }
  },
  
  // Soft delete
  deleted_at: ISODate,
  is_active: Boolean
}
```

---

## 4. Exemples Concrets

### Exemple 1: Application e-commerce simple

```javascript
db.translation_files.insertOne({
  id: UUID(),
  project_id: "proj_123",
  language_code: "es",
  language_name: "Spanish",
  
  messages: {
    "product.title": {
      value: "Título del Producto",
      status: "APPROVED",
      metadata: {
        ai_translated: true,
        ai_confidence: 0.95
      }
    },
    "product.description": {
      value: "Descripción detallada...",
      status: "APPROVED",
      metadata: {
        ai_translated: true,
        ai_confidence: 0.92
      }
    },
    "cart.empty_message": {
      value: "Tu carrito está vacío",
      status: "PENDING",
      metadata: {
        ai_translated: true,
        ai_confidence: 0.88
      }
    },
    "error.payment_failed": {
      value: "El pago falló. Por favor intenta de nuevo.",
      status: "APPROVED",
      metadata: {
        ai_translated: true,
        ai_confidence: 0.93,
        priority: "high"
      }
    }
  },
  
  structure: {
    product: ["title", "description"],
    cart: ["empty_message"],
    error: ["payment_failed"]
  }
})
```

### Exemple 2: Application SaaS complexe avec modules

```javascript
db.translation_files.insertOne({
  id: UUID(),
  project_id: "proj_456",
  language_code: "fr",
  language_name: "French",
  
  messages: {
    // Module Dashboard
    "dashboard.welcome": {
      value: "Bienvenue sur votre tableau de bord",
      status: "APPROVED",
      metadata: { ai_translated: true, ai_confidence: 0.97 }
    },
    "dashboard.stats.revenue": {
      value: "Chiffre d'affaires",
      status: "APPROVED",
      metadata: { ai_translated: true, ai_confidence: 0.96 }
    },
    
    // Module Utilisateurs
    "users.list.title": {
      value: "Liste des utilisateurs",
      status: "APPROVED",
      metadata: { ai_translated: true, ai_confidence: 0.98 }
    },
    "users.form.email": {
      value: "Adresse email",
      status: "APPROVED",
      metadata: { ai_translated: false }
    },
    
    // Erreurs
    "error.user_not_found": {
      value: "Utilisateur non trouvé",
      status: "IN_REVIEW",
      review_note: "À vérifier par native speaker",
      metadata: { ai_translated: true, ai_confidence: 0.85 }
    },
    "error.permission_denied": {
      value: "Vous n'avez pas l'autorisation d'accéder à cette ressource",
      status: "APPROVED",
      metadata: { ai_translated: true, ai_confidence: 0.92 }
    }
  },
  
  structure: {
    dashboard: ["welcome", "stats.revenue", "stats.users"],
    users: ["list.title", "form.email", "form.name"],
    error: ["user_not_found", "permission_denied"]
  },
  
  stats: {
    total_keys: 9,
    approved: 7,
    in_review: 1,
    pending: 1,
    ai_translated: 8
  }
})
```

---

## 5. Requêtes MongoDB Courantes

### Récupérer un message par clé

```javascript
db.translation_files.findOne(
  { 
    project_id: ObjectId("..."),
    "messages.dashboard.welcome": { $exists: true }
  },
  { 
    projection: { "messages.dashboard.welcome": 1 }
  }
)
```

### Lister tous les messages d'un module

```javascript
db.translation_files.findOne(
  { project_id: ObjectId("...") },
  { projection: { structure: 1, "messages": 1 } }
).then(doc => {
  const keys = doc.structure.dashboard;  // ["welcome", "stats.revenue"]
  return keys.map(k => ({
    key: `dashboard.${k}`,
    ...doc.messages[`dashboard.${k}`]
  }));
})
```

### Trouver les messages non approuvés

```javascript
db.translation_files.find({
  project_id: ObjectId("..."),
  "messages.status": { $ne: "APPROVED" }
})
```

### Compter les messages traduits par IA

```javascript
db.translation_files.aggregate([
  { $match: { project_id: ObjectId("...") } },
  {
    $group: {
      _id: "$language_code",
      ai_translated: {
        $sum: {
          $cond: ["$messages.metadata.ai_translated", 1, 0]
        }
      }
    }
  }
])
```

---

## 6. Avantages de cette Modélisation

✅ **Flexibilité**: Ajouter des champs sans migration
✅ **Performance**: Une seule requête pour file + messages
✅ **Extensibilité**: Support des objets imbriqués, pluriels, context
✅ **Traçabilité**: Historique complet intégré
✅ **IA-Ready**: Métadonnées de traduction native
✅ **Organisation**: Index de structure pour navigation
✅ **Scalabilité**: Document auto-contenu, facile à sharding

---

## 7. Intégration avec la Traduction IA

Voir `ai_translation/translator.py` pour l'intégration complète.
