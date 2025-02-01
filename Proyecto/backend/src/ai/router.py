'''
AI Routes Module

This module defines API routes for AI-related operations, including user authentication,
conversation retrieval, and Excel file generation.

Routes:
- /google_login/: Handles user login via Google authentication and database check.
- /bot_conversation/{user_email}: Retrieves the conversation history of a user.
- /get_excel/: Generates and returns an Excel file for the user.

Dependencies:
- Database session (db).
- GoogleLogin schema for user authentication.
'''

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from src.ai.schemas import GoogleLogin


from src.database import get_db
from src.models import Users, Messages
from src.ai.crud import generate_excel



ai_router = APIRouter()


@ai_router.post("/google_login/")
def google_login(user_data: GoogleLogin, db: Session = Depends(get_db)):

    '''
    Handles user login via Google authentication.

    This endpoint receives user data from Google Login, checks if the user
    already exists in the database, and if not, creates a new user record.

    Args:
        user_data (GoogleLogin): The user data containing the email obtained from Google Login.
        db (Session, optional): The database session dependency.

    Returns:
        JSONResponse: A response indicating that the user has successfully logged in.

    Status Codes:
        - 200: User logged in successfully.
    '''

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

    '''
    Retrieve the conversation history for a given user.

    This endpoint retrieves all messages exchanged with a user, ordered by their creation date.

    Args:
        user_email (str): The email of the user whose conversation is being fetched.
        db (Session, optional): The database session dependency.

    Returns:
        JSONResponse: A JSON response containing the user's conversation history.

    Status Codes:
        - 200: Successfully retrieved the conversation.
        - 404: User not found or no conversation available.
    '''

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


@ai_router.get("/get_excel/")
def get_excel(user_email: str, db: Session = Depends(get_db)):
    """
    Generate and return an Excel file for the given user.

    This endpoint generates an Excel file based on the user's data and returns it.

    Args:
        user_email (str): The email of the user for whom the Excel file is generated.
        db (Session, optional): The database session dependency.

    Returns:
        StreamingResponse: A streaming response containing the generated Excel file.

    Status Codes:
        - 200: Successfully generated and returned the Excel file.
        - 404: User not found in the database.
    """

    user = db.query(Users).filter(Users.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    buffer = generate_excel(user_email=user_email, db=db)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=products.xlsx"}
    )
