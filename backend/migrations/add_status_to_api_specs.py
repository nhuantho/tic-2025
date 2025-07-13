"""
Migration script to add status column to api_specs table
"""
from sqlalchemy import text
from app.core.database import engine

def upgrade():
    """Add status column to api_specs table"""
    with engine.connect() as conn:
        # Add status column with default value 'success'
        conn.execute(text("""
            ALTER TABLE api_specs 
            ADD COLUMN status VARCHAR(20) DEFAULT 'success'
        """))
        
        # Update existing records to have 'success' status
        conn.execute(text("""
            UPDATE api_specs 
            SET status = 'success' 
            WHERE status IS NULL
        """))
        
        conn.commit()

def downgrade():
    """Remove status column from api_specs table"""
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE api_specs 
            DROP COLUMN status
        """))
        conn.commit()

if __name__ == "__main__":
    print("Adding status column to api_specs table...")
    upgrade()
    print("Migration completed successfully!") 