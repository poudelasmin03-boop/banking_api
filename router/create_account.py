from models.bank import DbAccount, DbOpenAccount

from database.db import Base, get_db
from sqlalchemy.orm import Session


from fastapi import FastAPI, Form, File, APIRouter, HTTPException, status, Depends


router = APIRouter(prefix="/create_account", tags=["Create Account"])

import random


@router.post("/create_account")
def create_account(
    account_nbr: str = Form(...),
    account_type: str = Form(...),
    balance: str = Form(...),
    account_status: str = Form(...),
    open_id: int = Form(...),
    db: Session = Depends((get_db)),
):
    account_number = random.randint(10000, 99999)

    create_account = DbAccount(
        account_nbr=account_number,
        account_type=account_type,
        balance=balance,
        account_status=account_status,
        open_id=open_id,
    )

    db.add(create_account)
    db.commit()
    db.refresh(create_account)

    return {"message": f"accountbr is {account_nbr}"}
