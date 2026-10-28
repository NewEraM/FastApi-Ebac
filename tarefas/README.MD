# API de Livros com FastAPI, SQLAlchemy e Redis

## Sobre o projeto

API REST para cadastrar, consultar, atualizar e excluir livros. Utiliza FastAPI para os endpoints, SQLAlchemy para acessar o banco de dados SQLite e Redis para armazenar temporariamente os resultados das consultas.

## Tecnologias

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Redis
- Pydantic
- HTTP Basic Authentication

## 1. Instalação

Crie e ative um ambiente virtual no Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install fastapi uvicorn sqlalchemy redis python-dotenv
```

## 2. Configuração do banco de dados

Crie um arquivo `.env` na mesma pasta do `main.py`:

```env
DATABASE_URL=sqlite:///./livros.db
USER=admin
PASSWORD=senha123
REDIS_HOST=localhost
REDIS_PORT=6379
```

Use uma senha própria em vez do exemplo acima. Não envie seu arquivo `.env` para o GitHub.

## 3. Configuração do Redis

### Opção A — Redis já instalado localmente

Inicie o servidor Redis e mantenha-o em execução na porta 6379.

Verifique a conexão com:

```powershell
redis-cli ping
```

O resultado esperado é:

```text
PONG
```

### Opção B — Redis usando Docker

Se o Docker estiver instalado, execute:

```powershell
docker run -d --name redis-livros -p 6379:6379 redis:7
```

Para verificar o funcionamento:

```powershell
docker exec redis-livros redis-cli ping
```

O resultado esperado é `PONG`.

Se o contêiner já existir, inicie-o com:

```powershell
docker start redis-livros
```

Não é necessário usar Docker para executar a API se você já tiver um servidor Redis local funcionando.

## 4. Executando a API

Na pasta que contém o `main.py`, execute:

```powershell
uvicorn main:app --reload
```

A documentação interativa ficará disponível em:

http://127.0.0.1:8000/docs

## 5. Testando os endpoints

Os exemplos abaixo utilizam a autenticação configurada no arquivo `.env`.

### Cadastrar um livro

```powershell
curl.exe -u admin:senha123 -X POST http://127.0.0.1:8000/adiciona -H "Content-Type: application/json" -d "{\"nome_livro\":\"Dom Casmurro\",\"autor_livro\":\"Machado de Assis\",\"ano_livro\":1899}"
```

### Consultar os livros

```powershell
curl.exe -u admin:senha123 "http://127.0.0.1:8000/livros?page=1&limit=10"
```

Execute o comando duas vezes. A primeira consulta busca os dados no SQLite e os armazena no Redis; a segunda pode retornar diretamente do cache.

### Inspecionar o cache

```powershell
curl.exe -u admin:senha123 http://127.0.0.1:8000/debug/redis
```

### Atualizar um livro

Substitua `1` pelo ID real do livro:

```powershell
curl.exe -u admin:senha123 -X PUT http://127.0.0.1:8000/atualiza/1 -H "Content-Type: application/json" -d "{\"nome_livro\":\"Dom Casmurro - Revisado\",\"autor_livro\":\"Machado de Assis\",\"ano_livro\":1899}"
```

### Excluir um livro

```powershell
curl.exe -u admin:senha123 -X DELETE http://127.0.0.1:8000/deletar/1
```

Depois de incluir, atualizar ou excluir um livro, consulte novamente `/livros` para verificar que os resultados correspondem ao banco de dados atualizado.

## 6. Como funciona o cache

1. A API recebe uma solicitação para consultar livros.
2. O Redis é consultado usando uma chave que considera a página e o limite.
3. Se houver dados em cache, eles são retornados diretamente.
4. Caso contrário, a API consulta o banco SQLite e armazena a resposta no Redis.
5. O cache expira automaticamente após 60 segundos.
6. Ao cadastrar, atualizar ou excluir um livro, as chaves de cache das listagens são invalidadas.

## 7. Observações

- O Redis precisa estar em execução para que a integração funcione.
- A API utiliza SQLite como banco de dados original; o Redis serve como cache.
- A autenticação HTTP Basic é utilizada nos endpoints protegidos.
- O tempo de resposta pode variar conforme o ambiente e o tamanho dos dados.
