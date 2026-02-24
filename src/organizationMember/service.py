from datetime import datetime, timezone
from turtle import up
from sqlalchemy.orm import Session
from src.entities.organizationMember import OrganizationMember
from src.entities.user import User
from src.entities.organization import Organization
from . import models 
import logging
"""
# 1. Fonction de création d es organisationMember
@Paramètres 
- organization_id 
- user_id
-role
-created_at 

"""

def create_organization_member(db: Session, data:models.OrganizationMemberCreate) -> OrganizationMember:
    logging.debug("Starting organization member creation")
    check_user = db.query(User).filter(User.id==data.user_id).first()
    check_org = db.query(Organization).filter(Organization.id == data.organization_id).first()
    message = ""
    
    if check_user and check_org:
        member = OrganizationMember(
            organization_id=data.organization_id,
            user_id=data.user_id,
            role=data.role,
            created_at=datetime.utcnow()
        )

        db.add(member)
        db.commit()
        db.refresh(member)
        logging.info(f"An organization member is added with org id : {data.organization_id} and user_id : {data.user_id}")
        return member
    else : 
        if not check_user:
            message = message + "Utilisateur ayant cet id n'existe pas dans la base de données utilisateurs"
        if not check_org:
            message = message + "\n Organization ayany cet id n'existe pas dans la base de données des orgnizations" 
        return message   
    



"""
# 2. Fonction de suppression des organisationMember
@Paramètres 
- organization_id 
- user_id
 On peut supprimer par user_id ou on peut supprimer par organization_id
"""
def delete_by_user(db: Session, user_id) -> None:
    logging.debug(f"Deleting members of user {user_id}")

    members = db.query(OrganizationMember)\
        .filter(OrganizationMember.user_id == user_id)\
        .all()

    if not members:
        raise Exception("Membre non trouvé")

    for member in members:
        db.delete(member)

    db.commit()

def delete_by_organization(db: Session, organization_id) -> None:
    logging.debug(f"Deleting members of organization {organization_id}")

    members = db.query(OrganizationMember)\
        .filter(OrganizationMember.organization_id == organization_id)\
        .all()

    if not members:
        raise Exception("Membres non trouvés")

    for member in members:
        db.delete(member)

    db.commit()
    
def delete_member(db: Session, organization_id, user_id) -> None:
    logging.debug(f"Deleting user {user_id} from organization {organization_id}")

    member = db.query(OrganizationMember)\
        .filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id
        )\
        .first()

    if not member:
        raise Exception("Membre non trouvé")

    db.delete(member)
    db.commit()
"""
# 3. Fonction de lecture des organisationMember
@Paramètres 
- organization_id 
- user_id
-role 
- name_user : le nom de l'utilisateur (join la table user on user_id)
-email_user : email de l'utilisateur (join la table user on user_id)
 On peut supprimer par user_id ou on peut supprimer par organization_id
"""


# def get_members(db: Session, user_id = None, organization_id = None, role = None)  -> None:
#     logging.debug(f"Fetching organizations members ")

#     query = db.query(
#         OrganizationMember.organization_id,
#         OrganizationMember.user_id,
#         OrganizationMember.role,
#         User.name.label("name_user"),
#         User.email.label("email_user"),
#         OrganizationMember.created_at,
#         OrganizationMember.updated_at
#     ).join(User, OrganizationMember.user_id == User.id)

    

#     if not results:
#         logging.warning(f"Membres {user_id} de role {role} non trouvé au sein de l'organization {organization_id}") 
#     # je veux juste retourner un statut avec un message
#         return {"message": "Aucun membre trouvé"}
#     if organization_id:
#         query = query.filter(OrganizationMember.organization_id == organization_id)

#     if user_id:
#         query = query.filter(OrganizationMember.user_id == user_id)

#     if role:
#         query = query.filter(OrganizationMember.role == role)
#     results = query.all()
#     return query.all()

def get_members(db: Session, user_id=None, organization_id=None, role=None):

    logging.debug("Fetching organization members")

    query = (
        db.query(OrganizationMember)
        .join(User, OrganizationMember.user_id == User.id)
        .join(Organization, OrganizationMember.organization_id == Organization.id)
    )

    # 🔹 Appliquer les filtres AVANT .all()
    if organization_id:
        query = query.filter(OrganizationMember.organization_id == organization_id)

    if user_id:
        query = query.filter(OrganizationMember.user_id == user_id)

    if role:
        query = query.filter(OrganizationMember.role == role)

    members = query.all()

    if not members:
        logging.warning(
            f"Membres {user_id} de role {role} non trouvé au sein de l'organization {organization_id}"
        )
        return []  # Toujours une liste si response_model=List[...]

    # 🔹 Mapping propre vers Pydantic
    return [
        {
            "organization_id": m.organization_id,
            "user_id": m.user_id,
            "org_name": m.organization.name,
            "user_name": m.user.name,
            "user_email": m.user.email,
            "role": m.role,  # IMPORTANT: Enum, pas .value
        }
        for m in members
    ]

"""
# 3. Fonction de modification des organisationMember
@Paramètres 
- organization_id 
- user_id
-role 
 on modifie juste le role de l'utilisateur et on met updated at à now.
 
 """

def update_member_role(db: Session, update_data : models.OrganizationMemberUpdate):
    logging.debug(f"Updating organizationMember org_id {update_data.organization_id} \n user_id{update_data.user_id}")
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == update_data.organization_id,
        OrganizationMember.user_id == update_data.user_id
    ).first()

    if not member:
        return None
    if update_data.new_role is not None : 
        member.role = update_data.new_role
    member.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(member)

    logging.info(f"Organization member role updated: {update_data.new_role}")
    return member