# Guide d'Intégration du Module de Traduction IA

## 1. Vue d'ensemble

Ce guide explique comment intégrer le module de traduction IA dans votre application i18n backend existante. Le module utilise MongoDB et supporte plusieurs modèles IA (Groq, Anthropic, OpenAI).

---

## 2. Architecture du Module

```
src/ai_translation/
├── __init__.py           # Exports principaux
├── translator.py         # Core AI translation engine (593 lines)
├── service.py           # Business logic layer (408 lines)
└── controller.py        # FastAPI endpoints (436 lines)
```

### Flux de Traduction

```
1. User calls POST /api/v1/ai-translation/files/{id}/translate
   ↓
2. AITranslationService creates translation job (async)
   ↓
3. Background task executes AITranslator.translate_file()
   ↓
4. For each message:
   - Call AI provider (Groq/Claude/OpenAI)
   - Calculate confidence score
   - Store in MongoDB with metadata
   ↓
5. Create new translation_files document with all messages embedded
   ↓
6. Update job status to COMPLETED
```

---

## 3. Installation et Configuration

### 3.1 Dépendances

Ajouter à `requirements.txt`:

```txt
# MongoDB
pymongo==4.6.0

# AI Providers
groq==0.4.2                          # Groq API (pour M1800/Llama)
anthropic==0.18.0                    # Anthropic Claude API
openai==1.3.0                        # OpenAI API (optionnel)

# Async
aiohttp==3.9.1
asyncio-contextmanager==1.0.0
```

Installation:
```bash
pip install -r requirements.txt
```

### 3.2 Variables d'Environnement

Créer un fichier `.env`:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=i18n_db

# AI Providers
GROQ_API_KEY=your-groq-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key

# AI Configuration
DEFAULT_AI_MODEL=llama-3.1-70b
AI_CONFIDENCE_THRESHOLD=0.85
AUTO_APPROVE_THRESHOLD=0.90
```

### 3.3 Intégration dans FastAPI

Ajouter à `src/main.py`:

```python
from fastapi import FastAPI
from src.ai_translation.controller import router as ai_translation_router

app = FastAPI(title="i18n API")

# Include AI translation routes
app.include_router(ai_translation_router)

# Other routes...
```

---

## 4. Configuration des Providers IA

### 4.1 Groq (Recommandé - Plus rapide et moins cher)

**API Key**: Obtenir sur https://console.groq.com

**Modèles disponibles**:
- `llama-3.1-70b-versatile` (Recommandé)
- `llama-3.1-405b-versatile` (Plus puissant)
- `mixtral-8x7b-32768`

**Coût**: ~$0.27/million tokens

```python
from src.ai_translation import GroqTranslationProvider, AITranslator

provider = GroqTranslationProvider(
    api_key="your-groq-key",
    model="llama-3.1-70b-versatile"
)

translator = AITranslator(
    mongodb_url="mongodb://localhost:27017",
    ai_provider=provider
)
```

### 4.2 Anthropic Claude (Meilleure qualité)

**API Key**: Obtenir sur https://console.anthropic.com

**Modèles**:
- `claude-3-5-sonnet-20241022` (Recommandé)
- `claude-3-opus-20240229` (Plus puissant)

**Coût**: ~$3/million tokens input

```python
from src.ai_translation import AnthropicTranslationProvider

provider = AnthropicTranslationProvider(
    api_key="your-anthropic-key",
    model="claude-3-5-sonnet-20241022"
)
```

### 4.3 Comparaison des Providers

| Provider | Coût | Vitesse | Qualité | Temps réponse |
|----------|------|---------|---------|---------------|
| **Groq** | $$ | ⚡⚡⚡ | 🟨🟨🟨 | 200ms |
| **Claude** | $$$$ | ⚡⚡ | 🟩🟩🟩 | 500ms |
| **GPT-4** | $$$$$ | ⚡ | 🟩🟩🟩 | 1000ms |

**Recommandation**: Utiliser Groq pour traduction rapide, Claude pour qualité critique.

---

## 5. Migration de Postgres vers MongoDB

Avant d'utiliser le module IA, migrer vers MongoDB:

```bash
# 1. Voir MONGODB_MIGRATION_GUIDE.md
python migration/migrate_to_mongodb.py

# 2. Valider les données
python migration/validate_migration.py

# 3. Tester les performances
python migration/test_performance.py
```

---

## 6. Utilisation du Module IA

### 6.1 Traduire un Fichier Complet

**POST** `/api/v1/ai-translation/files/{file_id}/translate`

```bash
curl -X POST http://localhost:8000/api/v1/ai-translation/files/abc123/translate \
  -H "Content-Type: application/json" \
  -d '{
    "target_language_code": "fr",
    "target_language_name": "French",
    "auto_approve": true,
    "confidence_threshold": 0.85,
    "ai_model": "llama-3.1-70b"
  }'
```

**Response**:
```json
{
  "job_id": "job_xyz789",
  "status": "PENDING",
  "message": "Translation job created. Processing in background..."
}
```

### 6.2 Vérifier le Statut d'une Traduction

**GET** `/api/v1/ai-translation/jobs/{job_id}`

```bash
curl http://localhost:8000/api/v1/ai-translation/jobs/job_xyz789
```

**Response**:
```json
{
  "id": "job_xyz789",
  "status": "COMPLETED",
  "progress": {
    "total_messages": 150,
    "translated_messages": 150,
    "approved_messages": 145,
    "failed_messages": 0
  },
  "result": {
    "file_id": "file_fr_123",
    "messages_translated": 150,
    "average_confidence": 0.92,
    "translation_time_ms": 45000
  },
  "completed_at": "2024-03-15T10:30:00Z"
}
```

### 6.3 Traduire un Message Unique

**POST** `/api/v1/ai-translation/messages/translate`

```bash
curl -X POST http://localhost:8000/api/v1/ai-translation/messages/translate \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "file_123",
    "key": "app.header.title",
    "source_value": "Welcome to our app",
    "source_language": "en",
    "target_language": "fr",
    "context": "Header of dashboard",
    "auto_approve": true
  }'
```

**Response**:
```json
{
  "success": true,
  "key": "app.header.title",
  "translated_value": "Bienvenue sur notre application",
  "ai_confidence": 0.94,
  "ai_model": "llama-3.1-70b",
  "translation_time_ms": 250,
  "status": "APPROVED"
}
```

### 6.4 Approuver les Traductions

**POST** `/api/v1/ai-translation/files/{file_id}/approve`

```bash
curl -X POST http://localhost:8000/api/v1/ai-translation/files/file_123/approve \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {
        "key": "app.header.title",
        "status": "APPROVED",
        "review_note": "Perfect translation"
      },
      {
        "key": "error.message",
        "status": "REJECTED",
        "review_note": "Too literal, needs adaptation"
      }
    ]
  }'
```

### 6.5 Exporter les Traductions

**GET** `/api/v1/ai-translation/files/{file_id}/export?flatten=true`

```bash
curl http://localhost:8000/api/v1/ai-translation/files/file_fr_123/export?flatten=true
```

**Response** (JSON plat):
```json
{
  "app.header.title": "Bienvenue sur notre application",
  "app.header.subtitle": "Gérez vos traductions facilement",
  "app.footer.copyright": "© 2024 Notre Entreprise",
  "error.user_not_found": "Utilisateur non trouvé"
}
```

---

## 7. Gestion des Erreurs et Rollback

### 7.1 Erreurs Courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `API key invalid` | Clé IA incorrecte | Vérifier `.env` |
| `MongoDB connection failed` | BD non accessible | Vérifier `MONGODB_URL` |
| `File not found` | ID invalide | Vérifier l'UUID du fichier |
| `Confidence too low` | Qualité traduction < seuil | Réduire `confidence_threshold` |

### 7.2 Rollback d'une Traduction

```python
# Si traduction est mauvaise, supprimer le fichier
db.translation_files.delete_one({"id": "file_id"})

# Ou marquer comme inactive
db.translation_files.update_one(
    {"id": "file_id"},
    {"$set": {"is_active": False}}
)
```

---

## 8. Optimisation et Performance

### 8.1 Traduction Parallèle

Pour traduire plusieurs fichiers simultanément:

```python
import asyncio
from src.ai_translation import AITranslator

async def batch_translate():
    translator = AITranslator(...)
    
    tasks = [
        translator.translate_file(
            source_file_id=file_id,
            target_language_code="fr"
        )
        for file_id in source_files
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Exécuter
asyncio.run(batch_translate())
```

### 8.2 Caching des Traductions

Implémenter un cache Redis pour les traductions répétées:

```python
import redis

cache = redis.Redis(host='localhost', port=6379)

# Avant traduction
cache_key = f"translation:{source_value}:{target_lang}"
cached = cache.get(cache_key)

if cached:
    return json.loads(cached)

# Après traduction
cache.setex(cache_key, 86400, json.dumps(result))  # 24h TTL
```

### 8.3 Batch Processing

Traduire par lots pour réduire les appels API:

```python
BATCH_SIZE = 50

for i in range(0, len(messages), BATCH_SIZE):
    batch = messages[i:i+BATCH_SIZE]
    results = await translate_batch(batch)
```

---

## 9. Monitoring et Logs

### 9.1 Configuration des Logs

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_translation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ai_translation')
```

### 9.2 Métriques Clés

```python
# Confidence score moyen
avg_confidence = sum(c for c in scores) / len(scores)

# Taux d'approbation automatique
auto_approve_rate = approved / total * 100

# Coût estimé
cost_per_million = 0.27  # Groq
estimated_cost = (token_count / 1_000_000) * cost_per_million

# Temps moyen de traduction
avg_time_ms = sum(times) / len(times)
```

---

## 10. Exemple Complet d'Utilisation

```python
# app.py
import asyncio
from src.ai_translation import AITranslator, GroqTranslationProvider, AIModel
from src.ai_translation.service import AITranslationService

async def main():
    # 1. Initialiser le provider
    groq_provider = GroqTranslationProvider(
        api_key="gsk_XXXXX",
        model="llama-3.1-70b-versatile"
    )
    
    # 2. Initialiser le translator
    translator = AITranslator(
        mongodb_url="mongodb://localhost:27017",
        ai_provider=groq_provider,
        ai_model=AIModel.LLAMA_3_1
    )
    
    # 3. Traduire un fichier complet
    result = await translator.translate_file(
        source_file_id="source-file-uuid",
        target_language_code="fr",
        target_language_name="French",
        translator_user_id="user-uuid-123",
        auto_approve=True,
        confidence_threshold=0.85
    )
    
    # 4. Vérifier les résultats
    if result["success"]:
        print(f"✓ {result['messages_translated']} messages traduits")
        print(f"  Average confidence: {result['average_confidence']}")
        print(f"  Time: {result['translation_time_ms']}ms")
    else:
        print(f"✗ Error: {result['error']}")
    
    # 5. Obtenir les statistiques
    service = AITranslationService(mongodb_url="mongodb://localhost:27017")
    stats = service.get_translation_stats(result["file_id"])
    print(f"Stats: {stats}")
    
    translator.close()
    service.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 11. Prochaines Étapes

1. ✅ Migration MongoDB (voir MONGODB_MIGRATION_GUIDE.md)
2. ✅ Modèles imbriqués (voir NESTED_OBJECTS_DESIGN.md)
3. ✅ Module IA (ce fichier)
4. ⏭️ Tests unitaires (voir AI_TRANSLATION_TESTS.md)
5. ⏭️ Dashboard d'administration
6. ⏭️ Webhooks pour notifications

---

## 12. Support et Documentation

- 📖 [MONGODB_MIGRATION_GUIDE.md](./MONGODB_MIGRATION_GUIDE.md) - Migration base de données
- 📖 [NESTED_OBJECTS_DESIGN.md](./NESTED_OBJECTS_DESIGN.md) - Structure des objets
- 📖 [Groq API Docs](https://console.groq.com/docs)
- 📖 [Anthropic Docs](https://docs.anthropic.com)
- 📖 [MongoDB Docs](https://docs.mongodb.com)
