# seed_database.py
"""
Script de seed (données initiales / test) pour la base de données de gestion de traductions
Exécuter APRÈS avoir appliqué la migration alembic (upgrade head)
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# ────────────────────────────────────────────────
#  À ADAPTER selon ton projet
# ────────────────────────────────────────────────
DATABASE_URL = "postgresql+psycopg2://postgres:felicia@localhost:5432/RHOpenLabs"
# Exemples :
# "sqlite:///./test.db"
# "postgresql://postgres:postgres@localhost:5432/translation_db"

engine = create_engine(DATABASE_URL, echo=False)


# ────────────────────────────────────────────────
# Enums (doivent correspondre exactement à ceux de la base)
# ────────────────────────────────────────────────
class Priority(str, Enum):
    Low = "Low"
    Normal = "Normal"
    Medium = "Medium"
    High = "High"
    Top = "Top"


class OrgRole(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class ProjectRole(str, Enum):
    LEAD = "LEAD"
    TRANSLATOR = "TRANSLATOR"
    REVIEWER = "REVIEWER"


class MessageStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"


# ────────────────────────────────────────────────
# Fonctions utilitaires
# ────────────────────────────────────────────────
def now():
    return datetime.utcnow()


def hash_password(plain: str) -> str:
    # En prod → utiliser bcrypt ou argon2
    # Pour le seed on simule
    return f"fakehash_{plain}"


# ────────────────────────────────────────────────
# Données de test
# ────────────────────────────────────────────────
def seed_data(session: Session):
    # -----------------------
    # Utilisateurs
    # -----------------------
    users_data = [
        {"email": "alice@company.com", "name": "Alice Dupont", "password": "alice2026"},
        {"email": "bob@freelance.fr", "name": "Bob Martin", "password": "bob trad"},
        {"email": "carla@agency.io", "name": "Carla Rossi", "password": "carla-lead"},
        {"email": "david.dev@corp.com", "name": "David Lefèvre", "password": "david123"},
    ]

    users = {}
    for u in users_data:
        user_id = uuid.uuid4()
        session.execute(
            """
            INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
            VALUES (:id, :email, :name, :pwd, :created, NULL)
            """,
            {
                "id": user_id,
                "email": u["email"],
                "name": u["name"],
                "pwd": hash_password(u["password"]),
                "created": now(),
            },
        )
        users[u["email"]] = user_id

    session.flush()

    # -----------------------
    # Organisations
    # -----------------------
    orgs = {}
    org_data = [
        {"name": "GlobalTech Solutions", "desc": "Entreprise internationale de logiciels", "created_by": users["alice@company.com"]},
        {"name": "Traduction Express", "desc": "Agence de traduction rapide", "created_by": users["carla@agency.io"]},
    ]

    for o in org_data:
        org_id = uuid.uuid4()
        session.execute(
            """
            INSERT INTO organizations (id, name, description, created_by, created_at)
            VALUES (:id, :name, :desc, :cb, :created)
            """,
            {
                "id": org_id,
                "name": o["name"],
                "desc": o["desc"],
                "cb": o["created_by"],
                "created": now(),
            },
        )
        orgs[o["name"]] = org_id

    session.flush()

    # -----------------------
    # Membres d'organisations
    # -----------------------
    session.execute(
        """
        INSERT INTO organization_members (id, organization_id, user_id, role, created_at)
        VALUES
            (:mid1, :oid1, :uid1, 'ADMIN', :now),
            (:mid2, :oid1, :uid2, 'MEMBER', :now),
            (:mid3, :oid2, :uid3, 'ADMIN', :now),
            (:mid4, :oid2, :uid4, 'MEMBER', :now)
        """,
        {
            "mid1": uuid.uuid4(),
            "mid2": uuid.uuid4(),
            "mid3": uuid.uuid4(),
            "mid4": uuid.uuid4(),
            "oid1": orgs["GlobalTech Solutions"],
            "oid2": orgs["Traduction Express"],
            "uid1": users["alice@company.com"],
            "uid2": users["bob@freelance.fr"],
            "uid3": users["carla@agency.io"],
            "uid4": users["david.dev@corp.com"],
            "now": now(),
        },
    )

    # -----------------------
    # Projets
    # -----------------------
    projects = {}
    project_data = [
        {
            "name": "Application Mobile v2.1",
            "desc": "Localisation de la nouvelle version mobile",
            "org": "GlobalTech Solutions",
            "created_by": users["alice@company.com"],
            "source": "en",
            "targets": "fr,es,de,it",
        },
        {
            "name": "Site E-commerce 2026",
            "desc": "Traduction multilingue du site marchand",
            "org": "Traduction Express",
            "created_by": users["carla@agency.io"],
            "source": "fr",
            "targets": "en,pl,pt",
        },
    ]

    for p in project_data:
        proj_id = uuid.uuid4()
        session.execute(
            """
            INSERT INTO projects (
                id, name, description, organization_id, created_by,
                source_language, target_languages, created_at
            )
            VALUES (:id, :name, :desc, :oid, :cb, :src, :tgt, :created)
            """,
            {
                "id": proj_id,
                "name": p["name"],
                "desc": p["desc"],
                "oid": orgs[p["org"]],
                "cb": p["created_by"],
                "src": p["source"],
                "tgt": p["targets"],
                "created": now(),
            },
        )
        projects[p["name"]] = proj_id

    session.flush()

    # -----------------------
    # Membres de projets
    # -----------------------
    session.execute(
        """
        INSERT INTO project_members (id, project_id, user_id, role, created_at)
        VALUES
            (:m1, :p1, :u1, 'LEAD',      :now),
            (:m2, :p1, :u2, 'TRANSLATOR', :now),
            (:m3, :p1, :u4, 'REVIEWER',   :now),
            (:m4, :p2, :u3, 'LEAD',       :now),
            (:m5, :p2, :u2, 'TRANSLATOR', :now)
        """,
        {
            "m1": uuid.uuid4(),
            "m2": uuid.uuid4(),
            "m3": uuid.uuid4(),
            "m4": uuid.uuid4(),
            "m5": uuid.uuid4(),
            "p1": projects["Application Mobile v2.1"],
            "p2": projects["Site E-commerce 2026"],
            "u1": users["alice@company.com"],
            "u2": users["bob@freelance.fr"],
            "u3": users["carla@agency.io"],
            "u4": users["david.dev@corp.com"],
            "now": now(),
        },
    )

    # -----------------------
    # Fichiers de traduction (un par langue cible)
    # -----------------------
    translation_files = {}

    for proj_name, proj_id in projects.items():
        if proj_name == "Application Mobile v2.1":
            languages = ["fr", "es", "de", "it"]
        else:
            languages = ["en", "pl", "pt"]

        for lang in languages:
            file_id = uuid.uuid4()
            session.execute(
                """
                INSERT INTO translation_files (
                    id, project_id, language_code, language_name,
                    current_version, created_at
                )
                VALUES (:id, :pid, :code, :name, 0, :now)
                """,
                {
                    "id": file_id,
                    "pid": proj_id,
                    "code": lang,
                    "name": {"fr": "Français", "es": "Espagnol", "de": "Allemand", "it": "Italien",
                             "en": "English", "pl": "Polski", "pt": "Português"}[lang],
                    "now": now(),
                },
            )
            translation_files[(proj_name, lang)] = file_id

    session.flush()

    # -----------------------
    # Quelques messages / clés de traduction
    # -----------------------
    messages = [
        # Projet 1 - Français
        {"file": ("Application Mobile v2.1", "fr"), "key": "welcome.title", "value": "Bienvenue dans l'application !", "status": MessageStatus.APPROVED},
        {"file": ("Application Mobile v2.1", "fr"), "key": "button.save", "value": "Enregistrer", "status": MessageStatus.PENDING},
        # Projet 1 - Espagnol (quelques uns seulement)
        {"file": ("Application Mobile v2.1", "es"), "key": "welcome.title", "value": "¡Bienvenido a la aplicación!", "status": MessageStatus.APPROVED},
        # Projet 2 - Anglais
        {"file": ("Site E-commerce 2026", "en"), "key": "cart.title", "value": "Your Shopping Cart", "status": MessageStatus.APPROVED},
        {"file": ("Site E-commerce 2026", "en"), "key": "checkout.button", "value": "Proceed to Checkout", "status": MessageStatus.PENDING},
    ]

    for msg in messages:
        file_id = translation_files[msg["file"]]
        session.execute(
            """
            INSERT INTO messages (
                id, file_id, key, value, status, created_at
            )
            VALUES (:id, :fid, :key, :val, :status, :now)
            """,
            {
                "id": uuid.uuid4(),
                "fid": file_id,
                "key": msg["key"],
                "val": msg.get("value"),
                "status": msg["status"],
                "now": now(),
            },
        )

    # Optionnel : quelques todos pour tester
    session.execute(
        """
        INSERT INTO todos (id, user_id, description, due_date, is_completed, priority, created_at)
        VALUES
            (:t1, :u1, 'Revoir les traductions FR', :due1, false, 'High', :now),
            (:t2, :u2, 'Traduire les 48 nouvelles clés', :due2, false, 'Medium', :now)
        """,
        {
            "t1": uuid.uuid4(),
            "t2": uuid.uuid4(),
            "u1": users["alice@company.com"],
            "u2": users["bob@freelance.fr"],
            "due1": now() + timedelta(days=3),
            "due2": now() + timedelta(days=7),
            "now": now(),
        },
    )

    print("Données de test insérées avec succès !")


def main():
    with Session(engine) as session:
        with session.begin():
            seed_data(session)
        print("Commit effectué.")


if __name__ == "__main__":
    main()