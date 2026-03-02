# Guide de Dépannage - Backend Restructuring

## 🔴 Problèmes Courants et Solutions

---

## 1. console.log qui n'apparaissent pas

### Symptôme
```typescript
const data = await api.getOrganizationsByUser(userData.id, token);
console.log("organizationsData", data); // Ne s'affiche pas ❌
```

### Cause Probable
Le `console.log` est appelé **en dehors d'un `useEffect`**, ce qui cause un rendu en boucle infinie et les logs ne s'affichent qu'une fois avant d'être écrasés.

### ✅ Solution 1: Utiliser useEffect
```typescript
export default function Organizations() {
  useEffect(() => {
    const loadOrganizations = async () => {
      try {
        const data = await api.getOrganizationsByUser(userData.id, token);
        console.log("[v0] organizationsData", data); // ✅ S'affiche maintenant
        setOrganizations(data);
      } catch (error) {
        console.error("[v0] Error:", error);
      }
    };

    loadOrganizations();
  }, [userData.id, token]); // ✅ Dépendances importantes
}
```

### ✅ Solution 2: Utiliser SWR (Recommandé)
```typescript
import useSWR from 'swr';

export default function Organizations() {
  const { data, error, isLoading } = useSWR(
    userData?.id ? `/organizations/user/${userData.id}/detailed` : null,
    (url) => api.getOrganizationsByUser(userData.id, token),
    {
      onSuccess: (data) => {
        console.log("[v0] Data loaded:", data); // ✅ Appelé au bon moment
      }
    }
  );
}
```

### ✅ Solution 3: Vérifier la DevTools
1. Ouvrir DevTools (F12)
2. Aller à "Console"
3. Chercher "[v0]" dans les logs
4. Vérifier qu'il n'y a pas de "Uncaught ReferenceError"

---

## 2. Endpoint 404 Not Found

### Symptôme
```
GET /organizations/550e8400.../detailed 404 Not Found
```

### Cause Possible
1. Le nouvel endpoint n'est pas enregistré dans le router
2. Mauvais chemin d'accès à l'endpoint
3. Le contrôleur n'a pas été mis à jour

### ✅ Solutions

**Vérifier le chemin d'accès:**
```bash
# ❌ Mauvais
curl http://localhost:8000/organizations/550e8400.../detail

# ✅ Bon
curl http://localhost:8000/organizations/550e8400.../detailed
```

**Vérifier que le route est enregistré:**
```python
# Dans src/organization/controller.py
@router.get("/{org_id}/detailed", response_model=models.OrganizationDetailedResponse)
def get_organization_detailed(org_id: UUID, db: DbSession):
    return service.get_organization_detailed(db, org_id)
```

**Vérifier le router prefix:**
```python
router = APIRouter(
    prefix="/organizations",  # ✅ Le prefix est correct
    tags=["Organizations"]
)
```

---

## 3. Import Error: No module named ...

### Symptôme
```
ModuleNotFoundError: No module named 'src.entities.organizationMember'
```

### Cause
L'entité n'existe pas ou le chemin d'import est incorrect

### ✅ Solution
```python
# ✅ Vérifier que le fichier existe
ls -la src/entities/organizationMember.py

# ✅ Vérifier l'import
from src.entities.organizationMember import OrganizationMember

# ✅ Vérifier que le __init__.py existe
ls -la src/entities/__init__.py
```

---

## 4. Type Error: Expected UUID, got str

### Symptôme
```
ValueError: invalid UUID: 'not-a-uuid'
```

### Cause
L'ID est passé en tant que string au lieu de UUID

### ✅ Solution
```python
# ❌ Mauvais
org_id = "550e8400-e29b-41d4-a716-446655440000"  # String
org = service.get_organization_detailed(db, org_id)  # ❌ Erreur

# ✅ Bon
from uuid import UUID
org_id = UUID("550e8400-e29b-41d4-a716-446655440000")
org = service.get_organization_detailed(db, org_id)

# ✅ Ou utiliser FastAPI qui convertit automatiquement
@router.get("/{org_id}/detailed")
def get_org(org_id: UUID, db: DbSession):  # ✅ FastAPI parse automatiquement
    return service.get_organization_detailed(db, org_id)
```

---

## 5. Empty Members/Messages Array

### Symptôme
```json
{
  "id": "uuid",
  "name": "Org Name",
  "members": []  // ❌ Array vide bien qu'il y ait des membres
}
```

### Cause
La jointure n'est pas correcte ou les données n'ont pas été créées

### ✅ Solution
```python
# ✅ Vérifier la requête DB
members = db.query(OrganizationMember).filter(
    OrganizationMember.organization_id == org.id
).all()

# Déboguer
print(f"[v0] Found {len(members)} members for org {org.id}")

# ✅ S'assurer que les données existent
# Dans la base de données
SELECT * FROM organization_member WHERE organization_id = 'uuid';

# ✅ Vérifier les colonnes
# Assurez-vous que organization_id et user_id existent et sont correctement nommées
```

---

## 6. JSON Serialization Error

### Symptôme
```
TypeError: Object of type datetime is not JSON serializable
```

### Cause
Les types DateTime/UUID ne sont pas sérialisables par défaut en JSON

### ✅ Solution
```python
# ✅ Utiliser Pydantic BaseModel avec from_attributes
class OrganizationDetailedResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime  # ✅ Pydantic gère la sérialisation
    members: List[MemberInfo]

    class Config:
        from_attributes = True  # ✅ Important pour SQLAlchemy
```

---

## 7. 401 Unauthorized

### Symptôme
```
GET /organizations/{id}/detailed 401 Unauthorized
```

### Cause
Le token JWT est manquant ou invalide

### ✅ Solution
```bash
# ✅ Ajouter le token
curl -X GET "http://localhost:8000/organizations/uuid/detailed" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ✅ Vérifier que le token est valide
# Décoder le token sur jwt.io

# ✅ Vérifier que CurrentUser est correctement configuré
@router.get("/{org_id}/detailed")
def get_organization_detailed(
    org_id: UUID, 
    db: DbSession,
    current_user: CurrentUser  # ✅ Injecter si nécessaire
):
    return service.get_organization_detailed(db, org_id)
```

---

## 8. 500 Internal Server Error

### Symptôme
```
GET /organizations/{id}/detailed 500 Internal Server Error
```

### Cause
Une exception non gérée dans le service

### ✅ Debugging
```python
# ✅ Ajouter des logs détaillés
def get_organization_detailed(db: Session, org_id: UUID) -> dict:
    logging.debug(f"[v0] Fetching org {org_id}")
    
    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        
        if not org:
            logging.warning(f"[v0] Organization not found: {org_id}")
            raise Exception("Organization not found")
        
        logging.debug(f"[v0] Found org: {org.name}")
        
        members_data = []
        members = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org.id
        ).all()
        
        logging.debug(f"[v0] Found {len(members)} members")
        
        for member in members:
            user = db.query(User).filter(User.id == member.user_id).first()
            if user:
                logging.debug(f"[v0] Processing member: {user.name}")
                members_data.append({...})
        
        return {
            "id": org.id,
            "name": org.name,
            "members": members_data
        }
    except Exception as e:
        logging.error(f"[v0] Error in get_organization_detailed: {str(e)}", exc_info=True)
        raise
```

### Vérifier les logs
```bash
# ✅ Vérifier les logs de l'application
tail -f logs/app.log | grep "[v0]"

# ✅ Vérifier l'erreur exacte
# Chercher "Error" ou "Exception" dans les logs
```

---

## 9. Association/Relationship not loaded

### Symptôme
```
sqlalchemy.exc.InvalidRequestError: Relationship 'members' of 'Organization' 
does not load, no lazy= option was set
```

### Cause
La relation n'est pas définie dans l'entité SQLAlchemy

### ✅ Solution
```python
# ✅ Vérifier que la relation existe dans l'entité
class Organization(Base):
    __tablename__ = "organizations"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    
    # ✅ La relation doit être définie
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember",
        foreign_keys="OrganizationMember.organization_id"
    )
```

---

## 10. Database Connection Error

### Symptôme
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

### Cause
La base de données n'est pas accessible

### ✅ Solution
```bash
# ✅ Vérifier que la DB est en cours d'exécution
docker ps | grep postgres

# ✅ Vérifier la connexion
psql -U username -d dbname -h localhost

# ✅ Vérifier les variables d'environnement
echo $DATABASE_URL

# ✅ Vérifier les paramètres de connexion dans .env
cat .env | grep DATABASE
```

---

## 11. Duplicate Route Error

### Symptôme
```
RuntimeError: Duplicate route definition detected
```

### Cause
Deux routes avec le même chemin et même méthode

### ✅ Solution
```python
# ❌ Mauvais - Routes en doublon
@router.get("/{org_id}")
def get_organization(org_id: UUID, db: DbSession):
    return service.get_organization_by_id(db, org_id)

@router.get("/{org_id}")  # ❌ Route dupliquée
def get_organization_detailed(org_id: UUID, db: DbSession):
    return service.get_organization_detailed(db, org_id)

# ✅ Bon - Routes différentes
@router.get("/{org_id}")
def get_organization(org_id: UUID, db: DbSession):
    return service.get_organization_by_id(db, org_id)

@router.get("/{org_id}/detailed")  # ✅ Route différente
def get_organization_detailed(org_id: UUID, db: DbSession):
    return service.get_organization_detailed(db, org_id)
```

---

## 12. Performance Issue - Slow Response

### Symptôme
```
GET /organizations/{id}/detailed took 2.5 seconds
```

### Cause
N+1 queries ou requête inefficace

### ✅ Optimization
```python
# ❌ Mauvais - N+1 queries
members = db.query(OrganizationMember).filter(...).all()
for member in members:
    user = db.query(User).filter(User.id == member.user_id).first()  # ❌ Requête par membre

# ✅ Bon - Une seule requête avec JOIN
from sqlalchemy import select
from sqlalchemy.orm import joinedload

members = db.query(OrganizationMember).filter(...).options(
    joinedload(OrganizationMember.user)
).all()

# ✅ Ou utiliser un JOIN SQL
query = db.query(OrganizationMember, User).join(
    User, OrganizationMember.user_id == User.id
).filter(OrganizationMember.organization_id == org_id).all()
```

### Vérifier avec logging
```python
# Activer SQL logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Les requêtes SQL vont s'afficher dans la console
```

---

## Check-list de Dépannage Rapide

Quand quelque chose ne fonctionne pas:

1. **Vérifier les logs**
   ```bash
   tail -f logs/app.log | grep ERROR
   ```

2. **Tester avec cURL**
   ```bash
   curl -X GET "http://localhost:8000/organizations/uuid/detailed" \
     -H "Authorization: Bearer TOKEN"
   ```

3. **Vérifier le Network tab**
   - F12 → Network
   - Faire la requête
   - Vérifier le Status Code (200, 404, 500, etc.)
   - Vérifier la réponse JSON

4. **Vérifier les types**
   ```python
   print(f"Type: {type(org_id)}, Value: {org_id}")
   ```

5. **Vérifier les données**
   ```bash
   SELECT * FROM organizations WHERE id = 'uuid';
   SELECT * FROM organization_member WHERE organization_id = 'uuid';
   ```

6. **Redémarrer l'application**
   ```bash
   # Arrêter
   Ctrl+C
   
   # Redémarrer
   python -m uvicorn src.main:app --reload
   ```

---

## Resources Utiles

- **Pydantic**: https://docs.pydantic.dev/latest/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Debugging Python**: https://docs.python.org/3/library/pdb.html
- **cURL**: https://curl.se/docs/manual.html

---

## Quand Demander de l'Aide

Si vous avez essayé les solutions ci-dessus et ça ne marche toujours pas:

1. Chercher dans les logs d'erreur
2. Consulter la documentation pertinente
3. Chercher des issues similaires sur GitHub/StackOverflow
4. Créer un ticket de support avec:
   - Description du problème
   - Logs d'erreur complets
   - Étapes pour reproduire
   - Commandes/Code utilisé
