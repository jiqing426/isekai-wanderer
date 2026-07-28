"""数据库迁移脚本 - 添加聊天消息和推荐话题表"""
import asyncio
from sqlalchemy import text
from app.core.database import engine


async def migrate():
    """执行数据库迁移"""
    
    async with engine.begin() as conn:
        # 创建聊天消息表
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                character_id UUID NOT NULL,
                user_id UUID NOT NULL,
                sender_type VARCHAR(10) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_chat_messages_character_id 
            ON chat_messages(character_id);
            
            CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id 
            ON chat_messages(user_id);
            
            CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at 
            ON chat_messages(created_at);
        """))
        
        # 创建推荐话题表
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_topics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                character_id UUID NOT NULL,
                topic_text TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0
            );
            
            CREATE INDEX IF NOT EXISTS idx_chat_topics_character_id 
            ON chat_topics(character_id);
        """))
        
        print("✅ 数据库迁移完成：chat_messages, chat_topics")


if __name__ == "__main__":
    asyncio.run(migrate())
