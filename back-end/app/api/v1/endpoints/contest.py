from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app import schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Contest)
def create_contest(
    *, 
    db: Session = Depends(deps.get_db),
    contest_in: schemas.ContestCreate
):
    contest = crud.crud_contest.create_contest(db=db, contest=contest_in)
    return contest

@router.get("/", response_model=List[schemas.Contest])
def read_contests(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    contests = crud.crud_contest.get_contests(db, skip=skip, limit=limit)
    return contests

@router.get("/{contest_id}", response_model=schemas.Contest)
def read_contest(
    *, 
    db: Session = Depends(deps.get_db),
    contest_id: int
):
    contest = crud.crud_contest.get_contest(db=db, contest_id=contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return contest

@router.put("/{contest_id}", response_model=schemas.Contest)
def update_contest(
    *, 
    db: Session = Depends(deps.get_db),
    contest_id: int,
    contest_in: schemas.ContestUpdate
):
    contest = crud.crud_contest.get_contest(db=db, contest_id=contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    contest = crud.crud_contest.update_contest(db=db, contest_id=contest_id, contest=contest_in)
    return contest

@router.delete("/{contest_id}", response_model=schemas.Contest)
def delete_contest(
    *, 
    db: Session = Depends(deps.get_db),
    contest_id: int
):
    contest = crud.crud_contest.get_contest(db=db, contest_id=contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    contest = crud.crud_contest.delete_contest(db=db, contest_id=contest_id)
    return contest