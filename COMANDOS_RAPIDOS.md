# Comandos Rápidos - Bilheteria Cais

## 🗄️ **Banco de Dados Atual**

**SQLite** (desenvolvimento) - arquivo `bilheteria.db` local
- **Vantagem**: Simples, não precisa instalar nada
- **Desvantagem**: Não é adequado para produção

**PostgreSQL** (produção) - via variável de ambiente `DATABASE_URL`

## 🚀 **Comandos para Rodar o Projeto**

### **Opção 1: Desenvolvimento Simples (SQLite)**
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar ambiente
python setup_env.py

# 3. Criar usuários no banco
python seed_admin.py

# 4. Rodar servidor
python run_server.py
```

### **Opção 2: Desenvolvimento com Docker (PostgreSQL)**
```bash
# 1. Rodar banco + aplicação
docker-compose up

# 2. Acessar: http://localhost:8000
```

### **Opção 3: Produção (PostgreSQL)**
```bash
# 1. Configurar variáveis de ambiente
export DATABASE_URL="postgresql://user:pass@host:5432/bilheteria"
export SECRET_KEY="sua-chave-secreta"
export ADMIN_PASSWORD="sua-senha-segura"

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar migrações (se usando Alembic)
alembic upgrade head

# 4. Criar usuários
python seed_admin.py

# 5. Rodar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🧹 **Limpeza de Arquivos Desnecessários**

### **Arquivos que DEVEM ser removidos:**
```bash
# Remover arquivo SQLite (será recriado automaticamente)
rm bilheteria.db

# Remover cache Python
rm -rf __pycache__/
rm -rf app/__pycache__/
rm -rf tests/__pycache__/

# Remover arquivos temporários
rm -rf .pytest_cache/
rm -rf htmlcov/
rm -rf .coverage
```

### **Arquivos que DEVEM ser mantidos:**
- `requirements.txt` - dependências Python
- `requirements-dev.txt` - dependências de desenvolvimento
- `Dockerfile` - containerização
- `docker-compose.yml` - ambiente de desenvolvimento
- `.env.example` - exemplo de configuração
- `alembic.ini` - migrações de banco

## 🔧 **Configuração de Ambiente**

### **Para SQLite (desenvolvimento):**
```bash
# Copiar exemplo
cp .env.example .env

# Editar .env
DATABASE_URL=sqlite:///./bilheteria.db
SECRET_KEY=sua-chave-secreta
ADMIN_USERNAME=admin
ADMIN_PASSWORD=sua-senha
```

### **Para PostgreSQL (produção):**
```bash
# Editar .env
DATABASE_URL=postgresql://user:pass@localhost:5432/bilheteria
SECRET_KEY=sua-chave-secreta
ADMIN_USERNAME=admin
ADMIN_PASSWORD=sua-senha
```

## 🧪 **Comandos de Teste**

```bash
# Rodar todos os testes
pytest

# Rodar testes com coverage
pytest --cov=app

# Rodar testes específicos
pytest tests/test_auth.py

# Rodar linting
flake8 app/ tests/

# Rodar formatação
black app/ tests/
```

## 🐳 **Comandos Docker**

```bash
# Construir imagem
docker build -t bilheteria-cais .

# Rodar container
docker run -p 8000:8000 bilheteria-cais

# Rodar com docker-compose
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar tudo
docker-compose down
```

## 📊 **Comandos de Banco**

### **SQLite:**
```bash
# Ver estrutura
sqlite3 bilheteria.db ".schema"

# Ver dados
sqlite3 bilheteria.db "SELECT * FROM users;"

# Backup
cp bilheteria.db bilheteria_backup.db
```

### **PostgreSQL:**
```bash
# Conectar
psql $DATABASE_URL

# Backup
pg_dump $DATABASE_URL > backup.sql

# Restaurar
psql $DATABASE_URL < backup.sql
```

## 🚨 **Problemas Comuns**

### **Erro de banco não encontrado:**
```bash
# Recriar banco SQLite
rm bilheteria.db
python seed_admin.py
```

### **Erro de dependências:**
```bash
# Reinstalar tudo
pip install -r requirements.txt
```

### **Erro de permissão:**
```bash
# Dar permissão de execução
chmod +x *.py
```

## 📝 **Resumo Rápido**

**Para começar AGORA:**
1. `pip install -r requirements.txt`
2. `python setup_env.py`
3. `python seed_admin.py`
4. `python run_server.py`
5. Acessar: http://localhost:8000

**Login padrão:**
- Usuário: admin
- Senha: (definida no .env)
