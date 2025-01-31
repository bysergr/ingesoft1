from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.ai.router import ai_router

import os
import uvicorn

app = FastAPI()


app.title = "Naurat Importation Bot API"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router, prefix="/ai", tags=["ai"])


@app.get("/")
def read_root():
    return {"Hello": "Ingesoft Class"}


if __name__ == "__main__":

    port = os.getenv("PORT")

    print(f"[INFO] Port: {port}")

    if not port:
        print("[INFO] Environment variable not found: Port")

        port = 8080

    uvicorn.run(app, host="0.0.0.0", port=int(port))