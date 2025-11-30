# patch_schema.py
# 기존 DB에 누락된 컬럼(TeamMember.status, OpenPosition.filled_count)을 안전하게 추가
from sqlalchemy import inspect, text
from app.db.session import engine

def add_column_if_missing(table: str, column: str, ddl_sqlite: str, ddl_pg: str):
    insp = inspect(engine)
    cols = {c["name"] for c in insp.get_columns(table)}
    if column in cols:
        print(f"[SKIP] {table}.{column} 이미 존재")
        return

    dialect = engine.dialect.name  # 'sqlite' | 'postgresql'
    sql = ddl_sqlite if dialect == "sqlite" else ddl_pg
    print(f"[APPLY] {table}.{column} 추가 ({dialect}) -> {sql}")
    with engine.begin() as conn:
        conn.execute(text(sql))
    print(f"[OK]    {table}.{column} 추가 완료")

def main():
    # 1) team_members.status
    add_column_if_missing(
        table="team_members",
        column="status",
        ddl_sqlite="ALTER TABLE team_members ADD COLUMN status TEXT NOT NULL DEFAULT 'accepted';",
        ddl_pg   ="ALTER TABLE team_members ADD COLUMN status VARCHAR(32) NOT NULL DEFAULT 'accepted';",
    )

    # 2) open_positions.filled_count
    add_column_if_missing(
        table="open_positions",
        column="filled_count",
        ddl_sqlite="ALTER TABLE open_positions ADD COLUMN filled_count INTEGER NOT NULL DEFAULT 0;",
        ddl_pg   ="ALTER TABLE open_positions ADD COLUMN filled_count INTEGER NOT NULL DEFAULT 0;",
    )

if __name__ == "__main__":
    main()
