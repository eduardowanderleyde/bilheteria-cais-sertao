# Deploy no Heroku - Passo a Passo

## 1. Instalar Heroku CLI
```bash
# Windows
winget install Heroku.HerokuCLI

# Ou baixar de: https://devcenter.heroku.com/articles/heroku-cli
```

## 2. Preparar Projeto
```bash
# Login no Heroku
heroku login

# Criar app
heroku create bilheteria-cais-sertao

# Adicionar banco PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev
```

## 3. Configurar Variáveis
```bash
heroku config:set SECRET_KEY="sua-chave-secreta-forte-32-chars"
heroku config:set ADMIN_USERNAME="admin"
heroku config:set ADMIN_PASSWORD="senha-super-segura-123!"
heroku config:set GESTORA_PASSWORD="senha-gestora-123!"
heroku config:set BILHETEIRA_PASSWORD="senha-bilheteira-123!"
heroku config:set TEST_PASSWORD="senha-teste-123!"
heroku config:set DEBUG="False"
heroku config:set SECURE_COOKIES="True"
```

## 4. Deploy
```bash
# Fazer push
git push heroku main

# Criar usuários
heroku run python seed_admin.py

# Abrir app
heroku open
```

## ✅ Pronto!
Sistema online no Heroku!
