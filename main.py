"""
main.py
PONTO DE ENTRADA DO SISTEMA - COM COMPATIBILIDADE WINDOWS
"""

import sys
import os
import platform

# ========== DETECTAR VERSÃO DO WINDOWS ==========
print("=" * 60)
print("🚀 CONTROLE DE TONER - INICIANDO...")
print("=" * 60)

# Verificar se é Windows
if platform.system() == "Windows":
    try:
        from compatibilidade import detector
        detector.aplicar_correcoes()
        print(f"✅ Sistema otimizado para {detector.nome}")
    except Exception as e:
        print(f"⚠️  Não foi possível detectar versão do Windows: {e}")
else:
    print(f"🐧 Sistema detectado: {platform.system()}")

# ========== CORREÇÃO PARA WINDOWS 7 ==========
if platform.system() == "Windows" and platform.release() == "7":
    print("⚠️  Windows 7 detectado - Aplicando modo de compatibilidade...")
    # Forçar modo de compatibilidade com versões antigas de bibliotecas

    # Desabilitar verificações de SSL em versões antigas
    import ssl
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

# ========== CORREÇÃO PARA PYTHON 3.x ==========
if sys.version_info >= (3, 14):
    print("🐍 Python 3.14+ detectado. Aplicando correções de compatibilidade...")
    try:
        import customtkinter as ctk
        original_configure = ctk.CTkComboBox.configure

        def patched_configure(self, **kwargs):
            try:
                return original_configure(self, **kwargs)
            except Exception as e:
                if "invalid command name" in str(e):
                    pass
                else:
                    raise e

        ctk.CTkComboBox.configure = patched_configure
        print("✅ Correção aplicada com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao aplicar correção: {e}")

# ========== CONFIGURAR CAMINHOS ==========
# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print(f"📁 Diretório atual: {os.path.dirname(os.path.abspath(__file__))}")

# ========== INICIAR APLICAÇÃO ==========
try:
    print("🔄 Inicializando sistema...")
    from gui_app import ControleTonerApp

    print("✅ Sistema carregado com sucesso!")
except ImportError as e:
    print("=" * 50)
    print("❌ ERRO CRÍTICO: Não foi possível importar o módulo!")
    print("=" * 50)
    print(f"\nErro: {e}\n")
    print("Verifique se todos os arquivos estão na pasta:")
    print(f"   {os.path.dirname(os.path.abspath(__file__))}")
    print("\nArquivos necessários:")
    print("   - database.py")
    print("   - database_operations.py")
    print("   - models.py")
    print("   - gui_app.py")
    print("   - relatorios.py")
    print("   - calendar_widget.py")
    print("   - compatibilidade.py (NOVO)")
    print("\nPressione ENTER para sair...")
    input()
    sys.exit(1)

if __name__ == "__main__":
    try:
        print("🚀 Iniciando aplicação...")
        app = ControleTonerApp()

        # Configurar ícone da janela com fallback
        try:
            if os.path.exists("icone.ico"):
                app.iconbitmap("icone.ico")
        except:
            print("⚠️  Não foi possível definir ícone da janela")

        app.title("Controle de Toner v3.0")
        app.mainloop()

    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

        # Mensagem amigável para o usuário
        if platform.system() == "Windows" and platform.release() == "7":
            print("\n💡 DICA: No Windows 7, tente executar como administrador")
            print("   ou instale o Service Pack 1 e atualizações do Visual C++")

        input("\nPressione ENTER para sair...")