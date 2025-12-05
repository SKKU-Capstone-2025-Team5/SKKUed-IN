import sys
import os
import importlib
import pkgutil
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# 1. [수정] 불필요한 경로 설정 및 DB 강제 지정 코드 제거
# Docker 환경에서는 /app/app 구조로 마운트되므로 별도의 sys.path 설정 없이도 import가 잘 됩니다.
# 또한, settings.DATABASE_URL을 강제로 바꾸면 도커 볼륨(/data)을 쓰지 않게 되어 데이터가 날아갑니다.
# 따라서 Docker가 주입해준 환경변수(.env)를 그대로 따르도록 해당 코드는 삭제했습니다.

from app.core.config import settings
from app.db.session import SessionLocal

# 2. [유지] models 폴더 내의 모든 파일을 자동으로 찾아서 로딩하기
# (요청하신 대로 이 로직은 유지하여 'Team' 등의 관계 에러를 방지합니다.)
try:
    # app.models 패키지 가져오기
    import app.models
    package_path = os.path.dirname(app.models.__file__)
    
    # models 폴더 안의 모든 .py 파일을 순회하며 import
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        importlib.import_module(f"app.models.{module_name}")
        # print(f"[Model Loaded] app.models.{module_name}")

except Exception as e:
    # 자동 로딩 실패 시, 수동 로딩 시도
    print(f"[Warning] 자동 모델 로딩 실패 ({e}). 수동 로딩을 시도합니다.")
    try:
        from app.models.team import Team
        from app.models.user import User
        # 필요하다면 다른 모델 추가
    except ImportError as ie:
        # 모델 로딩 실패는 치명적이지 않을 수 있으므로 로그만 남기고 진행
        print(f"[Warning] 관계형 모델(Team, User)을 찾을 수 없습니다: {ie}")

# 저장 로직용 Contest 모델 명시적 import
from app.models.contest import Contest

def save_to_db(data_list):
    """
    크롤링 데이터 저장 함수
    도커 볼륨(/data)에 연결된 DB에 안전하게 저장됩니다.
    """
    if not data_list:
        print(">> 저장할 데이터가 없습니다.")
        return

    # 3. [추가] DB 파일이 저장될 '폴더'가 없으면 생성하는 안전장치
    # (sqlite3.OperationalError: unable to open database file 해결용)
    print(f"\n[Debug] 현재 DB 경로: {settings.DATABASE_URL}")
    
    if settings.DATABASE_URL.startswith("sqlite"):
        # URL에서 'sqlite:///' 제거하여 실제 파일 경로 추출 (예: /data/test.db)
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        
        # 슬래시 4개(////)인 경우 앞의 / 하나가 더 남을 수 있어 처리
        if db_path.startswith("/"):
             # 절대 경로인 경우 그대로 둠 (리눅스 환경)
             pass
        
        db_dir = os.path.dirname(db_path)
        
        # 폴더 경로가 존재하고, 실제로 디렉터리가 없다면 생성
        if db_dir and not os.path.exists(db_dir):
            try:
                print(f"[Debug] '{db_dir}' 폴더가 없어서 생성합니다...")
                os.makedirs(db_dir, exist_ok=True)
                print(f"[Debug] '{db_dir}' 폴더 생성 완료.")
            except Exception as e:
                print(f"[Fatal Error] DB 폴더 생성 실패: {e}")

    # 4. 세션 생성 및 데이터 저장
    session: Session = SessionLocal()
    inserted_count = 0
    skipped_count = 0
    
    try:
        for item in data_list:
            # 중복 방지 로직
            existing_contest = session.query(Contest).filter(Contest.ex_link == item["ex_link"]).first()
            if existing_contest:
                skipped_count += 1
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
            session.add(contest)
            inserted_count += 1
            
        session.commit()
        print(f"\n[DB 저장 완료]")
        print(f"- 총 데이터: {len(data_list)}개")
        print(f"- 신규 저장: {inserted_count}개")
        print(f"- 중복 제외: {skipped_count}개")
        
    except IntegrityError as e:
        session.rollback()
        print(f"[Error] 중복 키 에러 발생: {e}")
    except Exception as e:
        session.rollback()
        print(f"[Error] DB 저장 중 오류 발생: {e}")
    finally:
        session.close()