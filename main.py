import os
from typing import List, Optional
from datetime import date
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, engine
from models import (
    Base, User, Client, Service, Product, 
    Appointment, Transaction, SaaSPayment, PlanType, StudioStatus, 
    TransactionType, TransactionStatus
)

# Inicializa o app FastAPI
app = FastAPI(title="NailBoss Pro API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# SCHEMAS (PYDANTIC) - Validação de Entrada/Saída
# ==========================================

class StudioCreate(BaseModel):
    studio_name: str
    email: EmailStr
    phone: str
    password: str
    plan: PlanType

class StudioLogin(BaseModel):
    email: EmailStr
    password: str

class ServiceCreate(BaseModel):
    name: str
    price: float
    estimated_duration_minutes: int = 60

class ClientCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    preference: Optional[str] = None

class AppointmentCreate(BaseModel):
    appointment_date: date
    start_time: str
    end_time: Optional[str] = None
    client_name: str
    client_phone: Optional[str] = None
    service_name: str
    total_amount: float
    pix_deposit_amount: float = 0.0
    is_block: bool = False
    is_from_link: bool = False

class TransactionCreate(BaseModel):
    transaction_date: date
    description: str
    type: TransactionType
    amount: float
    status: TransactionStatus = TransactionStatus.PENDENTE

# ==========================================
# DEPENDÊNCIA DE MULTITENANT (Simulação de Token)
# ==========================================
# Em produção, você substituirá isso por extração de JWT.
# Aqui, exigimos que o Front-end envie o ID do Studio no Header.
def get_tenant(tenant_id: UUID = Header(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == tenant_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Studio não encontrado ou não autorizado.")
    if user.status != StudioStatus.ATIVO:
        raise HTTPException(status_code=403, detail=f"Acesso negado. Status atual: {user.status}")
    return user

# ==========================================
# ROTAS PÚBLICAS & AUTENTICAÇÃO
# ==========================================

@app.get("/", response_class=HTMLResponse)
def root():
    return "<h1>💅 NailBoss API Online</h1><a href='/docs'>Acessar Documentação</a>"

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register_studio(data: StudioCreate, db: Session = Depends(get_db)):
    # Verifica se e-mail já existe
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    
    # Cria o usuário com status AGUARDANDO_APROVACAO
    new_user = User(
        studio_name=data.studio_name,
        email=data.email,
        phone=data.phone,
        password_hash=data.password, # Em prod, use bcrypt aqui!
        plan=data.plan,
        status=StudioStatus.AGUARDANDO_APROVACAO
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Studio cadastrado com sucesso. Aguardando aprovação Master.", "id": new_user.id}

@app.post("/api/auth/login")
def login(data: StudioLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or user.password_hash != data.password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    
    if user.status == StudioStatus.AGUARDANDO_APROVACAO:
        raise HTTPException(status_code=403, detail="Sua conta ainda está em análise.")
    if user.status == StudioStatus.BLOQUEADO:
        raise HTTPException(status_code=403, detail="Conta bloqueada por inadimplência.")
        
    return {
        "tenant_id": user.id,
        "studio_name": user.studio_name,
        "plan": user.plan,
        "role": "studio"
    }

# ==========================================
# ROTAS DO MASTER SAAS (Admin)
# ==========================================

@app.get("/api/admin/studios")
def list_all_studios(db: Session = Depends(get_db)):
    # Em produção, proteja esta rota com senha/token de Admin
    return db.query(User).all()

@app.put("/api/admin/studios/{studio_id}/status")
def change_studio_status(studio_id: UUID, new_status: StudioStatus, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == studio_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Studio não encontrado.")
    
    user.status = new_status
    db.commit()
    return {"message": f"Status alterado para {new_status}"}

# ==========================================
# ROTAS DO STUDIO (Protegidas pelo get_tenant)
# ==========================================

# --- CATÁLOGO DE SERVIÇOS ---
@app.get("/api/services")
def get_services(tenant: User = Depends(get_tenant), db: Session = Depends(get_db)):
    return db.query(Service).filter(Service.user_id == tenant.id).all()

@app.post("/api/services")
def create_service(data: ServiceCreate, tenant: User = Depends(get_tenant), db: Session = Depends(get_db)):
    new_service = Service(**data.model_dump(), user_id=tenant.id)
    db.add(new_service)
    db.commit()
    return {"message": "Serviço cadastrado!"}

# --- CLIENTES ---
@app.get("/api/clients")
def get_clients(tenant: User = Depends(get_tenant), db: Session = Depends(get_db)):
    return db.query(Client).filter(Client.user_id == tenant.id).all()

@app.post("/api/clients")
def create_client(data: ClientCreate, tenant: User = Depends(get_tenant), db: Session = Depends(get_db)):
    new_client = Client(**data.model_dump(), user_id=tenant.id)
    db.add(new_client)
    db.commit()
    return {"message": "Cliente salvo com sucesso!"}

# --- AGENDA ---
@app.get("/api/appointments")
def get_appointments(date_filter: Optional[date] = None, tenant: User = Depends(get_tenant), db: Session = Depends(get_db)):
    query = db.query(Appointment).filter(Appointment.user_id == tenant.id)
    if date_filter:
        query = query.filter(Appointment.appointment_date == date_filter)
    return query.all()

@app.post("/api/appointments")
def create_appointment(data: AppointmentCreate, tenant: User = Depends(get_tenant), db: Session = Depends(get_db)):
    pending = data.total_amount - data.pix_deposit_amount
    new_app = Appointment(
        **data.model_dump(), 
        pending_amount=pending, 
        user_id=tenant.id
    )
    db.add(new_app)
    
    # Integração automática com Financeiro DFC
    if data.pix_deposit_amount > 0 and not data.is_block:
        db.add(Transaction(
            user_id=tenant.id,
            transaction_date=data.appointment_date,
            description=f"Sinal PIX - {data.client_name}",
            type=TransactionType.RECEITA,
            amount=data.pix_deposit_amount,
            status=TransactionStatus.LIQUIDADO
        ))
    if pending > 0 and not data.is_block:
        db.add(Transaction(
            user_id=tenant.id,
            transaction_date=data.appointment_date,
            description=f"Saldo Pendente - {data.client_name}",
            type=TransactionType.RECEITA,
            amount=pending,
            status=TransactionStatus.PENDENTE
        ))
        
    db.commit()
    return {"message": "Agendamento confirmado e DFC atualizado!"}

# --- TESOURARIA (DFC) ---
@app.get("/api/finance")
def get_transactions(tenant: User = Depends(get_tenant), db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.user_id == tenant.id).order_by(Transaction.transaction_date.desc()).all()

@app.post("/api/finance")
def create_transaction(data: TransactionCreate, tenant: User = Depends(get_tenant), db: Session = Depends(get_db)):
    new_trans = Transaction(**data.model_dump(), user_id=tenant.id)
    db.add(new_trans)
    db.commit()
    return {"message": "Lançamento efetuado."}

@app.put("/api/finance/{trans_id}/settle")
def settle_transaction(trans_id: UUID, tenant: User = Depends(get_tenant), db: Session = Depends(get_db)):
    trans = db.query(Transaction).filter(Transaction.id == trans_id, Transaction.user_id == tenant.id).first()
    if not trans:
        raise HTTPException(status_code=404, detail="Transação não encontrada.")
    
    trans.status = TransactionStatus.LIQUIDADO
    db.commit()
    return {"message": "Baixa financeira realizada com sucesso!"}