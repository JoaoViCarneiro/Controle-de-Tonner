"""
database.py
Gerencia conexão com SQLite.
O banco de dados fica em uma pasta 'db' no mesmo diretório do executável.
"""

import sqlite3
import os
import shutil
import sys
from datetime import datetime


def _get_app_dir() -> str:
    """Retorna o diretório onde o executável (ou o script) está rodando."""
    if getattr(sys, 'frozen', False):
        # Rodando como executável PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Rodando como script Python
        return os.path.dirname(os.path.abspath(__file__))


def _get_db_dir() -> str:
    """Retorna o diretório 'db' ao lado do executável."""
    pasta = os.path.join(_get_app_dir(), "db")
    os.makedirs(pasta, exist_ok=True)
    return pasta


def _get_db_path() -> str:
    return os.path.join(_get_db_dir(), "dados.db")


def _get_backup_dir() -> str:
    backup = os.path.join(_get_db_dir(), "backups")
    os.makedirs(backup, exist_ok=True)
    return backup


def get_conexao():
    return sqlite3.connect(_get_db_path())


def fazer_backup_automatico():
    try:
        nome_backup = f"backup_{datetime.now().strftime('%Y%m%d')}.db"
        caminho_backup = os.path.join(_get_backup_dir(), nome_backup)
        if not os.path.exists(caminho_backup) and os.path.exists(_get_db_path()):
            shutil.copy2(_get_db_path(), caminho_backup)
            backups = sorted([f for f in os.listdir(_get_backup_dir()) if f.startswith("backup_")])
            while len(backups) > 30:
                os.remove(os.path.join(_get_backup_dir(), backups.pop(0)))
    except Exception as e:
        print(f"Aviso: Backup automatico falhou: {e}")


def fazer_backup_manual(nome_backup: str):
    caminho_backup = os.path.join(_get_backup_dir(), nome_backup)
    if os.path.exists(_get_db_path()):
        shutil.copy2(_get_db_path(), caminho_backup)
        return caminho_backup
    return None


def init_database():
    """Cria o banco e as tabelas se não existirem."""
    fazer_backup_automatico()

    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maquinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            modelo TEXT,
            tipo TEXT NOT NULL CHECK (tipo IN ('P&B', 'Colorida')),
            contador_atual INTEGER DEFAULT 0,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tonners_individual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maquina_id INTEGER NOT NULL,
            cor TEXT NOT NULL,
            data_instalacao TEXT,
            data_retirada TEXT,
            contador_inicial INTEGER DEFAULT 0,
            contador_final INTEGER,
            custo REAL DEFAULT 0.0,
            observacao TEXT,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contadores_semanais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maquina_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            contador INTEGER NOT NULL,
            observacao TEXT,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Banco inicializado em: {_get_db_path()}")
