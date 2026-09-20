from app.core.security import verify_password
from app.core.database import async_session_factory
from sqlalchemy import text
import asyncio

async def main():
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT password_hash FROM users WHERE email='test@test.com'"))
        h = r.scalar_one()
        print(f"Hash: {h}")
        print(f"Verify Test123456!: {verify_password('Test123456!', h)}")
        print(f"Verify admin123456: {verify_password('admin123456', h)}")

asyncio.run(main())
