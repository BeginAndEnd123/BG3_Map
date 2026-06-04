"""
数据库 ER 图生成器

连接 MySQL 读取表结构和外键关系，输出 Mermaid ER 图代码。
可通过 Navicat / DBeaver / GitHub Markdown 渲染。

用法:
    python tools/er_generator.py                          # 输出 Mermaid 代码到终端
    python tools/er_generator.py --output er.md           # 输出到文件
    python tools/er_generator.py --format plantuml         # 输出 PlantUML 格式
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from dotenv import load_dotenv
load_dotenv()

import pymysql

DB_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/bg3_map")


def parse_url(url: str) -> dict:
    prefix = url.split("://", 1)[1] if "://" in url else url
    auth_host, _, db = prefix.partition("/")
    user_pass, _, host_port = auth_host.partition("@")
    user, _, passwd = user_pass.partition(":")
    host, _, port = host_port.partition(":")
    return {
        "host": host,
        "port": int(port) if port else 3306,
        "user": user,
        "password": passwd,
        "database": db,
    }


def get_schema(config: dict) -> dict:
    conn = pymysql.connect(**config, charset="utf8mb4")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY,
               COLUMN_COMMENT, ORDINAL_POSITION
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME != 'alembic_version'
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """, (config["database"],))
    tables = {}
    for row in cursor.fetchall():
        table, col, ctype, nullable, key, comment, pos = row
        if table not in tables:
            tables[table] = []
        tables[table].append({
            "name": col, "type": ctype, "nullable": nullable,
            "key": key, "comment": comment or "",
        })

    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
    """, (config["database"],))
    foreign_keys = []
    for row in cursor.fetchall():
        foreign_keys.append({
            "table": row[0], "column": row[1],
            "ref_table": row[2], "ref_column": row[3],
        })

    cursor.close()
    conn.close()
    return {"tables": tables, "foreign_keys": foreign_keys}


def render_mermaid(schema: dict) -> str:
    lines = ["```mermaid", "erDiagram"]
    rels = set()

    for table_name, cols in schema["tables"].items():
        lines.append(f"  {table_name} {{")
        for col in cols:
            col_type = col["type"].split("(")[0]
            pk = "PK" if col["key"] == "PRI" else ""
            entry = f"    {col_type} {col['name']} {pk}".rstrip()
            lines.append(entry)
        lines.append("  }")

    for fk in schema["foreign_keys"]:
        rel = (fk["table"], fk["ref_table"])
        if rel not in rels:
            rels.add(rel)
            lines.append(f"  {fk['ref_table']} ||--o{{ {fk['table']} : has")

    lines.append("```")
    return "\n".join(lines)


def render_plantuml(schema: dict) -> str:
    lines = ["@startuml", "", "!define table(x) class x << (T,#FFAAAA) >>"]
    for table_name in schema["tables"]:
        lines.append(f"class {table_name} {{")
        for col in schema["tables"][table_name]:
            lines.append(f"    {col['type']} {col['name']}")
        lines.append("}")
    for fk in schema["foreign_keys"]:
        lines.append(f"{fk['table']} \"1\" -- \"*\" {fk['ref_table']}")
    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="数据库 ER 图生成器")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--format", "-f", choices=["mermaid", "plantuml"],
                        default="mermaid", help="输出格式 (默认: mermaid)")
    parser.add_argument("--url", help="数据库连接 URL (默认从 .env 读取)")
    args = parser.parse_args()

    url = args.url or DB_URL
    config = parse_url(url)
    schema = get_schema(config)

    if args.format == "plantuml":
        result = render_plantuml(schema)
    else:
        result = render_mermaid(schema)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"已写出: {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
