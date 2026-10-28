
# API básica de livros com FastAPI, SQLAlchemy, SQLite e Redis
# CRUD: Create, Read, Update e Delete

import os
import json
import secrets
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as redis

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session


# ============================================================
# CONFIGURAÇÕES
# ============================================================

load_dotenv()

# Banco de dados SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./livros.db"
)

# Configuração compatível com SQLite
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Credenciais HTTP Basic
USER = os.getenv("USER", "admin")
PASSWORD = os.getenv("PASSWORD", "senha123")

security = HTTPBasic()


# ============================================================
# CONEXÃO REUTILIZÁVEL COM REDIS
# ============================================================

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0,
    decode_responses=True
)

# Tempo de expiração do cache em segundos
CACHE_TTL = 60


# ============================================================
# FUNÇÕES OBRIGATÓRIAS DE CACHE
# ============================================================

async def salvar_livros_redis(
    livros: list,
    chave: str = "livros",
    metadata: Optional[dict] = None
):
    """
    Salva uma lista de livros no Redis com tempo de expiração.
    A metadata permite guardar informações da paginação.
    """

    dados = {
        **(metadata or {}),
        "livros": livros
    }

    await redis_client.setex(
        chave,
        CACHE_TTL,
        json.dumps(dados, ensure_ascii=False)
    )


async def deletar_livros_redis(livros: list):
    """
    Invalida o cache das listagens de livros.
    Deve ser chamada depois de cadastrar, atualizar ou excluir.
    """

    chaves = []

    # Localiza todas as páginas armazenadas no cache
    async for chave in redis_client.scan_iter(
        match="livros:*"
    ):
        chaves.append(chave)

    # Remove também a chave geral, se existir
    chaves.append("livros")

    # Exclui as chaves encontradas
    if chaves:
        await redis_client.delete(*set(chaves))


# ============================================================
# MODELO DO BANCO DE DADOS
# ============================================================

class LivroDB(Base):
    __tablename__ = "Livros"

    id = Column(Integer, primary_key=True, index=True)
    nome_livro = Column(String, index=True)
    autor_livro = Column(String, index=True)
    ano_livro = Column(Integer)


# ============================================================
# MODELO DE VALIDAÇÃO DA API
# ============================================================

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int


# Cria a tabela caso ela ainda não exista
Base.metadata.create_all(bind=engine)


# ============================================================
# CICLO DE VIDA DA APLICAÇÃO
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Confirma que o Redis está acessível ao iniciar
    await redis_client.ping()

    yield

    # Fecha a conexão ao encerrar a aplicação
    await redis_client.aclose()


# ============================================================
# APLICAÇÃO FASTAPI
# ============================================================

app = FastAPI(
    title="API de livros",
    description="API para gerenciar catálogo de livros",
    version="1.0.0",
    contact={
        "name": "Guilherme Muniz",
        "email": "muniz_157@outlook.com"
    },
    lifespan=lifespan
)


# ============================================================
# DEPENDÊNCIA DO BANCO DE DADOS
# ============================================================

def sessao_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# AUTENTICAÇÃO HTTP BASIC
# ============================================================

def autenticar_meu_user(
    credentials: HTTPBasicCredentials = Depends(security)
):
    usuario_correto = secrets.compare_digest(
        credentials.username,
        USER
    )

    senha_correta = secrets.compare_digest(
        credentials.password,
        PASSWORD
    )

    if not (usuario_correto and senha_correta):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )


# ============================================================
# SIMULAÇÃO DE CHAMADAS EXTERNAS ASSÍNCRONAS
# ============================================================

async def chamadas_externas_1():
    await asyncio.sleep(2)
    return "Resultado chamada externa 1"


async def chamadas_externas_2():
    await asyncio.sleep(2)
    return "Resultado chamada externa 2"


async def chamadas_externas_3():
    await asyncio.sleep(2)
    return "Resultado chamada externa 3"


@app.get("/chamadas-externas")
async def chamadas_externas():
    resultados = await asyncio.gather(
        chamadas_externas_1(),
        chamadas_externas_2(),
        chamadas_externas_3()
    )

    return {
        "mensagem": (
            "Todas as chamadas externas foram concluídas "
            "com sucesso!"
        ),
        "resultado": resultados
    }


# ============================================================
# DEBUG DO REDIS
# ============================================================

@app.get("/debug/redis")
async def debug_redis(
    credentials: HTTPBasicCredentials = Depends(
        autenticar_meu_user
    )
):
    resultado = []

    async for chave in redis_client.scan_iter(
        match="livros:*"
    ):
        valor = await redis_client.get(chave)
        ttl = await redis_client.ttl(chave)

        resultado.append({
            "chave": chave,
            "valor": json.loads(valor) if valor else None,
            "ttl": ttl
        })

    return resultado


# ============================================================
# GET - LISTAR LIVROS COM CACHE REDIS
# ============================================================

@app.get("/livros")
async def get_livros(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(
        autenticar_meu_user
    )
):
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Page e limit devem ser maiores que 0"
        )

    # Cada combinação de página e limite possui sua chave
    cache_key = f"livros:page={page}&limit={limit}"

    # 1. Primeiro verifica se os dados estão no Redis
    cached = await redis_client.get(cache_key)

    if cached is not None:
        return json.loads(cached)

    # 2. Se não estiverem no cache, consulta o SQLite
    total_livros = db.query(LivroDB).count()

    livros_db = (
        db.query(LivroDB)
        .order_by(LivroDB.id)
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    # Converte os registros em dicionários serializáveis
    livros = [
        {
            "id": livro.id,
            "nome_livro": livro.nome_livro,
            "autor_livro": livro.autor_livro,
            "ano_livro": livro.ano_livro
        }
        for livro in livros_db
    ]

    # 3. Monta a resposta com a paginação
    metadata = {
        "page": page,
        "limit": limit,
        "total_livros": total_livros
    }

    resposta = {
        **metadata,
        "livros": livros
    }

    # 4. Armazena os dados no Redis por 60 segundos
    await salvar_livros_redis(
        livros=livros,
        chave=cache_key,
        metadata=metadata
    )

    return resposta


# ============================================================
# POST - ADICIONAR LIVRO
# ============================================================

@app.post("/adiciona")
async def post_livros(
    livro: Livro,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(
        autenticar_meu_user
    )
):
    # Verifica se o livro já existe
    livro_existente = (
        db.query(LivroDB)
        .filter(
            LivroDB.nome_livro == livro.nome_livro,
            LivroDB.autor_livro == livro.autor_livro
        )
        .first()
    )

    if livro_existente:
        raise HTTPException(
            status_code=400,
            detail="Esse livro já existe no banco de dados"
        )

    # Cria o registro no banco
    novo_livro = LivroDB(
        nome_livro=livro.nome_livro,
        autor_livro=livro.autor_livro,
        ano_livro=livro.ano_livro
    )

    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    # Invalida as listagens para não devolver dados antigos
    await deletar_livros_redis([novo_livro])

    return {
        "message": "O livro foi criado com sucesso!",
        "id": novo_livro.id
    }


# ============================================================
# PUT - ATUALIZAR LIVRO
# ============================================================

@app.put("/atualiza/{id_livro}")
async def put_livros(
    id_livro: int,
    livro: Livro,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(
        autenticar_meu_user
    )
):
    db_livro = (
        db.query(LivroDB)
        .filter(LivroDB.id == id_livro)
        .first()
    )

    if not db_livro:
        raise HTTPException(
            status_code=404,
            detail="Este livro não foi encontrado"
        )

    # Atualiza os dados originais
    db_livro.nome_livro = livro.nome_livro
    db_livro.autor_livro = livro.autor_livro
    db_livro.ano_livro = livro.ano_livro

    db.commit()
    db.refresh(db_livro)

    # Invalida o cache após a atualização
    await deletar_livros_redis([db_livro])

    return {
        "message": "O livro foi atualizado com sucesso!"
    }


# ============================================================
# DELETE - EXCLUIR LIVRO
# ============================================================

@app.delete("/deletar/{id_livro}")
async def delete_livro(
    id_livro: int,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(
        autenticar_meu_user
    )
):
    db_livro = (
        db.query(LivroDB)
        .filter(LivroDB.id == id_livro)
        .first()
    )

    if not db_livro:
        raise HTTPException(
            status_code=404,
            detail="Este livro não foi encontrado"
        )

    # Exclui o registro do banco
    db.delete(db_livro)
    db.commit()

    # Invalida o cache após a exclusão
    await deletar_livros_redis([db_livro])

    return {
        "message": "Seu livro foi deletado com sucesso!"
    }
