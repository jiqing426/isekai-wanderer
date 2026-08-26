#!/usr/bin/env python3
"""
迁移脚本：将所有非UUID v4格式的ID转换为UUID v4格式

依赖关系：
- scripts (3条，全部v4) - 不需要修改
- characters (9条，全部v4) - 不需要修改  
- routes (11条，8条v4) - 被nodes引用
- nodes (92条，50条v4) - 引用routes，被node_choices, game_sessions, game_progress引用

更新顺序：
1. 备份数据库
2. 更新routes（因为被nodes引用）
3. 更新nodes（因为被其他表引用）
4. 更新所有引用nodes的表
"""

import os
import sys
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Tuple
import json

# 数据库连接配置
DB_CONFIG = {
    'host': 'db',
    'port': '5432',
    'database': os.getenv('POSTGRES_DB', 'isekai'),
    'user': os.getenv('POSTGRES_USER', 'isekai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'isekai_password')
}

def is_uuid_v4(uuid_str: str) -> bool:
    """检查是否为UUID v4格式"""
    import re
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_str, re.IGNORECASE))

def generate_uuid_v4() -> str:
    """生成UUID v4"""
    return str(uuid.uuid4())

def backup_database(conn):
    """备份数据库（创建备份表）"""
    print("📦 正在备份数据库...")
    
    tables = ['routes', 'nodes', 'node_choices', 'game_sessions', 'game_progress']
    
    with conn.cursor() as cur:
        for table in tables:
            backup_table = f"{table}_backup"
            cur.execute(f"DROP TABLE IF EXISTS {backup_table}")
            cur.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {table}")
            print(f"  ✓ 备份 {table} -> {backup_table}")
    
    conn.commit()
    print("✅ 数据库备份完成\n")

def get_non_v4_records(conn, table: str) -> List[Dict]:
    """获取表中所有非UUID v4格式的记录"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT id::text as id
            FROM {table}
            WHERE id::text !~ '^[0-9a-f]{{8}}-[0-9a-f]{{4}}-4[0-9a-f]{{3}}-[89ab][0-9a-f]{{3}}-[0-9a-f]{{12}}$'
        """)
        return cur.fetchall()

def create_id_mapping(old_ids: List[str]) -> Dict[str, str]:
    """创建旧ID到新UUID v4的映射"""
    mapping = {}
    for record in old_ids:
        old_id = record['id']
        new_id = generate_uuid_v4()
        mapping[old_id] = new_id
    return mapping

def update_routes(conn, id_mapping: Dict[str, str]):
    """更新routes表的ID"""
    print("🔄 正在更新 routes 表...")
    
    with conn.cursor() as cur:
        # 暂时禁用外键约束
        cur.execute("SET session_replication_role = 'replica';")
        
        # 更新routes表的主键
        for old_id, new_id in id_mapping.items():
            cur.execute("""
                UPDATE routes 
                SET id = %s::uuid 
                WHERE id = %s::uuid
            """, (new_id, old_id))
            print(f"  ✓ 更新 routes.id: {old_id} -> {new_id}")
        
        # 更新nodes表中的route_id外键
        for old_id, new_id in id_mapping.items():
            cur.execute("""
                UPDATE nodes 
                SET route_id = %s::uuid 
                WHERE route_id = %s::uuid
            """, (new_id, old_id))
            print(f"  ✓ 更新 nodes.route_id: {old_id} -> {new_id}")
        
        # 重新启用外键约束
        cur.execute("SET session_replication_role = 'origin';")
    
    conn.commit()
    print(f"✅ routes 表更新完成，共更新 {len(id_mapping)} 条记录\n")

def update_nodes(conn, id_mapping: Dict[str, str]):
    """更新nodes表的ID"""
    print("🔄 正在更新 nodes 表...")
    
    with conn.cursor() as cur:
        # 暂时禁用外键约束
        cur.execute("SET session_replication_role = 'replica';")
        
        # 更新nodes表的主键
        for old_id, new_id in id_mapping.items():
            cur.execute("""
                UPDATE nodes 
                SET id = %s::uuid 
                WHERE id = %s::uuid
            """, (new_id, old_id))
            print(f"  ✓ 更新 nodes.id: {old_id} -> {new_id}")
        
        # 更新node_choices表中的node_id外键
        for old_id, new_id in id_mapping.items():
            cur.execute("""
                UPDATE node_choices 
                SET node_id = %s::uuid 
                WHERE node_id = %s::uuid
            """, (new_id, old_id))
        
        # 更新node_choices表中的next_node_id外键
        for old_id, new_id in id_mapping.items():
            cur.execute("""
                UPDATE node_choices 
                SET next_node_id = %s::uuid 
                WHERE next_node_id = %s::uuid
            """, (new_id, old_id))
        
        # 更新game_sessions表中的current_node_id外键
        for old_id, new_id in id_mapping.items():
            cur.execute("""
                UPDATE game_sessions 
                SET current_node_id = %s::uuid 
                WHERE current_node_id = %s::uuid
            """, (new_id, old_id))
        
        # 更新game_progress表中的node_id外键
        for old_id, new_id in id_mapping.items():
            cur.execute("""
                UPDATE game_progress 
                SET node_id = %s::uuid 
                WHERE node_id = %s::uuid
            """, (new_id, old_id))
        
        # 更新nodes表中的parent_id外键
        for old_id, new_id in id_mapping.items():
            cur.execute("""
                UPDATE nodes 
                SET parent_id = %s::uuid 
                WHERE parent_id = %s::uuid
            """, (new_id, old_id))
        
        # 重新启用外键约束
        cur.execute("SET session_replication_role = 'origin';")
    
    conn.commit()
    print(f"✅ nodes 表更新完成，共更新 {len(id_mapping)} 条记录\n")

def verify_migration(conn):
    """验证迁移结果"""
    print("🔍 正在验证迁移结果...")
    
    tables = ['routes', 'nodes']
    
    with conn.cursor() as cur:
        for table in tables:
            cur.execute(f"""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN id::text ~ '^[0-9a-f]{{8}}-[0-9a-f]{{4}}-4[0-9a-f]{{3}}-[89ab][0-9a-f]{{3}}-[0-9a-f]{{12}}$' THEN 1 END) as v4_count
                FROM {table}
            """)
            result = cur.fetchone()
            total, v4_count = result
            
            if total == v4_count:
                print(f"  ✓ {table}: {v4_count}/{total} 条记录已转换为UUID v4")
            else:
                print(f"  ✗ {table}: {v4_count}/{total} 条记录是UUID v4（仍有 {total - v4_count} 条未转换）")
    
    print()

def main():
    """主函数"""
    print("=" * 60)
    print("UUID v4 迁移脚本")
    print("=" * 60)
    print()
    
    # 连接数据库
    print("🔌 正在连接数据库...")
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ 数据库连接成功\n")
    
    try:
        # 1. 备份数据库
        backup_database(conn)
        
        # 2. 更新routes表
        routes_records = get_non_v4_records(conn, 'routes')
        if routes_records:
            print(f"发现 {len(routes_records)} 条非UUID v4格式的routes记录")
            routes_mapping = create_id_mapping(routes_records)
            update_routes(conn, routes_mapping)
        else:
            print("✅ routes 表已全部是UUID v4格式，跳过\n")
        
        # 3. 更新nodes表
        nodes_records = get_non_v4_records(conn, 'nodes')
        if nodes_records:
            print(f"发现 {len(nodes_records)} 条非UUID v4格式的nodes记录")
            nodes_mapping = create_id_mapping(nodes_records)
            update_nodes(conn, nodes_mapping)
        else:
            print("✅ nodes 表已全部是UUID v4格式，跳过\n")
        
        # 4. 验证迁移结果
        verify_migration(conn)
        
        print("=" * 60)
        print("✅ 迁移完成！")
        print("=" * 60)
        print()
        print("⚠️  重要提示：")
        print("1. 备份表已创建：routes_backup, nodes_backup")
        print("2. 如需回滚，可从备份表恢复数据")
        print("3. 建议测试应用功能是否正常")
        print()
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        print("已回滚所有更改")
        sys.exit(1)
    
    finally:
        conn.close()
        print("🔌 数据库连接已关闭")

if __name__ == "__main__":
    main()
