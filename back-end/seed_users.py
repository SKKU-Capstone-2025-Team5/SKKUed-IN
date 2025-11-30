from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.base import create_tables  
from app.models.user import User
from app.core.security import get_password_hash

create_tables()   # <- 추가: 모델 로드 + 테이블 생성

def create_user(db: Session, email: str, password: str, full_name: str):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"[SKIP] {email} 이미 존재함.")
        return existing
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"[OK] {email} 생성됨.")
    return user

def run():
    print("=== 시드 유저 생성 시작 ===")
    db = SessionLocal()
    for i in range(1, 11):
        email = f"seed{i:03d}@skku.edu"
        full_name = f"Seed User {i:03d}"
        password = "password"
        create_user(db, email, password, full_name)
    db.close()
    print("=== 시드 유저 생성 완료 ===")

if __name__ == "__main__":
    run()
