# contest_db.py
import sqlite3
import os
from datetime import date

DB_NAME = "../db/contest_info.db"

def init_db():
    """
    데이터베이스와 'contest_info' 테이블을 초기화합니다.
    테이블이 이미 존재하면 아무 작업도 하지 않습니다.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 'contest_info' 테이블 생성
    # ex_link를 UNIQUE로 설정하여 동일한 공고가 중복 저장되는 것을 방지
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contest_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ex_name TEXT NOT NULL,
        ex_link TEXT NOT NULL UNIQUE,
        ex_host TEXT,
        ex_image TEXT,
        ex_start DATE,
        ex_end DATE,
        ex_flag INTEGER
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized and table 'contest_info' is ready.")

def save_to_db(data_list):
    """
    크롤링한 데이터(딕셔너리 리스트)를 DB에 저장합니다.
    ex_link가 중복될 경우 INSERT OR IGNORE를 통해 무시합니다.
    """
    if not data_list:
        print("No data to save.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    insert_query = """
    INSERT OR IGNORE INTO contest_info 
    (ex_name, ex_link, ex_host, ex_image, ex_start, ex_end, ex_flag) 
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    
    # 딕셔너리 리스트를 튜플 리스트로 변환
    data_to_insert = []
    for item in data_list:
        # datetime.date 객체는 SQLite가 이해할 수 있도록 'YYYY-MM-DD' 문자열로 변환
        # (None 값은 None으로 유지)
        start_date_str = item["ex_start"].isoformat() if isinstance(item["ex_start"], date) else None
        end_date_str = item["ex_end"].isoformat() if isinstance(item["ex_end"], date) else None
        
        data_to_insert.append((
            item["ex_name"],
            item["ex_link"],
            item["ex_host"],
            item["ex_image"],
            start_date_str,
            end_date_str,
            item["ex_flag"]
        ))
    
    # executemany를 사용하여 여러 데이터를 한 번에 효율적으로 삽입
    cursor.executemany(insert_query, data_to_insert)
    
    # cursor.rowcount는 마지막 실행으로 인해 '실제로' 영향을 받은 행의 수
    inserted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"Attempted to save {len(data_list)} items. Successfully inserted {inserted_count} new items.")