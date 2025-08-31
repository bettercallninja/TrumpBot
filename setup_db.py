#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database setup script with Windows compatibility
"""

import platform

# Fix Windows event loop policy early for psycopg compatibility
if platform.system() == 'Windows':
    import asyncio
    try:
        # Set Windows-compatible event loop policy for async database operations
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        print("✅ Windows event loop policy set")
    except (AttributeError, RuntimeError) as e:
        print(f"⚠️  Could not set event loop policy: {e}")

import asyncio
from src.database.db_manager import setup_database

async def main():
    """Run database setup"""
    try:
        print("🔧 Starting database setup...")
        await setup_database()
        print("✅ Database setup completed successfully!")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
