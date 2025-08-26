#!/usr/bin/env python3
"""
读取数据库中sdx schema下的所有表结构
"""
import asyncio
import sys
import os
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def read_sdx_schema():
    """读取sdx schema下的所有表结构"""
    print("🔍 开始读取sdx schema下的表结构...")
    
    try:
        from app.core.config import settings
        import asyncpg
        
        # 连接到数据库
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        
        print(f"✅ 成功连接到数据库: {settings.postgres_db}")
        
        # 1. 获取sdx schema下的非sm开头的表
        print("\n📋 获取sdx schema下的非sm开头的表:")
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables 
            WHERE table_schema = 'sdx'
            AND table_type = 'BASE TABLE'
            AND table_name NOT LIKE 'sm%'
            ORDER BY table_name 
        """)
        
        if not tables:
            print("❌ 未找到sdx schema下的表")
            return
        
        print(f"找到 {len(tables)} 个表:")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # 2. 读取每个表的详细结构
        print("\n" + "="*80)
        print("📊 详细表结构信息")
        print("="*80)
        
        schema_info = {}
        
        for table in tables:
            table_name = table['table_name']
            print(f"\n🔍 表名: {table_name}")
            print("-" * 60)
            
            # 获取表结构
            columns = await conn.fetch("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    ordinal_position
                FROM information_schema.columns 
                WHERE table_schema = 'sdx' 
                AND table_name = $1
                ORDER BY ordinal_position
            """, table_name)
            
            # 获取主键信息
            primary_keys = await conn.fetch("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_schema = 'sdx'
                AND tc.table_name = $1
                AND tc.constraint_type = 'PRIMARY KEY'
                ORDER BY kcu.ordinal_position
            """, table_name)
            
            # 获取外键信息
            foreign_keys = await conn.fetch("""
                SELECT 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu 
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.table_schema = 'sdx'
                AND tc.table_name = $1
                AND tc.constraint_type = 'FOREIGN KEY'
                ORDER BY kcu.ordinal_position
            """, table_name)
            
            # 获取索引信息
            indexes = await conn.fetch("""
                SELECT 
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'sdx'
                AND tablename = $1
                ORDER BY indexname
            """, table_name)
            
            # 获取表的行数
            row_count = await conn.fetchval(f"SELECT COUNT(*) FROM sdx.{table_name}")
            
            # 存储表信息
            table_info = {
                'columns': [],
                'primary_keys': [],
                'foreign_keys': [],
                'indexes': [],
                'row_count': row_count
            }
            
            # 显示列信息
            print(f"📋 列结构 (共{len(columns)}列):")
            for col in columns:
                col_info = {
                    'name': col['column_name'],
                    'type': col['data_type'],
                    'nullable': col['is_nullable'],
                    'default': col['column_default'],
                    'max_length': col['character_maximum_length'],
                    'precision': col['numeric_precision'],
                    'scale': col['numeric_scale']
                }
                table_info['columns'].append(col_info)
                
                # 格式化显示
                nullable_str = "可空" if col['is_nullable'] == 'YES' else "非空"
                default_str = f"默认: {col['column_default']}" if col['column_default'] else ""
                length_str = f"长度: {col['character_maximum_length']}" if col['character_maximum_length'] else ""
                precision_str = f"精度: {col['numeric_precision']}" if col['numeric_precision'] else ""
                
                print(f"   {col['ordinal_position']:2d}. {col['column_name']:<20} {col['data_type']:<15} {nullable_str:<6} {default_str} {length_str} {precision_str}")
            
            # 显示主键信息
            if primary_keys:
                pk_columns = [pk['column_name'] for pk in primary_keys]
                table_info['primary_keys'] = pk_columns
                print(f"🔑 主键: {', '.join(pk_columns)}")
            
            # 显示外键信息
            if foreign_keys:
                print(f"🔗 外键关系:")
                for fk in foreign_keys:
                    fk_info = {
                        'column': fk['column_name'],
                        'foreign_table': fk['foreign_table_name'],
                        'foreign_column': fk['foreign_column_name']
                    }
                    table_info['foreign_keys'].append(fk_info)
                    print(f"   {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
            
            # 显示索引信息
            if indexes:
                print(f"📇 索引:")
                for idx in indexes:
                    idx_info = {
                        'name': idx['indexname'],
                        'definition': idx['indexdef']
                    }
                    table_info['indexes'].append(idx_info)
                    print(f"   {idx['indexname']}")
            
            # 显示行数
            print(f"📊 数据行数: {row_count:,}")
            
            # 存储到总信息中
            schema_info[table_name] = table_info
        
        # 3. 生成SQL创建语句
        print("\n" + "="*80)
        print("📝 SQL创建语句")
        print("="*80)
        
        for table_name, table_info in schema_info.items():
            print(f"\n-- 创建表: {table_name}")
            print(f"CREATE TABLE sdx.{table_name} (")
            
            column_definitions = []
            for col in table_info['columns']:
                col_def = f"    {col['name']} {col['type']}"
                
                if col['max_length']:
                    col_def += f"({col['max_length']})"
                elif col['precision'] and col['scale']:
                    col_def += f"({col['precision']},{col['scale']})"
                elif col['precision']:
                    col_def += f"({col['precision']})"
                
                if col['nullable'] == 'NO':
                    col_def += " NOT NULL"
                
                if col['default']:
                    col_def += f" DEFAULT {col['default']}"
                
                column_definitions.append(col_def)
            
            print(",\n".join(column_definitions))
            
            if table_info['primary_keys']:
                pk_columns = ", ".join(table_info['primary_keys'])
                print(f",\n    PRIMARY KEY ({pk_columns})")
            
            print(");")
            
            # 添加外键约束
            for fk in table_info['foreign_keys']:
                print(f"ALTER TABLE sdx.{table_name} ADD CONSTRAINT fk_{table_name}_{fk['column']} ")
                print(f"    FOREIGN KEY ({fk['column']}) REFERENCES sdx.{fk['foreign_table']}({fk['foreign_column']});")
            
            # 添加索引
            for idx in table_info['indexes']:
                if not idx['name'].endswith('_pkey'):  # 跳过主键索引
                    print(f"-- 索引: {idx['name']}")
                    print(f"-- {idx['definition']}")
        
        # 4. 生成统计报告
        print("\n" + "="*80)
        print("📈 统计报告")
        print("="*80)
        
        total_tables = len(schema_info)
        total_columns = sum(len(table_info['columns']) for table_info in schema_info.values())
        total_rows = sum(table_info['row_count'] for table_info in schema_info.values())
        total_indexes = sum(len(table_info['indexes']) for table_info in schema_info.values())
        
        print(f"📊 总表数: {total_tables}")
        print(f"📊 总列数: {total_columns}")
        print(f"📊 总行数: {total_rows:,}")
        print(f"📊 总索引数: {total_indexes}")
        
        # 按行数排序显示表
        print(f"\n📋 按数据量排序的表:")
        sorted_tables = sorted(schema_info.items(), key=lambda x: x[1]['row_count'], reverse=True)
        for table_name, table_info in sorted_tables:
            print(f"   {table_name:<25} {table_info['row_count']:>10,} 行")
        
        await conn.close()
        print("\n🎉 sdx schema结构读取完成！")
        
        return schema_info
        
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print("SuperMap sdx Schema 结构读取工具")
    print("=" * 80)
    
    # 显示配置信息
    from app.core.config import settings
    print(f"📋 数据库配置:")
    print(f"   主机: {settings.postgres_host}")
    print(f"   端口: {settings.postgres_port}")
    print(f"   数据库: {settings.postgres_db}")
    print(f"   用户: {settings.postgres_user}")
    print()
    
    # 执行读取
    asyncio.run(read_sdx_schema())
