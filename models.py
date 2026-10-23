import uuid
import enum
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, Date, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class PlanType(str, enum.Enum):
    STARTER = "STARTER"
    PRO = "PRO"
    VIP = "VIP"

class StudioStatus(str, enum.Enum):
    ATIVO = "ATIVO"
    AGUARDANDO_APROVACAO = "AGUARDANDO_APROVACAO"
    BLOQUEADO = "BLOQUEADO"

class TransactionType(str, enum.Enum):
    RECEITA = "receita"
    DESPESA = "despesa"

class TransactionStatus(str, enum.Enum):
    PENDENTE = "PENDENTE"
    LIQUIDADO = "LIQUIDADO"

# 1. Usuárias (Manicures / Nail Designers / Studios)
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    studio_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    plan = Column(Enum(PlanType), default=PlanType.STARTER, nullable=False)
    status = Column(Enum(StudioStatus), default=StudioStatus.AGUARDANDO_APROVACAO, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 2. Configurações de Regra de Negócio & Salão
class BusinessSettings(Base):
    __tablename__ = "business_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    salon_commission_rate = Column(Numeric(5, 2), default=30.00)
    commission_base_type = Column(String(20), default="GROSS")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# 3. Clientes (CRM)
class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=True)
    client_since = Column(Date, server_default=func.current_date())
    preference = Column(String(150), nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 4. Catálogo de Serviços
class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    estimated_duration_minutes = Column(Integer, default=60)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 5. Insumos / Estoque (Cálculo de CMV)
class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)
    total_cost = Column(Numeric(10, 2), nullable=False) 
    current_stock = Column(Integer, nullable=False, default=0)
    yield_per_unit = Column(Integer, default=1) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 6. Agendamentos da Agenda (Slots e Bloqueios)
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    appointment_date = Column(Date, nullable=False)
    start_time = Column(String(5), nullable=False) 
    end_time = Column(String(5), nullable=True) 
    
    client_name = Column(String(120), nullable=False)
    client_phone = Column(String(20), nullable=True)
    service_name = Column(String(100), nullable=False)
    
    total_amount = Column(Numeric(10, 2), default=0.00)
    pix_deposit_amount = Column(Numeric(10, 2), default=0.00) 
    pending_amount = Column(Numeric(10, 2), default=0.00)
    
    is_settled = Column(Boolean, default=False) 
    is_block = Column(Boolean, default=False) 
    is_from_link = Column(Boolean, default=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 7. Transações Financeiras (DFC)
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    
    transaction_date = Column(Date, nullable=False)
    description = Column(String(200), nullable=False)
    
    type = Column(Enum(TransactionType), nullable=False) 
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDENTE, nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 8. Pagamentos Master SaaS
class SaaSPayment(Base):
    __tablename__ = "saas_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    payment_date = Column(Date, nullable=False)
    plan = Column(Enum(PlanType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDENTE, nullable=False)