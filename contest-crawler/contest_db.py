# contest_db.py
import sqlite3
import os
from datetime import date

DB_NAME = "../back-end/test.db"

TABLE_NAME = "contests"

def save_to_db(data_list):
    """
    크롤링한 데이터(딕셔너리 리스트)를 DB에 저장합니다.
    ex_link가 중복될 경우 INSERT OR IGNORE를 통해 무시합니다.
    """
    if not data_list:
        print("No data to save.")
        return
    
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        print("Please run the FastAPI server once to initialize the database.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    insert_query = f"""
    INSERT OR IGNORE INTO {TABLE_NAME} 
    (ex_name, ex_link, ex_host, ex_image, ex_start, ex_end, ex_flag) 
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    
    data_to_insert = []
    for item in data_list:
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
    
    try:
        cursor.executemany(insert_query, data_to_insert)
        inserted_count = cursor.rowcount
        conn.commit()
        print(f"Attempted to save {len(data_list)} items. Successfully inserted {inserted_count} new items into {TABLE_NAME}.")
    except sqlite3.Error as e:
        print(f"An error occurred while inserting data into {TABLE_NAME}: {e}")
    finally:
        conn.close()