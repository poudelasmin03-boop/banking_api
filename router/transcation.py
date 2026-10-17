from email.policy import HTTP

from models.bank import DbAccount, DbOpenAccount, DbTranscation, DbUser

from database.db import Base, get_db
from sqlalchemy.orm import Session

from uuid import uuid4

from fastapi import FastAPI, Form, File, APIRouter, HTTPException, status, Depends

from router.user import get_current_user

router = APIRouter(prefix="/transaction", tags=["Transcation"])


@router.post("/transcatiion")
def Transcation_money(
    amount: float = Form(...),
    sender: DbUser = Depends(get_current_user),
    account_nbr: str = Form(...),
    db: Session = Depends(get_db),
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater then 0")

    ## Checking receiver account nbr exist or not
    receiver_account_nbr = (
        db.query(DbAccount).filter(DbAccount.account_nbr == account_nbr).first()
    )

    if not receiver_account_nbr:
        raise HTTPException(status_code=400, detail="Invalid Account nbr")

    ### Checking sender
    sender_account = (
        db.query(DbAccount)
        .join(DbOpenAccount)
        .filter(DbOpenAccount.username == sender.username)
        .first()
    )
    if not sender_account:
        raise HTTPException(status_code=400, detail="Invalid sendername ")

    sender_name = sender_account.open_account

    if not sender_name:
        raise HTTPException(status_code=404, detail="Sender details not found")

    if sender_account.id == receiver_account_nbr.id:
        raise HTTPException(
            status_code=400, detail="Cannot sent the amount ti same user"
        )

    if sender_account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        receiver_account_nbr.balance += amount
        sender_account.balance -= amount

        new_transcation = DbTranscation(
            sender=sender_account.id,
            transcation=str(uuid4()),
            receiver=receiver_account_nbr.id,
            amount=amount,
        )

        db.add(new_transcation)
        db.commit()
        db.refresh(new_transcation)

        return {
            "message": f"{amount} is successfully transfer",
            "sender": sender_name.username,
            "receiver": receiver_account_nbr.open_account.username,
        }

    except Exception as e:
        db.rollback()
        print("Errror", repr(e))
        raise HTTPException(status_code=403, detail="Error occur during Transcation")


from sqlalchemy import or_


###  Transcation details of request.user
@router.get("/transcation_details")
def Transcation_history(
    current_user: DbUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    user = (
        db.query(DbOpenAccount)
        .filter(DbOpenAccount.username == current_user.username)
        .first()
    )
    print("current_user", current_user.username)
    print("User is", user.username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found..")

    history = (
        db.query(DbTranscation)
        .filter((DbTranscation.sender == user.id) | (DbTranscation.receiver == user.id))
        .order_by(DbTranscation.id.desc())
        .all()
    )

    if not history:
        raise HTTPException(status_code=404, detail="No History found")

    details = []

    for i in history:
        details.append(
            {
                "messsage": f"Here the Transcation history of :{current_user.username}  ",
                "id": i.id,
                "sender_name": i.sender_account.open_account.username,
                "receiver_name": i.receiver_account.open_account.username,
                "transcation_id": i.transcation,
                "amount": i.amount,
            }
        )

    return {"details": details}
