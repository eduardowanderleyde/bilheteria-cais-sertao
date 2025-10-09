# Deploy no Render - Passo a Passo

## 1. Preparar Repositório
```bash
# Fazer push do código
git add .
git commit -m "feat: preparar para deploy"
git push origin main
```

## 2. Criar Serviço no Render
1. Acesse: https://render.com
2. Conecte seu repositório GitHub
3. Crie um **Web Service**
4. Configure:

### **Build Command:**
```bash
pip install -r requirements.txt && alembic upgrade head
```

### **Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### **Variáveis de Ambiente:**
```
DATABASE_URL=postgresql://user:pass@host:5432/bilheteria
SECRET_KEY=sua-chave-secreta-forte-32-chars
ADMIN_USERNAME=admin
ADMIN_PASSWORD=senha-super-segura-123!
GESTORA_PASSWORD=senha-gestora-123!
BILHETEIRA_PASSWORD=senha-bilheteira-123!
TEST_PASSWORD=senha-teste-123!
DEBUG=False
SECURE_COOKIES=True
```

## 3. Criar Banco PostgreSQL
1. No Render, crie um **PostgreSQL Database**
2. Copie a `DATABASE_URL` gerada
3. Cole na variável `DATABASE_URL` do Web Service

## 4. Deploy Automático
- Render faz deploy automático a cada push
- Acesse a URL fornecida
- Faça login com as credenciais configuradas

## 5. Pós-Deploy
```bash
# Criar usuários no banco (via terminal do Render)
python seed_admin.py
```

## ✅ Pronto!
Sistema online e funcionando!
