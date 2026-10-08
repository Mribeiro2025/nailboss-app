import os
import uuid
from decimal import Decimal
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from models import Base, User, BusinessSettings, Client, Service, Product, Appointment, Transaction
from services.financial import calculate_service_settlement, calculate_prolabore_status

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("A variavel DATABASE_URL nao foi configurada no .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="NailBoss API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>NailBoss API - Status</title>
        <style>
            body { font-family: system-ui, sans-serif; background: #fff5f7; color: #5a1a32; text-align: center; padding: 50px; }
            .card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(184,51,106,0.1); display: inline-block; }
            h1 { color: #b8336a; }
            a { color: #b8336a; font-weight: bold; text-decoration: none; border: 2px solid #b8336a; padding: 10px 20px; border-radius: 10px; display: inline-block; margin-top: 20px; }
            a:hover { background: #b8336a; color: white; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>💅 NailBoss API Online</h1>
            <p>Seja a chefe das suas finanças e horários!</p>
            <a href="/docs">Abrir Documentacao da API (Swagger)</a>
        </div>
    </body>
    </html>
    """

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "app": "NailBoss", "version": "1.0.0"}

