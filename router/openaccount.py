import secrets

from database.db import get_db
from fastapi import APIRouter, Depends, Form, HTTPException, status
from models.bank import DbAccount, DbOpenAccount, DbUser
from sqlalchemy.orm import Session
from models.bank import AccountStatus, AccountType
from router.user import get_current_user

router = APIRouter(prefix="/open_account", tags=["Open Account"])


@router.post("/open_account")
async def open_account(
    username: str = Form(...),
    address: str = Form(...),
    phone_no: str = Form(...),
    account_type: str = Form(AccountType.saving),
    account_status: str = Form(AccountStatus.active),
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user),
):
    ##it return the query of if existing user exist
    existing__user = (
        db.query(DbOpenAccount).filter(DbOpenAccount.phone_no == phone_no).first()
    )

    if existing__user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already created an account",
        )

    try:
        new_application = DbOpenAccount(
            username=username, phone_no=phone_no, address=address
        )

        db.add(new_application)
        db.flush()

        new_account = DbAccount(
            account_nbr="ACC" + secrets.token_hex(6).upper(),
            account_type=account_type,
            account_status=account_status,
            open_id=new_application.id,
        )

        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        return {
            "message": f" Account of {new_application.username} is successfully created And your account number is{new_account.account_nbr}.."
        }

    except Exception as e:
        db.rollback()
        print("eror", repr(e))
        raise HTTPException(status_code=500, detail="failed while openaccount")
