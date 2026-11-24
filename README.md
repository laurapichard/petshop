# Pet Shop Amigo Fiel — Sistema Web (Flask + PostgreSQL)

Sistema para funcionários do petshop: cadastro e login, clientes, pets, catálogo de serviços, atendimentos e relatórios.

## Estrutura

```
petshop/
├── app.py              # rotas Flask
├── db.py               # conexão e execução de SQL (psycopg2)
├── schema.sql          # DDL (PostgreSQL)
├── seed.sql            # dados de teste do documento
├── requirements.txt
├── templates/          # páginas HTML (Jinja2)
└── static/style.css
```

## 1. Preparar o banco

```bash
psql -U postgres -c "CREATE DATABASE petshop_amigo_fiel;"
psql -U postgres -d petshop_amigo_fiel -f schema.sql
psql -U postgres -d petshop_amigo_fiel -f seed.sql
```

## 2. Instalar dependências

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configurar conexão (opcional)

Por padrão o sistema usa `dbname=petshop_amigo_fiel user=postgres password=postgres host=localhost`. Para mudar:

```bash
export DATABASE_URL="dbname=petshop_amigo_fiel user=SEU_USUARIO password=SUA_SENHA host=localhost"
export SECRET_KEY="uma-chave-secreta-longa"
```

## 4. Executar

```bash
python app.py
```

Acesse http://127.0.0.1:5000, clique em **Cadastre-se**, crie seu funcionário e faça login.

## Modelo de dados

As tabelas seguem o modelo do documento (CLIENTE, PET, FUNCIONARIO, SERVICO, ATENDIMENTO, ITEM_ATENDIMENTO). A tabela **USUARIO** foi adicionada: ela guarda login e senha (com hash) e liga cada conta a um funcionário. Ao cadastrar um usuário, o sistema cria o funcionário e a conta de acesso juntos.

Ao registrar um atendimento, o sistema grava o preço do serviço em `item_atendimento.preco_praticado` e calcula `valor_total` na mesma transação.
