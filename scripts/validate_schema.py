#!/usr/bin/env python3
"""
Schema validation script - Verify database was set up correctly
Checks that all tables, columns, and constraints exist
"""

from sqlalchemy import inspect, text
from src.database.core import engine


def validate_schema():
    """Validate that all required tables and columns exist"""
    inspector = inspect(engine)
    
    # Expected tables
    expected_tables = {
        "organizations",
        "users",
        "projects",
        "project_members",
        "translation_files",
        "messages",
        "translation_versions",
        "audit_logs",
    }
    
    # Expected columns by table
    expected_columns = {
        "organizations": {
            "id", "name", "description", "created_by", "created_at", "updated_at"
        },
        "users": {
            "id", "email", "name", "password_hash", "created_at", "updated_at"
        },
        "projects": {
            "id", "name", "description", "organization_id", "created_by",
            "source_language", "target_languages", "created_at", "updated_at"
        },
        "project_members": {
            "id", "project_id", "user_id", "role", "created_at", "updated_at"
        },
        "translation_files": {
            "id", "project_id", "created_by", "language_code", "language_name",
            "current_version", "created_at", "updated_at"
        },
        "messages": {
            "id", "file_id", "created_by", "key", "value", "comment",
            "status", "reviewed_by", "created_at", "updated_at"
        },
        "translation_versions": {
            "id", "file_id", "created_by", "version_number", "snapshot_json", "created_at"
        },
        "audit_logs": {
            "id", "user_id", "project_id", "action", "entity_type",
            "entity_id", "details", "created_at"
        },
    }
    
    # Check tables exist
    existing_tables = set(inspector.get_table_names())
    print("Checking tables...")
    for table in expected_tables:
        if table in existing_tables:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ MISSING: {table}")
            return False
    
    # Check columns
    print("\nChecking columns...")
    all_good = True
    for table, expected_cols in expected_columns.items():
        existing_cols = {col["name"] for col in inspector.get_columns(table)}
        missing = expected_cols - existing_cols
        extra = existing_cols - expected_cols
        
        if not missing and not extra:
            print(f"  ✓ {table}")
        else:
            all_good = False
            print(f"  ✗ {table}")
            if missing:
                print(f"    Missing columns: {missing}")
            if extra:
                print(f"    Extra columns: {extra}")
    
    # Check constraints
    print("\nChecking constraints...")
    with engine.connect() as conn:
        # Check unique constraints
        unique_constraints = {
            "uq_org_project_name": "projects",
            "uq_project_user": "project_members",
            "uq_project_language": "translation_files",
            "uq_file_message_key": "messages",
        }
        
        for constraint, table in unique_constraints.items():
            try:
                constraints = inspector.get_unique_constraints(table)
                constraint_names = [c.get("name") for c in constraints]
                if constraint in constraint_names:
                    print(f"  ✓ {constraint}")
                else:
                    print(f"  ✗ MISSING: {constraint}")
                    all_good = False
            except Exception as e:
                print(f"  ? Could not check {constraint}: {e}")
    
    # Check enums
    print("\nChecking enum types...")
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT typname FROM pg_type WHERE typkind = 'e'"
        ))
        enum_types = {row[0] for row in result}
        
        expected_enums = {
            "translationstatus",  # lowercase in PostgreSQL
            "projectrole",
            "auditaction",
            "auditentitytype",
            "messagestatus",
        }
        
        for enum_type in expected_enums:
            if enum_type in enum_types:
                print(f"  ✓ {enum_type}")
            else:
                print(f"  ✗ MISSING: {enum_type}")
                all_good = False
    
    # Summary
    print("\n" + "="*50)
    if all_good:
        print("✓ Schema validation PASSED")
        print("Database is ready for use!")
        return True
    else:
        print("✗ Schema validation FAILED")
        print("Please run: python scripts/create_schema.sql")
        return False


if __name__ == "__main__":
    import sys
    success = validate_schema()
    sys.exit(0 if success else 1)
