#!/usr/bin/env python3
"""
Script de inicialização do Sistema de Coleta de Dados
Executa verificações de sistema e inicia o servidor Flask
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        print(f"Versão atual: {platform.python_version()}")
        return False
    print(f"✅ Python {platform.python_version()} OK")
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import flask
        import PyPDF2
        print("✅ Dependências instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = ['uploads', 'backups']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Diretório criado: {directory}")
        else:
            print(f"✅ Diretório existe: {directory}")

def show_system_info():
    """Mostra informações do sistema"""
    print("\n" + "="*50)
    print("📋 SISTEMA DE COLETA DE DADOS")
    print("="*50)
    print(f"🐍 Python: {platform.python_version()}")
    print(f"💻 Sistema: {platform.system()} {platform.release()}")
    print(f"📁 Diretório: {os.getcwd()}")
    print("="*50)

def main():
    """Função principal"""
    show_system_info()
    
    print("\n🔍 Verificando sistema...")
    
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        print("\n💡 Para instalar dependências:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    create_directories()
    
    print("\n🚀 Iniciando servidor...")
    print("📍 Acesse: http://localhost:5000")
    print("⏹️  Para parar: Ctrl+C")
    print("-" * 50)
    
    # Inicia o servidor Flask
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Sistema finalizado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
