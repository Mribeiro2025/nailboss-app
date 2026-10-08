import uuid
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# 1. Usuárias (Manicures / Nail Designers)
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 2. Configurações de Regra de Negócio & Salão
class BusinessSettings(Base):
    __tablename__ = "business_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    salon_commission_rate = Column(Numeric(5, 2), default=30.00)  # Ex: 30%
    commission_base_type = Column(String(20), default="GROSS")     # 'GROSS' (Bruto) ou 'NET' (Líquido descontando CMV)
    chair_rent_fee = Column(Numeric(10, 2), default=0.00)        # Aluguel fixo de cadeira
    chair_rent_period = Column(String(10), default="MONTHLY")   # 'WEEKLY' ou 'MONTHLY'
    monthly_revenue_goal = Column(Numeric(10, 2), default=0.00)  # Meta de faturamento
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# 3. Clientes (CRM)
class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    favorite_shape = Column(String(50), nullable=True) # Formato de unha favorito
    allergies = Column(Text, nullable=True)             # Alergias
    notes = Column(Text, nullable=True)
    last_appointment_at = Column(DateTime(timezone=True), nullable=True)
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
    purchase_price = Column(Numeric(10, 2), nullable=False)
    current_stock = Column(Integer, nullable=False, default=0)
    min_stock_alert = Column(Integer, default=5)
    yield_per_unit = Column(Integer, default=1) # Rende x atendimentos por unidade
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 6. Agendamentos
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id", ondelete="RESTRICT"), nullable=False)
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="SCHEDULED") # SCHEDULED, CONFIRMED, COMPLETED, CANCELED, NO_SHOW
    pix_deposit_amount = Column(Numeric(10, 2), default=0.00) # Valor do Sinal
    pix_deposit_paid = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 7. Transações Financeiras (Conciliação Completa)
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    
    description = Column(String(200), nullable=False)
    type = Column(String(10), nullable=False)       # INCOME ou EXPENSE
    category = Column(String(50), nullable=False)    # SERVICE, PRODUCT_SALE, SALON_COMMISSION, CHAIR_RENT, PRO_LABORE, OPERATIONAL_EXPENSE
    
    gross_amount = Column(Numeric(10, 2), nullable=False) # Valor total cobrado
    cmv_cost = Column(Numeric(10, 2), default=0.00)        # Custo dos Insumos
    salon_fee = Column(Numeric(10, 2), default=0.00)       # Comissão devida ao Salão
    net_amount = Column(Numeric(10, 2), nullable=False)    # Lucro Líquido final da Manicure
    
    payment_method = Column(String(20), default="PIX")     # PIX, CREDIT_CARD, DEBIT_CARD, CASH
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())