# Kafka, ZooKeeper e Kafka-UI com Docker Compose

## 📌 Sobre o projeto

Este projeto consiste na configuração de um ambiente local de mensageria utilizando Docker Compose, integrando três serviços: ZooKeeper, Kafka e Kafka-UI.

O objetivo é orquestrar os contêineres, configurar suas dependências e portas de comunicação e disponibilizar uma interface gráfica para monitorar o ambiente Kafka.

## 🛠️ Tecnologias utilizadas

- **Docker Compose:** orquestração dos serviços.
- **ZooKeeper:** coordenação do cluster Kafka.
- **Apache Kafka:** plataforma de mensageria para processamento e distribuição de eventos.
- **Kafka-UI:** interface gráfica para gerenciamento e monitoramento do Kafka.

## 📂 Estrutura do projeto

```text
projeto-kafka/
├── docker-compose.yml
└── README.md
```

## 🚀 Como executar

### 1. Pré-requisitos

- Docker Desktop instalado e em execução.
- Docker Compose disponível no terminal.

### 2. Iniciar os serviços

Na raiz do projeto, execute:

```bash
docker compose up -d
```

O comando inicia os serviços em segundo plano.

### 3. Verificar os contêineres

Para verificar o estado dos serviços, execute:

```bash
docker compose ps
```

Para acompanhar os logs:

```bash
docker compose logs -f
```

Para consultar os logs de um serviço específico:

```bash
docker compose logs -f kafka
```

### 4. Acessar o Kafka-UI

Abra o navegador e acesse:

http://localhost:8080

A interface permite visualizar os clusters configurados, consultar tópicos e acompanhar mensagens, conforme a configuração do ambiente.

### 5. Encerrar os serviços

Para parar e remover os contêineres criados pelo Compose, execute:

```bash
docker compose down
```

## 🔌 Serviços e portas

| Serviço | Porta | Finalidade |
|---|---|---|
| ZooKeeper | 2181 | Coordenação do Kafka |
| Kafka | 9092 | Comunicação com produtores e consumidores |
| Kafka-UI | 8080 | Interface gráfica de gerenciamento |

As portas podem variar conforme a configuração definida no arquivo `docker-compose.yml`.

## ✅ Resultados esperados

- Inicialização dos três serviços por meio de um único comando.
- Comunicação configurada entre Kafka, ZooKeeper e Kafka-UI.
- Portas de acesso devidamente configuradas.
- Interface gráfica acessível para monitoramento do Kafka.
- Evidência visual demonstrando o funcionamento do ambiente.

## 🎯 Conclusão

O exercício permite praticar a orquestração de múltiplos serviços com Docker Compose, a configuração de dependências entre contêineres e a integração de ferramentas utilizadas em arquiteturas de microsserviços e sistemas orientados a eventos.

**Observação:** o funcionamento correto depende das imagens, variáveis de ambiente, endereços de conexão e configurações definidas no arquivo `docker-compose.yml`.