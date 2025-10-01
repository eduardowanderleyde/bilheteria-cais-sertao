# 📋 Guia de Instalação - Sistema de Bilheteria

## 🎯 Instalação Rápida (5 minutos)

### 1. Pré-requisitos
- **Windows 10/11**
- **Python 3.8+** ([Download aqui](https://python.org/downloads/))
- **Conexão com internet** (apenas para instalar dependências)

### 2. Download e Instalação

1. **Baixe o projeto** (todos os arquivos)
2. **Abra o PowerShell** como administrador
3. **Navegue até a pasta** do projeto:
   ```powershell
   cd C:\caminho\para\bilheteria-cais
   ```

4. **Instale as dependências:**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

### 3. Teste Rápido

**Versão Desktop:**
```powershell
python run_desktop.py
```

**Versão Web:**
```powershell
python run_web.py
```
Acesse: http://127.0.0.1:8000

**Login:**
- Usuário: `funcionario1`
- Senha: `123456`

## 🔧 Instalação Detalhada

### Passo 1: Verificar Python
```powershell
python --version
```
Deve mostrar Python 3.8 ou superior.

### Passo 2: Instalar Dependências
```powershell
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list | findstr customtkinter
pip list | findstr fastapi
```

### Passo 3: Testar Aplicação

**Teste Desktop:**
```powershell
python app_gui.py
```

**Teste Web:**
```powershell
python web_app.py
```

### Passo 4: Criar Executáveis (Opcional)

```powershell
# Build completo
python build_all.py

# Ou individual
python build_desktop.py
python build_web.py
```

## 🚨 Solução de Problemas

### Erro: "Python não é reconhecido"
**Solução:**
1. Reinstale Python marcando "Add to PATH"
2. Ou adicione manualmente ao PATH do Windows

### Erro: "ModuleNotFoundError"
**Solução:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Erro: "Permission denied"
**Solução:**
1. Execute PowerShell como administrador
2. Ou instale em ambiente virtual:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Erro de Build PyInstaller
**Solução:**
```powershell
# Limpar cache
rmdir /s build dist
python build_all.py
```

### Erro: "Port 8000 already in use"
**Solução:**
1. Feche outras aplicações na porta 8000
2. Ou altere a porta em `run_web.py`

## 📁 Estrutura de Arquivos

```
bilheteria-cais/
├── app_gui.py              # Versão Desktop
├── web_app.py              # Versão Web
├── requirements.txt        # Dependências
├── run_desktop.py         # Executar Desktop
├── run_web.py             # Executar Web
├── build_desktop.py       # Build Desktop
├── build_web.py           # Build Web
├── build_all.py           # Build Completo
├── templates/             # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── sell.html
│   ├── reports.html
│   └── reports_summary.html
├── static/                # Arquivos estáticos
├── temp/                  # Arquivos temporários
├── bilheteria.db          # Banco de dados (criado automaticamente)
└── dist/                  # Executáveis (após build)
    ├── BilheteriaCais.exe
    └── BilheteriaWeb.exe
```

## 🔄 Atualizações

### Atualizar Dependências
```powershell
pip install -r requirements.txt --upgrade
```

### Atualizar Aplicação
1. Substitua os arquivos antigos pelos novos
2. Execute novamente a instalação

## 🗂️ Backup e Restauração

### Backup do Banco
```powershell
copy bilheteria.db backup_%date%.db
```

### Restaurar Backup
```powershell
copy backup_20240101.db bilheteria.db
```

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** de erro
2. **Consulte** o README.md
3. **Teste** com usuário administrador
4. **Reinstale** as dependências se necessário

## ✅ Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Versão Desktop funcionando (`python run_desktop.py`)
- [ ] Versão Web funcionando (`python run_web.py`)
- [ ] Login funcionando (funcionario1/123456)
- [ ] Venda de ingressos funcionando
- [ ] Relatórios funcionando
- [ ] Exportação Excel funcionando
- [ ] Executáveis criados (opcional)

**🎉 Parabéns! Sua instalação está completa!**
