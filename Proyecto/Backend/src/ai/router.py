from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from src.database import get_db
from src.models import *

from requests import Session
from src.ai.schemas import *

ai_router = APIRouter()

@ai_router.post("/google_login/")
def google_login(user_data: GoogleLogin, db: Session = Depends(get_db)):
    email = user_data.email

    user_record = db.query(Users).filter(Users.email == email).first()
    if not user_record:
        user_record = Users(email=email)
        db.add(user_record)
        db.commit()

    return JSONResponse(
        content={"message": "User logged in successfully"}, status_code=200
    )


@ai_router.get("/bot_conversation/{user_email}")
def get_user_conversation(user_email: str, db: Session = Depends(get_db)):
    user_record = db.query(Users).filter(Users.email == user_email).first()
    if not user_record:
        raise HTTPException(
            status_code=404, detail="No conversation found for this user"
        )

    all_messages = (
        db.query(Messages)
        .filter(Messages.user_id == user_record.id)
        .order_by(Messages.created_at.asc())
        .all()
    )

    conversation_list = []
    for message in all_messages:
        conversation_list.append(message.message)

    return JSONResponse(content={"conversation": conversation_list}, status_code=200)


