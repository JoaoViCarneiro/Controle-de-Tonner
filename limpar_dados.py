"""
limpar_dados.py
UTILITÁRIO PARA LIMPAR TODOS OS DADOS DO SISTEMA
Execute este arquivo na mesma pasta do Controletonner.exe
"""

import os
import sys
import shutil
from datetime import datetime


def get_db_dir():
    """Retorna a pasta 'db' ao lado deste script/executável."""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "db")


def criar_backup_antes_limpar():
    """Cria um backup antes de limpar."""
    db_path = os.path.join(get_db_dir(), "dados.db")
    backup_dir = os.path.join(get_db_dir(), "backups")

    if not os.path.exists(db_path):
        print("⚠️  Nenhum banco de dados encontrado para fazer backup.")
        return

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"backup_antes_limpeza_{timestamp}.db")

    try:
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup criado em: {backup_path}")
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")


def limpar_tudo():
    """Remove todos os dados do sistema."""
    db_dir = get_db_dir()
    db_path = os.path.join(db_dir, "dados.db")
    backup_dir = os.path.join(db_dir, "backups")
    relatorios_dir = os.path.join(db_dir, "relatorios_exportados")

    print("\n🔄 Iniciando limpeza...")

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✅ Banco de dados removido.")
        except Exception as e:
            print(f"❌ Erro ao remover banco: {e}")
    else:
        print("⚠️  Banco de dados não encontrado.")

    if os.path.exists(backup_dir):
        try:
            shutil.rmtree(backup_dir)
            print(f"✅ Backups removidos.")
        except Exception as e:
            print(f"❌ Erro ao remover backups: {e}")

    if os.path.exists(relatorios_dir):
        try:
            shutil.rmtree(relatorios_dir)
            print(f"✅ Relatórios removidos.")
        except Exception as e:
            print(f"❌ Erro ao remover relatórios: {e}")

    # Recria o banco zerado
    try:
        from database import init_database
        init_database()
        print("✅ Banco de dados recriado vazio com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao recriar banco: {e}")

    print("\n" + "=" * 60)
    print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🛠️  UTILITÁRIO DE LIMPEZA - CONTROLE DE tonner")
    print("=" * 60)
    print(f"\n📁 Pasta do banco: {get_db_dir()}")
    print("\n⚠️  ATENÇÃO: Esta operação irá apagar TODOS os dados:")
    print("   - Todas as máquinas cadastradas")
    print("   - Todas as trocas de tonner")
    print("   - Todos os contadores semanais")
    print("   - Todos os relatórios gerados")
    print("   - Todos os backups")
    print("\n1. 🧹 Limpeza COMPLETA (apaga TUDO)")
    print("2. ❌ Cancelar")

    opcao = input("\nEscolha uma opção (1-2): ")

    if opcao == "1":
        confirmacao = input("\nDigite 'LIMPAR' para confirmar: ")
        if confirmacao == "LIMPAR":
            criar_backup_antes_limpar()
            limpar_tudo()
        else:
            print("❌ Operação cancelada.")
    else:
        print("❌ Operação cancelada.")

    input("\nPressione ENTER para sair...")
