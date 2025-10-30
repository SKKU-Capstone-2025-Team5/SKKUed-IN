from sqlalchemy.orm import Session
from app.models.contest import Contest
from app.schemas.contest import ContestCreate, ContestUpdate

def get_contest(db: Session, contest_id: int):
    return db.query(Contest).filter(Contest.id == contest_id).first()

def get_contests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Contest).offset(skip).limit(limit).all()

def create_contest(db: Session, contest: ContestCreate):
    contest_data = contest.dict()
    if contest.ex_link:
        contest_data['ex_link'] = str(contest.ex_link)
    if contest.ex_image:
        contest_data['ex_image'] = str(contest.ex_image)
    db_contest = Contest(**contest_data)
    db.add(db_contest)
    db.commit()
    db.refresh(db_contest)
    return db_contest

def update_contest(db: Session, contest_id: int, contest: ContestUpdate):
    db_contest = get_contest(db, contest_id)
    if db_contest:
        update_data = contest.dict(exclude_unset=True)
        if 'ex_link' in update_data and update_data['ex_link']:
            update_data['ex_link'] = str(update_data['ex_link'])
        if 'ex_image' in update_data and update_data['ex_image']:
            update_data['ex_image'] = str(update_data['ex_image'])
        for key, value in update_data.items():
            setattr(db_contest, key, value)
        db.commit()
        db.refresh(db_contest)
    return db_contest

def delete_contest(db: Session, contest_id: int):
    db_contest = get_contest(db, contest_id)
    if db_contest:
        db.delete(db_contest)
        db.commit()
    return db_contest