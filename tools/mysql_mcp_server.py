"""
MySQL MCP Server
通过 stdin/stdout 提供 MySQL 数据库操作能力。
"""

import json
import sys
import traceback
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "bg3_map",
    "charset": "utf8mb4",
}


def query(sql: str) -> list[dict]:
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description:
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                return [dict(zip(cols, r)) for r in rows]
            conn.commit()
            return [{"affected_rows": cur.rowcount}]
    finally:
        conn.close()


TOOLS = [
    {
        "name": "query",
        "description": "执行 MySQL 查询语句 (SELECT/INSERT/UPDATE/DELETE)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "SQL 语句"}
            },
            "required": ["sql"]
        }
    },
    {
        "name": "list_tables",
        "description": "列出数据库中所有表",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "describe_table",
        "description": "查看表结构",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "表名"}
            },
            "required": ["table"]
        }
    },
]


def handle_request(msg: dict) -> dict:
    req_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})

        try:
            if name == "query":
                result = query(args["sql"])
            elif name == "list_tables":
                result = query("SHOW TABLES")
            elif name == "describe_table":
                result = query(f"DESCRIBE `{args['table']}`")
            else:
                raise ValueError(f"Unknown tool: {name}")

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, default=str)}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -1, "message": str(e)}
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}


def main():
    initialize_msg = json.loads(sys.stdin.readline())
    if initialize_msg.get("method") == "initialize":
        resp = {
            "jsonrpc": "2.0",
            "id": initialize_msg["id"],
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "mysql-mcp", "version": "1.0.0"},
                "capabilities": {"tools": {}}
            }
        }
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()

        # notified
        sys.stdin.readline()

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        msg = json.loads(line)
        resp = handle_request(msg)
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
