# Deploy com Docker - VPS

## 1. Preparar VPS
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 2. Configurar Projeto
```bash
# Clonar repositório
git clone https://github.com/eduardowanderleyde/bilheteria-cais-sertao.git
cd bilheteria-cais-sertao

# Criar .env
cp .env.example .env
nano .env
```

## 3. Configurar .env
```env
DATABASE_URL=postgresql://bilheteria:bilheteria123@db:5432/bilheteria
SECRET_KEY=sua-chave-secreta-forte-32-chars
ADMIN_USERNAME=admin
ADMIN_PASSWORD=senha-super-segura-123!
GESTORA_PASSWORD=senha-gestora-123!
BILHETEIRA_PASSWORD=senha-bilheteira-123!
TEST_PASSWORD=senha-teste-123!
DEBUG=False
SECURE_COOKIES=True
```

## 4. Deploy
```bash
# Rodar com Docker Compose
docker-compose up -d

# Criar usuários
docker-compose exec web python seed_admin.py

# Ver logs
docker-compose logs -f
```

## 5. Configurar Nginx (Opcional)
```bash
# Copiar nginx.conf
sudo cp nginx.conf /etc/nginx/sites-available/bilheteria
sudo ln -s /etc/nginx/sites-available/bilheteria /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## ✅ Pronto!
Sistema online no VPS!
