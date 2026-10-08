import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    print("Conectando ao Neon.tech e criando as tabelas do NailBoss...")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("✅ Todas as tabelas foram criadas com sucesso no Neon.tech!")

if __name__ == "__main__":
    init_db()