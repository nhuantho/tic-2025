"""
Migration to add file_type column to api_specs table
"""
from sqlalchemy import text
from app.core.database import engine

def upgrade():
    """Add file_type column to api_specs table"""
    with engine.connect() as conn:
        # Add file_type column
        conn.execute(text("""
            ALTER TABLE api_specs 
            ADD COLUMN file_type VARCHAR(50)
        """))
        
        # Update existing records to have file_type = 'openapi' (assuming they are OpenAPI specs)
        conn.execute(text("""
            UPDATE api_specs 
            SET file_type = 'openapi' 
            WHERE file_type IS NULL
        """))
        
        conn.commit()

def downgrade():
    """Remove file_type column from api_specs table"""
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE api_specs 
            DROP COLUMN file_type
        """))
        conn.commit()

if __name__ == "__main__":
    print("Adding file_type column to api_specs table...")
    upgrade()
    print("Migration completed successfully!") 