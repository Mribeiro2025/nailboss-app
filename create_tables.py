import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def init_db():
    print("⏳ Conectando ao Neon.tech e criando as tabelas do NailBoss...")
    engine = create_engine(DATABASE_URL)
    
    # Cria todas as tabelas baseadas no models.py
    Base.metadata.create_all(bind=engine)
    
    print("✅ Todas as tabelas foram criadas com sucesso no Neon.tech!")

if __name__ == "__main__":
    init_db()