"""Migration: CR-005 add TTS config and gender to characters table.

Adds columns:
  - characters.gender VARCHAR(10) DEFAULT 'female'
  - characters.tts_config JSONB

Usage:
  python migrations/002_add_character_tts_config.py
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine


ALTER_CHARACTERS_ADD_TTS = """
ALTER TABLE characters ADD COLUMN IF NOT EXISTS gender VARCHAR(10) NOT NULL DEFAULT 'female';
ALTER TABLE characters ADD COLUMN IF NOT EXISTS tts_config JSONB;
"""


async def run_migration():
    """Execute migration DDL statements."""
    print("Running CR-005 migration (add character tts_config + gender)...")

    async with engine.begin() as conn:
        print("  Altering characters table (adding gender, tts_config)...")
        await conn.execute(text(ALTER_CHARACTERS_ADD_TTS))

    print("CR-005 migration completed successfully.")


if __name__ == "__main__":
    asyncio.run(run_migration())
