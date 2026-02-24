from ast import Or
from sqlalchemy.orm import Session 
from uuid import UUID
from datetime import datetime, timezone
import logging

from src.entities.organization import Organization
from . import models


# Fonction backend des organisations 

"""
# 1. Fonction de création des organisations
@Paramètres 

- nom
- description
- created_at
- created_by 

"""

def create_organization(db:Session, org_data: models.OrganizationCreate, user_id) -> Organization:
    logging.debug("Starting organization creation")

    new_org = Organization(
        name = org_data.name.lower(),
        description=org_data.description,
        created_at= datetime.now(timezone.utc),
        created_by = user_id
        
    )

    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    logging.info(f"Organization created with ID : {new_org.id}")
    return new_org


"""

 
# 2. Fonction de suppression des organisations
@Paramètres 
 - on get l'id de l'organisation 
 - on supprime de la BD 

"""

def delete_organization(db:Session, org_id:UUID) -> None:
    logging.debug(f"Attempting to delete orgnanization {org_id}")
    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        logging.warning(f"Organization not found with ID: {org_id}")
        raise Exception ("Organization not found")

    db.delete(org)
    db.commit()

    logging.info(f"Organization deleted : {org_id}")
"""
# 3. Fonction de modifications des organisations
@Paramètres 
 - on get l'id de l'organisation 
 - on modifies les champs modifié (nom, description et on enregistre updated_at à default now)

"""
def update_organization (db: Session, org_id: UUID, update_data:models.OrganizationUpdate)->Organization:
    logging.debug(f"Updating organization {org_id}")

    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org: 
        logging.warning(f"Organization not found : {org_id}")
        raise Exception ("Organization not found")

    if update_data.name is not None: 
        org.name = update_data.name
    if update_data.description is not None:
        org.description = update_data.description
    
    org.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(org)

    logging.info(f"Organization updated: {org_id}")
    return org

"""
# 4. Fonction de lecture des organisations
@Listes des fonctions de lecture 

 -  Fonction de lecture par id
 -  Fonction de lecture par nom 
 -  Fonction de lecture des organisations par id_user. 
 
"""




def get_organization_by_id(db:Session, org_id:UUID)->Organization:
    logging.debug(f"Fetching organization by ID : {org_id} ")

    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org: 
        logging.warning(f"Organization not found : {org_id}")
        raise Exception ("organization not found")

    return org
def get_organization_by_name (db:Session, name:str)->Organization:
    logging.debug(f"Fetchin organization by name")

    org = db.query(Organization).filter(Organization.name == name).first()

    if not org: 
        logging.warning(f"Organization not found : {name}")
        raise Exception ("Organization not found")

    return org

def get_organizations_by_user (db: Session, user_id:UUID):
    logging.debug(f"Fetching Organizations for user : {user_id}")

    org =  db.query(Organization).filter(Organization.created_by== user_id).all()

    if not org: 
        logging.warning(f"Organization not found : {user_id}")
        raise Exception ("Organization not found")

    return org
