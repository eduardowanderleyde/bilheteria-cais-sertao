# Guia de Seguranca

## IMPORTANTE: Credenciais Sensiveis

Este projeto NAO deve conter credenciais hardcoded no codigo.

### Como usar credenciais de forma segura:

1. Use variaveis de ambiente:
   ```python
   import os
   username = os.getenv("ADMIN_USERNAME")
   password = os.getenv("ADMIN_PASSWORD")
   ```

2. Configure no arquivo .env (nao versionado):
   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais
   ```

3. Para producao (Render/Heroku):
   - Configure variaveis de ambiente no painel
   - NUNCA commite arquivos .env

### Credenciais que DEVEM ser trocadas:

- ADMIN_PASSWORD
- GESTORA_PASSWORD  
- BILHETEIRA_PASSWORD
- TEST_PASSWORD
- SECRET_KEY

### Scripts de configuracao:

```bash
# Configurar ambiente local
python setup_env.py

# Criar usuarios no banco
python seed_admin.py

# Testar sistema
python test_login.py
```

### Checklist de seguranca:

- [ ] Nenhuma senha hardcoded no codigo
- [ ] Variaveis de ambiente configuradas
- [ ] Arquivo .env no .gitignore
- [ ] Credenciais de producao diferentes das de desenvolvimento
- [ ] SECRET_KEY forte e unica
- [ ] Hooks pre-commit ativados
