# API basica de livros

# GET,POST, PUT, DELETE

 
#POST - add novos livros
#GET - Buscar dados livros
#PUT - Atualizar info dos livros
#DELETE - deletar info dos livros

#CRUD - 
# Create 
# Read 
# Uptade 
# Delete

#Vamos acessar nosso end-point
#vamos acessar os PATHS do nosso ENDPOINT

#PATHS ou rotas - caminhos que vamos acessar para cada metodo
#Querry strings - parametros que passamos na URL

#documentacao swagger -> Documentar os endpoints da nossa aplicacao (da nossa API)

# Aceesa minha documetacao swagger nesse endpoint -> ........

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets

#Criar banco de dados dentro do python

from sqlalchemy import  create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


DATABASE_URL = "sqlite:///./livros.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#_______________________________________________________________________________
app = FastAPI(
    title="API de livros",
    description="API para gerenciar catalogo de livros",
    version="1.0.0",
    contact={
        "name":"Guilherme Muniz",
        "email":"muniz_157@outlook.com"
    }
)

USER = "admin"
PASSWORD = "admin"


security = HTTPBasic()

dicionario_livros = {}

#Criar nossa table e adcionar nossas colunas com os parametros necessarios

class LivroDB(Base):
    __tablename__ = "Livros"
    id = Column(Integer, primary_key=True,index = True)
    nome_livro = Column(String, index = True)
    autor_livro = Column(String, index = True)
    ano_livro = Column(Integer)

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

Base.metadata.create_all(bind=engine)


def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Funcao com responsabilidade para fazer a autenticacao  do usuario
def autenticar_meu_user(credentials:HTTPBasicCredentials = Depends(security)):
   is_username_correct = secrets.compare_digest(credentials.username, USER)
   is_password_correct = secrets.compare_digest(credentials.password, PASSWORD)

   if not (is_username_correct and is_password_correct):
       raise HTTPException(
           status_code = 401,
           detail= "Usuario ou senha incorretos",
           headers={"WWW-Autheticate":"Basic"}
       )


@app.get("/livros") #GET atualizado usando o metodo sqlalchemy (banco de dados)
def get_livros(page: int = 1, limit: int = 10, db: Session = Depends(sessao_db) ,  credentials: HTTPBasicCredentials = Depends(autenticar_meu_user)):
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code =400, detail="Page ou limit estao com valores invalidos" )

    livros = db.query(LivroDB).offset(page - 1 * limit).limit(limit).all()
    
    if not livros:
        return {"message":"Nao existe nenhum livro!!"}

    total_livros = db.query(LivroDB).count()


    return {
        "page": page,
        "limit": limit,
        "total": total_livros,
        "livros":[{"id": livro.id, "nome_livro": livro.nome_livro,"autor_livro": livro.autor_livro, "ano_livro": livro.ano_livro } for livro in livros]
    }


#id do livro
#nome do livros
#autor do livro
#ano de lancamento do livro

#Nao mais .dict() e agora .model_dump()

@app.post("/adiciona") #POST atualizado usando o metodo sqlalchemy (banco de dados)
def post_livros(livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_user) ):
    db_livro = db.query(LivroDB).filter(LivroDB.nome_livro == livro.nome_livro, LivroDB.autor_livro == livro.autor_livro).first()
    if db_livro:
        raise HTTPException(status_code = 400, detail = "Esse livro ja existe dentro do banco de dados")

    novo_livro = LivroDB(nome_livro = livro.nome_livro, autor_livro = livro.autor_livro, ano_livro = livro.ano_livro)
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    return {"message": "O livro foi criado com sucesso!"}

@app.put("/atualiza/{id_livro}")#PUT atualizado usando o metodo sqlalchemy (banco de dados)
def put_livros(id_livro: int, livro: Livro,db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_user)):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()
    if not db_livro:
        raise HTTPException (status_code = 404, detail = "Este livro nao foi encontrado no seu banco de dados!")
    db_livro.nome_livro = livro.nome_livro
    db_livro.autor_livro = livro.autor_livro
    db_livro.ano_livro = livro.ano_livro

    db.commit()
    db.refresh(db_livro)

    return {"message": "O livro foi atualizado com sucesso!"}
    
@app.delete("/deletar/{id_livro}")
def delete_livro(id_livro: int, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_user)):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()

    if not db_livro:
        raise HTTPException(status_code = 404, detail = "Este livro nao foi encontrado no seu banco de dados!")
    db.delete(db_livro)
    db.commit()

    return {"message": "Seu livro foi deletado com sucesso!"}


