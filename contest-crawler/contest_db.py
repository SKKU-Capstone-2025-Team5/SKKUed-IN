import sys
import os

# Add the parent directory of 'app' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'back-end')))

from app.core.config import settings
settings.DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'back-end', 'test.db')}"

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.models.contest import Contest

def save_to_db(data_list):
    """
    크롤링한 데이터(딕셔너리 리스트)를 DB에 저장합니다.
    ex_link가 중복될 경우 INSERT OR IGNORE를 통해 무시합니다.
    """
    if not data_list:
        print("No data to save.")
        return

    db: Session = SessionLocal()
    inserted_count = 0
    try:
        for item in data_list:
            # Check if a contest with the same ex_link already exists
            existing_contest = db.query(Contest).filter(Contest.ex_link == item["ex_link"]).first()
            if existing_contest:
                # Optionally update existing contest if needed, or just skip
                print(f"Contest with link {item['ex_link']} already exists. Skipping.")
                continue

            contest = Contest(
                ex_name=item["ex_name"],
                ex_link=item["ex_link"],
                ex_host=item["ex_host"],
                ex_image=item["ex_image"],
                ex_start=item["ex_start"],
                ex_end=item["ex_end"],
                ex_flag=item["ex_flag"],
            )
            db.add(contest)
            inserted_count += 1
        db.commit()
        print(f"Attempted to save {len(data_list)} items. Successfully inserted {inserted_count} new items into contests table.")
    except IntegrityError as e:
        db.rollback()
        print(f"An IntegrityError occurred (likely duplicate ex_link): {e}")
    except Exception as e:
        db.rollback()
        print(f"An unexpected error occurred while inserting data into contests table: {e}")
    finally:
        db.close()