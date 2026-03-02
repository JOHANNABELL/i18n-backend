# ⚡ Quick Start: Démarrer en 15 minutes

## Prérequis

- Python 3.9+
- MongoDB (local ou cloud)
- API key Groq (gratuit sur https://console.groq.com)

---

## 1️⃣ Installation (2 min)

```bash
# Installer dépendances
pip install pymongo groq asyncio

# Ou ajouter à requirements.txt
pymongo==4.6.0
groq==0.4.2
asyncio-contextmanager==1.0.0
```

---

## 2️⃣ Configuration (2 min)

**Créer `.env`**:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=i18n_db
GROQ_API_KEY=gsk_YOUR_KEY_HERE
DEFAULT_AI_MODEL=llama-3.1-70b-versatile
```

---

## 3️⃣ Copier le Code (1 min)

```bash
# Copier module IA
cp -r src/ai_translation/ /votre/projet/src/

# Copier docs
cp MONGODB_MIGRATION_GUIDE.md /votre/projet/
cp NESTED_OBJECTS_DESIGN.md /votre/projet/
cp AI_TRANSLATION_INTEGRATION_GUIDE.md /votre/projet/
```

---

## 4️⃣ Intégrer dans FastAPI (2 min)

**main.py**:
```python
from fastapi import FastAPI
from src.ai_translation.controller import router as ai_router

app = FastAPI(title="i18n API")

# Include AI translation routes
app.include_router(ai_router)

# Autres routes...
```

---

## 5️⃣ Tester (5 min)

### Lancer le serveur
```bash
python -m uvicorn src.main:app --reload
```

### Traduire un fichier complet
```bash
curl -X POST http://localhost:8000/api/v1/ai-translation/files/YOUR_FILE_ID/translate \
  -H "Content-Type: application/json" \
  -d '{
    "target_language_code": "fr",
    "target_language_name": "French",
    "auto_approve": true,
    "confidence_threshold": 0.85,
    "ai_model": "llama-3.1-70b"
  }'
```

### Vérifier le statut
```bash
curl http://localhost:8000/api/v1/ai-translation/jobs/JOB_ID
```

### Traduire un seul message
```bash
curl -X POST http://localhost:8000/api/v1/ai-translation/messages/translate \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "file_id",
    "key": "app.header.title",
    "source_value": "Welcome to our app",
    "source_language": "en",
    "target_language": "fr",
    "context": "Header of dashboard",
    "auto_approve": true
  }'
```

### Exporter les traductions
```bash
curl http://localhost:8000/api/v1/ai-translation/files/FILE_ID/export?flatten=true
```

---

## 6️⃣ Utilisation en Python

```python
import asyncio
from src.ai_translation import AITranslator, GroqTranslationProvider, AIModel

async def main():
    # Initialiser provider
    provider = GroqTranslationProvider(
        api_key="gsk_YOUR_KEY"
    )
    
    # Initialiser translator
    translator = AITranslator(
        mongodb_url="mongodb://localhost:27017",
        ai_provider=provider,
        ai_model=AIModel.LLAMA_3_1
    )
    
    # Traduire
    result = await translator.translate_file(
        source_file_id="source-uuid",
        target_language_code="es",
        target_language_name="Spanish",
        translator_user_id="user-uuid",
        auto_approve=True
    )
    
    print(result)
    translator.close()

asyncio.run(main())
```

---

## 📊 Structure des Résultats

### Réponse Traduction Complète
```json
{
  "success": true,
  "file_id": "file_es_123",
  "language_code": "es",
  "messages_translated": 150,
  "messages_approved": 145,
  "average_confidence": 0.92,
  "translation_time_ms": 45000,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Réponse Message Unique
```json
{
  "success": true,
  "key": "app.header.title",
  "translated_value": "Bienvenue sur notre application",
  "ai_confidence": 0.97,
  "ai_model": "llama-3.1-70b",
  "translation_time_ms": 280,
  "status": "APPROVED"
}
```

---

## 🔥 Cas d'Usage Courants

### 1. Traduire une app simple
```python
# Fichier EN avec 50 messages
result = await translator.translate_file(
    source_file_id="en_file",
    target_language_code="fr",
    target_language_name="French",
    translator_user_id="user_123",
    auto_approve=True  # Approuver automatiquement
)
# Résultat: 50 messages en FR en ~2 minutes
```

### 2. Traduire vers 5 langues
```python
languages = [
    ("fr", "French"),
    ("es", "Spanish"),
    ("de", "German"),
    ("it", "Italian"),
    ("pt", "Portuguese")
]

for lang_code, lang_name in languages:
    result = await translator.translate_file(
        source_file_id="en_file",
        target_language_code=lang_code,
        target_language_name=lang_name,
        translator_user_id="user_123"
    )
    print(f"✓ {lang_code}: {result['messages_translated']} messages")
```

### 3. Réviser les traductions
```bash
curl -X POST http://localhost:8000/api/v1/ai-translation/files/FILE_ID/approve \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {
        "key": "error.message",
        "status": "REJECTED",
        "review_note": "Too literal, needs adaptation"
      },
      {
        "key": "app.title",
        "status": "APPROVED",
        "review_note": "Perfect!"
      }
    ]
  }'
```

### 4. Exporter pour utilisation
```bash
# Format plat (JSON)
curl http://localhost:8000/api/v1/ai-translation/files/FILE_ID/export?flatten=true > translations_fr.json

# Utiliser dans votre app
import json
with open('translations_fr.json') as f:
    messages = json.load(f)
    
# Access like: messages['app.header.title']
```

---

## 📋 Checklist Rapide

- [ ] Python 3.9+ installé
- [ ] MongoDB accessible
- [ ] Groq API key obtenue
- [ ] `.env` configuré
- [ ] Module `src/ai_translation/` copié
- [ ] Router intégré dans FastAPI
- [ ] Serveur lancé (`uvicorn`)
- [ ] Premier test réussi
- [ ] Confiance > 0.85
- [ ] Prêt pour production

---

## 🆘 Dépannage Rapide

| Problème | Solution |
|----------|----------|
| `MongoDB connection refused` | Vérifier `MONGODB_URL` |
| `API key invalid` | Vérifier `GROQ_API_KEY` dans `.env` |
| `File not found` | UUID du fichier incorrect |
| `Confidence too low (< 0.80)` | Texte complexe = résultat normal |
| `Timeout` | Fichier trop gros = diviser |

---

## 📚 Pour Approfondir

- **Migration MongoDB**: Lire `MONGODB_MIGRATION_GUIDE.md`
- **Design objets**: Lire `NESTED_OBJECTS_DESIGN.md`
- **Intégration complète**: Lire `AI_TRANSLATION_INTEGRATION_GUIDE.md`
- **Exemples concrets**: Lire `TRANSLATION_EXAMPLES.md`
- **Planning détaillé**: Lire `I18N_COMPLETE_ROADMAP.md`

---

## ✅ Vous êtes Prêt!

Vous pouvez maintenant:
- ✅ Traduire des fichiers complets en quelques minutes
- ✅ Approuver/rejeter les traductions
- ✅ Exporter les résultats
- ✅ Monitorer la confiance IA
- ✅ Gérer plusieurs langues

**Bonne traduction! 🚀**
