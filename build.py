# build.py
# Script para empacotar a aplicação web em executável

import subprocess
import sys
import os

def build():
    """Empacota a aplicação web em executável"""
    print("🔨 Iniciando build da aplicação web...")
    
    # Verifica se o PyInstaller está instalado
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Cria arquivo principal para web
    web_main_content = '''
# web_main.py
# Aplicação web empacotada com PyWebview

import webview
import threading
import uvicorn
from web_app import app

def start_server():
    """Inicia o servidor FastAPI em thread separada"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if __name__ == "__main__":
    # Inicia servidor em thread separada
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Aguarda um pouco para o servidor inicializar
    import time
    time.sleep(2)
    
    # Cria janela web
    webview.create_window(
        "Bilheteria - Museu Cais do Sertão",
        "http://127.0.0.1:8000",
        width=1200,
        height=800,
        resizable=True,
        min_size=(800, 600)
    )
    webview.start(debug=False)
'''
    
    with open("web_main.py", "w", encoding="utf-8") as f:
        f.write(web_main_content)
    
    # Comando para build
    cmd = [
        "pyinstaller",
        "--onefile",                    # Arquivo único
        "--windowed",                   # Sem console (GUI)
        "--name=BilheteriaCais",        # Nome do executável
        "--icon=icon.ico",              # Ícone (se existir)
        "--add-data=templates;templates",  # Inclui templates
        "--add-data=static;static",     # Inclui arquivos estáticos
        "--hidden-import=fastapi",
        "--hidden-import=uvicorn",
        "--hidden-import=webview",
        "--hidden-import=jinja2",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=bcrypt",
        "web_main.py"
    ]
    
    # Remove parâmetros de ícone se não existir
    if not os.path.exists("icon.ico"):
        cmd = [c for c in cmd if c != "--icon=icon.ico"]
    
    print("📦 Executando PyInstaller...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build concluído com sucesso!")
        print("📁 Executável criado em: dist/BilheteriaCais.exe")
        print("\n🚀 Para executar:")
        print("   dist/BilheteriaCais.exe")
        print("\n📝 Nota: A aplicação abrirá em uma janela nativa do Windows")
    else:
        print("❌ Erro no build:")
        print(result.stderr)

if __name__ == "__main__":
    build()
