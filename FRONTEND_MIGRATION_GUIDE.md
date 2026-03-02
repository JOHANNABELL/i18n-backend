# Guide de Migration Frontend - Endpoints Détaillés

## Problème: console.log qui n'apparaissent pas

Votre problème initial où `console.log` ne s'affichait pas malgré la requête réussie provient probablement d'une **architecture asynchrone** dans React. Voici les solutions:

### Solution 1: Vérifier le contexte d'exécution

```typescript
// ❌ Mauvais - loadOrganizations s'exécute en boucle infinie
export default function Organizations() {
  const [organizations, setOrganizations] = useState([]);
  
  // ⚠️ Ceci s'exécute à CHAQUE rendu !
  const loadOrganizations = async () => {
    try {
      const data = await api.getOrganizationsByUser(userData.id, token);
      console.log("[v0] organizationsData", data); // Ne s'affiche qu'une fois
      setOrganizations(data);
    } catch (error) {
      console.error("[v0] Erreur fetch organizations", error);
    }
  };

  loadOrganizations(); // ❌ Appelé directement
  
  // ... code
}
```

### Solution 2: Utiliser useEffect correctement

```typescript
// ✅ Bon - loadOrganizations s'exécute une seule fois au montage
export default function Organizations() {
  const [organizations, setOrganizations] = useState([]);
  
  useEffect(() => {
    const loadOrganizations = async () => {
      try {
        const data = await api.getOrganizationsByUser(userData.id, token);
        console.log("[v0] organizationsData", data); // ✅ S'affiche maintenant
        setOrganizations(data);
      } catch (error) {
        console.error("[v0] Erreur fetch organizations", error);
      }
    };
    
    loadOrganizations();
  }, [userData.id, token]); // Dépendances
  
  // ... code
}
```

### Solution 3: Utiliser SWR (Recommandé)

```typescript
import useSWR from 'swr';
import API from '../utils/API';

export default function Organizations() {
  const api = new API();
  const { data: organizations, error, isLoading } = useSWR(
    userData?.id ? `/organizations/user/${userData.id}/detailed` : null,
    (url) => api.getOrganizationsByUser(userData.id, token),
    {
      revalidateOnFocus: false,
      onSuccess: (data) => {
        console.log("[v0] organizationsData loaded:", data);
      }
    }
  );

  if (isLoading) return <div>Chargement...</div>;
  if (error) return <div>Erreur: {error.message}</div>;

  return (
    <div>
      {organizations?.map(org => (
        <div key={org.id}>
          <h3>{org.name}</h3>
          <p>Membres: {org.members.map(m => m.name).join(', ')}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Migration vers les endpoints détaillés

### Avant: Deux requêtes HTTP

```typescript
// ❌ Ancien code - Nécessite 2 requêtes
const loadOrganizationData = async (orgId) => {
  try {
    // Requête 1: Récupérer l'organisation
    const org = await api.getOrganization(orgId);
    console.log("[v0] Organization:", org);
    
    // Requête 2: Récupérer les membres
    const members = await api.getOrganizationMembers(orgId);
    console.log("[v0] Members:", members);
    
    const completeOrg = { ...org, members };
    setSelectedOrg(completeOrg);
  } catch (error) {
    console.error("[v0] Erreur", error);
  }
};
```

### Après: Une seule requête avec données imbriquées

```typescript
// ✅ Nouveau code - Une seule requête
const loadOrganizationData = async (orgId) => {
  try {
    // Une seule requête retourne tout !
    const org = await api.getOrganizationDetailed(orgId);
    console.log("[v0] Organization with members:", org);
    
    // Accès direct aux membres
    org.members.forEach(member => {
      console.log("[v0] Member:", member.name, member.email);
    });
    
    setSelectedOrg(org);
  } catch (error) {
    console.error("[v0] Erreur", error);
  }
};
```

---

## Mise à jour de la classe API

Ajoutez ces méthodes à votre classe `API`:

```typescript
// src/utils/API.ts
export default class API {
  // ... méthodes existantes

  // Organizations - Détaillé
  async getOrganizationDetailed(orgId: string, token: string) {
    const response = await fetch(`${this.baseUrl}/organizations/${orgId}/detailed`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Failed to fetch organization');
    return response.json();
  }

  async getOrganizationsByUserDetailed(userId: string, token: string) {
    const response = await fetch(`${this.baseUrl}/organizations/user/${userId}/detailed`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Failed to fetch organizations');
    return response.json();
  }

  // Projects - Détaillé
  async getProjectDetailed(projectId: string, token: string) {
    const response = await fetch(`${this.baseUrl}/projects/${projectId}/detailed`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Failed to fetch project');
    return response.json();
  }

  async getProjectsByOrganizationDetailed(orgId: string, token: string) {
    const response = await fetch(
      `${this.baseUrl}/projects/organization/${orgId}/detailed`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (!response.ok) throw new Error('Failed to fetch projects');
    return response.json();
  }

  async getUserProjectsDetailed(token: string) {
    const response = await fetch(`${this.baseUrl}/projects/user/projects/detailed`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Failed to fetch user projects');
    return response.json();
  }

  // Translation Files - Détaillé
  async getTranslationFileDetailed(projectId: string, fileId: string, token: string) {
    const response = await fetch(
      `${this.baseUrl}/projects/${projectId}/files/${fileId}/detailed`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (!response.ok) throw new Error('Failed to fetch translation file');
    return response.json();
  }

  async getTranslationFilesDetailed(projectId: string, token: string) {
    const response = await fetch(
      `${this.baseUrl}/projects/${projectId}/files/detailed`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (!response.ok) throw new Error('Failed to fetch translation files');
    return response.json();
  }
}
```

---

## Exemples d'utilisation

### 1. Charger une organisation avec ses membres

```typescript
useEffect(() => {
  const loadOrgData = async () => {
    try {
      // Une seule requête pour l'organisation ET ses membres
      const org = await api.getOrganizationDetailed(orgId, token);
      
      console.log("[v0] Org data:", org);
      console.log("[v0] Number of members:", org.members.length);
      
      // Afficher les membres
      org.members.forEach(member => {
        console.log(`[v0] Member: ${member.name} (${member.email})`);
      });
      
      setSelectedOrg(org);
    } catch (error) {
      console.error("[v0] Error loading organization:", error);
      toast.error("Erreur lors du chargement");
    }
  };

  loadOrgData();
}, [orgId]);
```

### 2. Afficher les fichiers de traduction avec leurs messages

```typescript
useEffect(() => {
  const loadFiles = async () => {
    try {
      // Une seule requête pour tous les fichiers avec leurs messages
      const files = await api.getTranslationFilesDetailed(projectId, token);
      
      console.log("[v0] Files loaded:", files.length);
      
      files.forEach(file => {
        console.log(`[v0] ${file.language_name}: ${file.messages.length} messages`);
        
        const approved = file.messages.filter(m => m.reviewed_by !== null).length;
        console.log(`[v0]   Approuvés: ${approved}/${file.messages.length}`);
      });
      
      setFiles(files);
    } catch (error) {
      console.error("[v0] Error loading files:", error);
    }
  };

  loadFiles();
}, [projectId]);
```

### 3. Comparer avant/après les requêtes

```typescript
// ❌ AVANT: 3 requêtes HTTP
async function loadProjectOldWay(projectId) {
  const project = await fetch(`/projects/${projectId}`);
  const members = await fetch(`/projects/${projectId}/members`);
  const files = await fetch(`/projects/${projectId}/files`);
  
  console.log("Requêtes: 3"); // 🔴
}

// ✅ APRÈS: 1 requête HTTP
async function loadProjectNewWay(projectId) {
  const project = await fetch(`/projects/${projectId}/detailed`);
  // Contient: project + members
  // Pour les fichiers: fetch(`/projects/${projectId}/files/detailed`)
  // Contient: tous les fichiers + messages
  
  console.log("Requêtes: 1-2 au lieu de 3-4"); // 🟢
}
```

---

## Checklist de Migration

- [ ] Metter à jour la classe `API` avec les nouvelles méthodes détaillées
- [ ] Remplacer `loadOrganizations()` par une version avec `useEffect`
- [ ] Changer `api.getOrganizationsByUser()` → `api.getOrganizationsByUserDetailed()`
- [ ] Supprimer les appels séparés pour les membres (maintenant imbriqués)
- [ ] Tester que les `console.log` s'affichent dans la DevTools
- [ ] Vérifier dans le network tab qu'il y a moins de requêtes
- [ ] Décommenter les `console.log("[v0] ...")` pour déboguer
- [ ] Utiliser les données imbriquées: `org.members` au lieu de requête séparée

---

## Debugging: Vérifier les console.log

```typescript
// ✅ Bonne pratique pour voir les logs
useEffect(() => {
  console.log("[v0] Component mounted");
  
  const loadData = async () => {
    console.log("[v0] Starting async fetch...");
    
    try {
      const data = await api.getOrganizationDetailed(orgId, token);
      console.log("[v0] Data received:", data); // ✅ S'affichera maintenant
      console.log("[v0] Members:", data.members);
    } catch (error) {
      console.error("[v0] Error occurred:", error); // ✅ S'affichera en rouge
    }
  };
  
  loadData();
}, [orgId, token]);
```

Pour vérifier les logs:
1. Ouvrir DevTools (F12)
2. Aller à "Console"
3. Chercher les messages avec "[v0]"
4. Si rien n'apparaît → Vérifier que `useEffect` est en place
5. Vérifier "Network" tab pour voir les requêtes HTTP réelles
