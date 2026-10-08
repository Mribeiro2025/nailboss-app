import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega as variáveis do ficheiro .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("A testar a conexão com o Neon.tech...")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("\n✅ CONEXÃO BEM-SUCEDIDA!")
        print(f"Versão do Postgres no Neon: {result.fetchone()[0]}")
except Exception as e:
    print("\n❌ Erro ao conectar:")
    print(e)