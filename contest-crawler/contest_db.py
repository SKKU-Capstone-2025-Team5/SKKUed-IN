import sys
import os
import importlib
import pkgutil

# 1. 백엔드 경로 설정 (app 모듈을 찾기 위함)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'back-end'))
sys.path.append(BACKEND_DIR)

# 2. DB 경로 강제 수정 (skkuedin.db 사용)
from app.core.config import settings
settings.DATABASE_URL = f"sqlite:///{os.path.join(BACKEND_DIR, 'skkuedin.db')}"

# 3. [핵심] models 폴더 내의 모든 파일을 자동으로 찾아서 로딩하기
# 이렇게 하면 파일이 추가되어도 코드를 고칠 필요가 없습니다.
try:
    # app/models 패키지의 경로를 찾습니다.
    import app.models
    package_path = os.path.dirname(app.models.__file__)
    
    # models 폴더 안의 모든 .py 파일을 순회하며 import 합니다.
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        # "app.models.user", "app.models.team" 등으로 불러옵니다.
        importlib.import_module(f"app.models.{module_name}")
        # print(f"[Model Loaded] app.models.{module_name}")

except Exception as e:
    # 자동 로딩 실패 시, 수동으로라도 핵심 모델을 다 부릅니다.
    print(f"[Warning] 자동 모델 로딩 실패 ({e}). 수동 로딩을 시도합니다.")
    try:
        from app.models.skill import Skill
        from app.models.interest import Interest
        from app.models.user import User
        from app.models.team import Team
        from app.models.contest import Contest
        # 채팅 관련 (파일명 추정)
        try: from app.models.conversation import Conversation
        except: pass
        try: from app.models.conversation_participant import ConversationParticipant
        except: pass
        try: from app.models.message import Message
        except: pass
        try: from app.models.notification import Notification
        except: pass
    except ImportError as ie:
        print(f"[Fatal Error] 모델을 불러올 수 없습니다: {ie}")
        sys.exit(1)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
# Contest 모델 명시적 import (저장 로직용)
from app.models.contest import Contest

def save_to_db(data_list):
    """
    크롤링 데이터 저장 함수
    """
    if not data_list:
        print("저장할 데이터가 없습니다.")
        return

    db: Session = SessionLocal()
    inserted_count = 0
    
    try:
        for item in data_list:
            # 중복 방지 로직
            existing_contest = db.query(Contest).filter(Contest.ex_link == item["ex_link"]).first()
            if existing_contest:
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
        print(f"총 {len(data_list)}개 중 {inserted_count}개의 새로운 공모전을 저장했습니다.")
        
    except IntegrityError as e:
        db.rollback()
        print(f"[중복 에러] {e}")
    except Exception as e:
        db.rollback()
        print(f"[DB 저장 실패] {e}")
    finally:
        db.close()