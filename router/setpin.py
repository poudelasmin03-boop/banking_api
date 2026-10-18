from models.bank import (
    DbAccount,
    DbOpenAccount,
    DbTranscation,
    DbUser,
    DbTranscationPin,
)

from database.db import Base, get_db
from sqlalchemy.orm import Session

from uuid import uuid4

from fastapi import FastAPI, Form, File, APIRouter, HTTPException, status, Depends

from router.user import get_current_user

from passlib.context import CryptContext


router = APIRouter(prefix="/pin", tags=["Pin"])


pwdContext = CryptContext(schemes=["argon2"], deprecated="auto")


class Hash:
    def Hash_pin(pin: str):
        return pwdContext.hash(pin)

    def verify(hashed_pin: str, plain_pin: str):
        return pwdContext.verify(plain_pin, hashed_pin)


@router.post("/setpin")
def setPin(
    pin: str = Form(...),
    confirm_pin: str = Form(...),
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user),
):
    ###Current_user
    user = (
        db.query(DbOpenAccount).filter(DbOpenAccount.user_id == current_user.id).first()
    )

    print("username", user.username)
    print("Current_user", current_user.username)

    if len(pin) != 4:
        raise HTTPException(
            status_code=400, detail="Transcation Pin must have 4 character"
        )

    if pin != confirm_pin:
        raise HTTPException(status_code=400, detail="Both Pin doesn't match.")

    set_pin = DbTranscationPin(pin=Hash.Hash_pin(pin), account_id=user.id)
    db.add(set_pin)
    db.commit()
    db.refresh(set_pin)

    return {"message": f"Pin number of {user.username} is set successfully"}


### Update the existing pin code
@router.put("/update_pin")
def update_pin(
    pin: str = Form(...),
    new_pin: str = Form(...),
    confirm: str = Form(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):

    user = user = (
        db.query(DbOpenAccount).filter(DbOpenAccount.user_id == current_user.id).first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found..")
    print("username", user.username)
    print("Current_user", current_user.username)

    check_pin = (
        db.query(DbTranscationPin)
        .filter(DbTranscationPin.account_id == user.id)
        .first()
    )

    if not check_pin:
        raise HTTPException(status_code=400, detail="Pin not found")

    hased_new_pin = Hash.Hash_pin(new_pin)

    if not Hash.verify(check_pin.pin, pin):
        raise HTTPException(status_code=400, detail="Incorrect previous pin")

    if Hash.verify(check_pin.pin, new_pin):
        raise HTTPException(
            status_code=400, detail="Current pin  cann't match to the perivous pin"
        )
    if new_pin != confirm:
        raise HTTPException(
            status_code=400, detail="new pin and confirm pin not matching.."
        )

    try:
        check_pin.pin = hased_new_pin
        db.commit()
        return {"message": "Transcation pin is update successfully.."}

    except Exception as e:
        print("Error", repr(e))
        raise HTTPException(status_code=400, detail="Error occur while updated the pin")
