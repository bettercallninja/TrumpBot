#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test to see if database tables exist
"""

import platform
import psycopg
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/trumpbot")

def test_tables():
    """Test if tables exist using simple psycopg"""
    try:
        # Simple synchronous test
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN (
                        'players', 'groups', 'attacks', 'inventories', 
                        'purchases', 'cooldowns', 'tg_stars_purchases', 'active_defenses'
                    )
                """)
                result = cur.fetchone()
                count = result[0] if result else 0
                
                print(f"Database tables found: {count}/8")
                
                if count == 8:
                    print("✅ All database tables exist!")
                    return True
                else:
                    print("❌ Some tables are missing")
                    
                    # List existing tables
                    cur.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """)
                    tables = cur.fetchall()
                    
                    print("Existing tables:")
                    for table in tables:
                        print(f"  - {table[0]}")
                    return False
                        
    except Exception as e:
        print(f"Error testing database: {e}")
        return False

if __name__ == "__main__":
    test_tables()
