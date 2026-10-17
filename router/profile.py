from email.policy import HTTP

from models.bank import DbAccount, DbOpenAccount, DbTranscation, DbUser

from database.db import Base, get_db
from sqlalchemy.orm import Session

from uuid import uuid4

from fastapi import FastAPI, Form, File, APIRouter, HTTPException, status, Depends

from router.user import get_current_user


router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/profile")
def profile(
    current_user: DbUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    user = (
        db.query(DbOpenAccount).filter(DbOpenAccount.user_id == current_user.id).first()
    )

    print("username", user.username)
    print("Current_user", current_user.username)

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    detail = db.query(DbAccount).filter(DbAccount.open_id == user.id).first()

    if not detail:
        raise HTTPException(status_code=400, detail="Details not found")

    profile_details = {
        "username": user.username,
        "Balance": detail.balance,
        "Account Number": detail.account_nbr,
        "Account Type": detail.account_type.value,
    }

    return {
        "message": f"Profile details of user is {user.username}",
        "details": profile_details,
    }
