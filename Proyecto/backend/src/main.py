"""
Main module for the Naurat Importation Bot API.

This script initializes and runs a FastAPI server with the following features:

- **CORS Middleware:** Configured to allow all origins, credentials, methods, and headers.
- **Routers:**
  - `/ai`: Handles AI-related endpoints (imported from `src.ai.router`).
  - `/`: Root endpoint returning a basic welcome message.
- **Server Execution:**
  - Runs with Uvicorn.
  - Uses the `PORT` environment variable if defined, otherwise defaults to port 8080.

Usage:
    Run the script directly to start the FastAPI server.

Modules:
    - `fastapi.FastAPI`: Main framework for building the API.
    - `fastapi.middleware.cors.CORSMiddleware`: Middleware for handling CORS.
    - `uvicorn`: ASGI server for running FastAPI applications.
    - `os`: Used for retrieving environment variables.

"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.ai.router import ai_router


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
    """
    Root endpoint of the API.

    Returns:
        dict: A welcome message with the key "Hello" and the value "Ingesoft Class".
    """

    return {"Hello": "Ingesoft Class"}


if __name__ == "__main__":

    PORT = os.getenv("PORT")

    print(f"[INFO] Port: {PORT}")

    if not PORT:
        print("[INFO] Environment variable not found: Port")

        PORT = 8080

    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
