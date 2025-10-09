# 🚀 Guia de Deploy - Sistema de Bilheteria

## Deploy no Render (Recomendado)

### 1. Preparação do Repositório

1. **Faça commit das mudanças:**
```bash
git add .
git commit -m "feat: implementação completa para produção"
git push origin main
```

2. **Verifique se o .gitignore está correto:**
- ✅ `*.db` (arquivos de banco)
- ✅ `__pycache__/` (cache Python)
- ✅ `.env` (variáveis de ambiente)

### 2. Configuração no Render

1. **Acesse [render.com](https://render.com)** e faça login
2. **Clique em "New +"** → **"Web Service"**
3. **Conecte seu repositório** do GitHub
4. **Configure o serviço:**
   - **Name:** `bilheteria-cais`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python seed_admin.py`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Configuração do Banco de Dados

1. **Crie um banco PostgreSQL:**
   - Clique em **"New +"** → **"PostgreSQL"**
   - **Name:** `bilheteria-db`
   - **Plan:** `Free` (para começar)

2. **Configure a variável DATABASE_URL:**
   - No serviço web, vá em **"Environment"**
   - Adicione: `DATABASE_URL` = `from database` → `bilheteria-db`

### 4. Variáveis de Ambiente

⚠️ **IMPORTANTE:** Configure valores SEGUROS para todas as variáveis obrigatórias!

```bash
# OBRIGATÓRIAS
DATABASE_URL=postgresql://... (automático via Render)

# Gere uma SECRET_KEY segura com:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=<valor_gerado_aleatoriamente_min_32_caracteres>

# Credenciais do administrador
ADMIN_USERNAME=seu_usuario_admin
ADMIN_PASSWORD=SuaSenhaForte123!

# Configurações de produção
DEBUG=False
SECURE_COOKIES=True
ENV=production

# OPCIONAIS (deixe vazio para não criar)
GESTORA_PASSWORD=
BILHETEIRA_PASSWORD=
```

**⚠️ NUNCA use senhas padrão ou fracas em produção!**

### 5. Deploy

1. **Clique em "Create Web Service"**
2. **Aguarde o build** (pode levar alguns minutos)
3. **Acesse a URL** fornecida pelo Render
4. **Teste o login** com as credenciais configuradas

## Deploy em Outras Plataformas

### Heroku

1. **Instale o Heroku CLI**
2. **Crie o app:**
```bash
heroku create bilheteria-cais
```

3. **Configure o banco:**
```bash
heroku addons:create heroku-postgresql:mini
```

4. **Configure as variáveis (OBRIGATÓRIO):**
```bash
# Gere uma SECRET_KEY segura primeiro:
# python -c "import secrets; print(secrets.token_urlsafe(32))"

heroku config:set SECRET_KEY=<valor_gerado_seguro>
heroku config:set ADMIN_USERNAME=seu_usuario_admin
heroku config:set ADMIN_PASSWORD=SuaSenhaForte123!
heroku config:set DEBUG=False
heroku config:set SECURE_COOKIES=True
heroku config:set ENV=production
```

**⚠️ Substitua os valores de exemplo por credenciais seguras!**

5. **Deploy:**
```bash
git push heroku main
```

### Railway

1. **Conecte o repositório** no Railway
2. **Configure as variáveis** de ambiente
3. **Deploy automático** com PostgreSQL

### DigitalOcean App Platform

1. **Use o `render.yaml`** como referência
2. **Configure PostgreSQL** como serviço
3. **Configure as variáveis** de ambiente

## Verificação Pós-Deploy

### 1. Teste de Funcionamento

1. **Acesse a URL** do deploy
2. **Teste o login** com diferentes usuários
3. **Teste as funcionalidades:**
   - ✅ Venda de ingressos
   - ✅ Venda em grupo
   - ✅ Relatórios
   - ✅ Exportação CSV/Excel
   - ✅ Painel admin (se admin/gestora)

### 2. Verificação de Segurança

1. **Teste de autenticação:**
   - Login com credenciais incorretas
   - Acesso sem login
   - Logout

2. **Teste de autorização:**
   - Bilheteira não pode acessar admin
   - Bilheteira não pode excluir registros

3. **Teste de CSRF:**
   - Formulários devem ter token CSRF
   - Requisições sem token devem falhar

### 3. Monitoramento

1. **Logs da aplicação:**
   - Acesse o dashboard do Render
   - Monitore logs de erro
   - Verifique performance

2. **Banco de dados:**
   - Monitore uso de conexões
   - Verifique espaço em disco
   - Configure backup automático

## Backup e Restauração

### Backup do Banco

```bash
# Via Render CLI
render-db dump bilheteria-db > backup.sql

# Via psql direto
pg_dump $DATABASE_URL > backup.sql
```

### Restauração

```bash
# Via psql
psql $DATABASE_URL < backup.sql
```

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco:**
   - Verifique se `DATABASE_URL` está correto
   - Confirme se o banco está ativo

2. **Erro de migração:**
   - Execute `python seed_admin.py` manualmente
   - Verifique logs de build

3. **Erro de permissão:**
   - Verifique se as variáveis de ambiente estão corretas
   - Confirme se o usuário admin foi criado

4. **Erro de CSRF:**
   - Verifique se `SECRET_KEY` está configurado
   - Confirme se os templates estão corretos

### Logs Úteis

```bash
# Logs da aplicação
render logs bilheteria-cais

# Logs do banco
render logs bilheteria-db
```

## Atualizações

### Deploy de Atualizações

1. **Faça as mudanças** no código
2. **Commit e push:**
```bash
git add .
git commit -m "feat: nova funcionalidade"
git push origin main
```

3. **Render fará deploy automático**
4. **Teste** a nova versão

### Migração de Dados

Se houver mudanças no banco:

1. **Crie uma migração Alembic:**
```bash
alembic revision --autogenerate -m "descrição da mudança"
```

2. **Aplique a migração:**
```bash
alembic upgrade head
```

## Suporte

Para problemas específicos:

1. **Verifique os logs** do Render
2. **Consulte a documentação** do FastAPI
3. **Abra uma issue** no GitHub
4. **Contate o suporte** do Render se necessário

---

**Sistema pronto para produção! 🎉**
