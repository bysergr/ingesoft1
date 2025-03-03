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


import uuid
import codecs
import os
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from src.ai.schemas import GoogleLogin, AskAgent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph



from src.database import get_db
from src.models import Users, Messages
from src.ai.crud import *
from src.ai.constants.en import *
from src.ai.constants.es import *
from src.ai.utils.detect_language import detect_language


ai_router = APIRouter()


@ai_router.post("/google-login/")
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


@ai_router.post("/importation-bot/")
async def ask_agent(user_prompt: AskAgent, db: Session = Depends(get_db)):


    """
    Ask the AI agent a question or provide a prompt.

    This endpoint receives a user prompt, detects the language of the input text,

    and interacts with the AI agent to generate a response.

    Args:
        user_prompt (AskAgent): The user's prompt containing the input message or question.
        db (Session, optional): The database session dependency.

    Returns:

        JSONResponse: A JSON response containing the AI agent's response.

    Status Codes:

        - 200: Successfully received and processed the user prompt.

        - 400: Error occurred while processing the user prompt.

    """

    try:
        prompt = codecs.decode(user_prompt.prompt, "unicode_escape")
        language = detect_language(prompt)

        agent_objective = (
            "Agent's objective:" if language == "en" else "Objetivo del agente:"
        )
        agent_context = (
            "Agent's context:" if language == "en" else "Contexto del agente:"
        )
        agent_task = "Agent's task:" if language == "en" else "Tarea del agente:"
        agent_output = "Agent's output:" if language == "en" else "Salida del agente:"

        initial_context = (
            f"{EN_NAURAT_AGENT_ROLE if language == 'en' else NAURAT_AGENT_ROLE}\n\n"
            f"{agent_objective}\n{EN_NAURAT_AGENT_GOAL if language == 'en' else NAURAT_AGENT_GOAL}\n\n"
            f"{agent_context}\n{EN_NAURAT_AGENT_BACKSTORY if language == 'en' else NAURAT_AGENT_BACKSTORY}"
            f"{agent_task}\n{EN_NAURAT_TASK_DESCRIPTION if language == 'en' else NAURAT_TASK_DESCRIPTION}"
            f"{agent_output}\n{EN_NAURAT_TASK_EXPECTED_OUTPUT if language == 'en' else NAURAT_TASK_EXPECTED_OUTPUT} "
        )

       
        workflow = StateGraph(state_schema=MessagesState)
        model = ChatOpenAI(
            model="chatgpt-4o-latest",
            temperature=1,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

       
        def call_model(state: MessagesState):
            response = model.invoke(state["messages"])
            return {"messages": response}

        workflow.add_edge(START, "model")
        workflow.add_node("model", call_model)

        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)

        thread_id = uuid.uuid4()

        if user_prompt.user_email:
            user = db.query(Users).filter(Users.email == user_prompt.user_email).first()
        else:
            user = (
                db.query(Users).filter(Users.private_id == user_prompt.user_id).first()
            )

        if not user:
            if user_prompt.user_id:
                user = Users(private_id=user_prompt.user_id)
                db.add(user)
                db.commit()

        all_messages = (
            db.query(Messages)
            .filter(Messages.user_id == user.id)
            .order_by(Messages.created_at.asc())
            .all()
        )

        conversation_list = []
        for message in all_messages:
            conversation_list.append(message.message)

        conversation_history = "\n".join(
            [
                f"{msg['owner'].capitalize()}: {msg['message']}"
                for msg in conversation_list
            ]
        )

        input_message = HumanMessage(
            content=f"{initial_context}\n\n{conversation_history}\nHuman: {prompt}\nAi:"
        )

        config = {"configurable": {"thread_id": thread_id}}
        result_messages = []

        for event in app.stream(
            {"messages": [SystemMessage(content=initial_context), input_message]},
            config,
            stream_mode="values",
        ):
            result_messages.append(event["messages"][-1].content)

        response = result_messages[-1]

        noms_in_response = re.findall(r"NOM-\d{3}-[A-Z]+-\d{4}", response)

        answer_product_es = re.search(r"Información\s+de\s+importación\s+para", response)

        answer_product_en = re.search(r"Import\s+information\s+for", response)

        if answer_product_es or answer_product_en:

            noms_result = re.findall(r"NOM-\d{3}-SCFI-\d{4}\s+\(.*?\)", response, re.IGNORECASE)


            cofepris_result = "Aplica" if "COFEPRIS" in response else "No Aplica"


            save_data_into_db( user_email=user_prompt.user_email,data=get_data(response, noms_result if noms_result else "", cofepris_result), db=db)

        new_human_message = Messages(
            user_id=user.id,
            message={"owner": "human", "message": user_prompt.prompt, "lang": language},
        )
        db.add(new_human_message)

        new_ai_message = Messages(
            user_id=user.id,
            message={
                "owner": "ai",
                "message": response,
                "lang": language,
                "noms": noms_in_response,
            },
        )
        db.add(new_ai_message)
        db.commit()

        return JSONResponse(
            content={"message": response, "noms": noms_in_response, "lang": language},
            status_code=200,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
