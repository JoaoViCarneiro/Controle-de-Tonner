"""
database_operations.py
CRUD completo com auto-finalização de toners duplicados e função de edição.
"""

import sqlite3
from typing import List, Optional, Dict
from models import Maquina, Toner, Rendimento
from database import get_conexao


# ==================== MÁQUINAS ====================

def listar_maquinas() -> List[Maquina]:
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, modelo, tipo, contador_atual, data_cadastro FROM maquinas ORDER BY nome')
    maquinas = [Maquina(id=r[0], nome=r[1], modelo=r[2] or "", tipo=r[3],
                        contador_atual=r[4] or 0, data_cadastro=r[5]) for r in cursor.fetchall()]
    conn.close()
    return maquinas


def salvar_maquina(maquina: Maquina) -> int:
    conn = get_conexao()
    cursor = conn.cursor()
    if maquina.id:
        cursor.execute('UPDATE maquinas SET nome=?, modelo=?, tipo=?, contador_atual=? WHERE id=?',
                       (maquina.nome, maquina.modelo, maquina.tipo, maquina.contador_atual, maquina.id))
        conn.commit(); conn.close()
        return maquina.id
    else:
        cursor.execute('INSERT INTO maquinas (nome, modelo, tipo, contador_atual, data_cadastro) VALUES (?,?,?,?,?)',
                       (maquina.nome, maquina.modelo, maquina.tipo, maquina.contador_atual, maquina.data_cadastro or None))
        mid = cursor.lastrowid
        conn.commit(); conn.close()
        return mid


def deletar_maquina(maquina_id: int) -> bool:
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM maquinas WHERE id=?", (maquina_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao deletar: {e}")
        return False
    finally:
        conn.close()


# ==================== TONERS ====================

def registrar_toner(toner: Toner) -> int:
    """
    Registra um novo toner. Se já existir um toner ativo da mesma cor
    na mesma máquina, ele é finalizado automaticamente.
    """
    conn = get_conexao()
    cursor = conn.cursor()

    # Verifica toner ativo da mesma cor
    cursor.execute('''
        SELECT id FROM toners_individual
        WHERE maquina_id=? AND cor=? AND data_retirada IS NULL
        ORDER BY data_instalacao DESC LIMIT 1
    ''', (toner.maquina_id, toner.cor))
    ativo = cursor.fetchone()

    if ativo:
        # Finaliza o anterior automaticamente com o contador inicial do novo
        cursor.execute('UPDATE toners_individual SET data_retirada=?, contador_final=? WHERE id=?',
                       (toner.data_instalacao, toner.contador_inicial, ativo[0]))

    cursor.execute('''
        INSERT INTO toners_individual (maquina_id, cor, data_instalacao, contador_inicial, custo, observacao)
        VALUES (?,?,?,?,?,?)
    ''', (toner.maquina_id, toner.cor, toner.data_instalacao,
          toner.contador_inicial, toner.custo, toner.observacao))

    toner_id = cursor.lastrowid
    cursor.execute('UPDATE maquinas SET contador_atual=MAX(contador_atual,?) WHERE id=?',
                   (toner.contador_inicial, toner.maquina_id))
    conn.commit(); conn.close()
    return toner_id


def finalizar_toner(toner_id: int, data_retirada: str, contador_final: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute('UPDATE toners_individual SET data_retirada=?, contador_final=? WHERE id=?',
                   (data_retirada, contador_final, toner_id))
    cursor.execute('''UPDATE maquinas SET contador_atual=MAX(contador_atual,?)
                      WHERE id=(SELECT maquina_id FROM toners_individual WHERE id=?)''',
                   (contador_final, toner_id))
    conn.commit(); conn.close()


def editar_toner(toner_id: int, cor: str, data_instalacao: str,
                 data_retirada, contador_inicial: int, contador_final, custo: float):
    """
    Edita um registro de toner. Se a cor mudar e já houver outro toner
    ativo desta cor na máquina, o conflito é resolvido automaticamente.
    """
    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute('SELECT maquina_id FROM toners_individual WHERE id=?', (toner_id,))
    row = cursor.fetchone()
    if row:
        maquina_id = row[0]
        # Verifica conflito: outro toner ativo da nova cor
        cursor.execute('''
            SELECT id FROM toners_individual
            WHERE maquina_id=? AND cor=? AND data_retirada IS NULL AND id!=?
            LIMIT 1
        ''', (maquina_id, cor, toner_id))
        conflito = cursor.fetchone()
        if conflito:
            cursor.execute('UPDATE toners_individual SET data_retirada=?, contador_final=? WHERE id=?',
                           (data_instalacao, contador_inicial, conflito[0]))

    cursor.execute('''
        UPDATE toners_individual
        SET cor=?, data_instalacao=?, data_retirada=?, contador_inicial=?, contador_final=?, custo=?
        WHERE id=?
    ''', (cor, data_instalacao, data_retirada, contador_inicial, contador_final, custo, toner_id))

    conn.commit(); conn.close()


def listar_toners_por_maquina(maquina_id: int, apenas_ativos: bool = False) -> List[Toner]:
    conn = get_conexao()
    cursor = conn.cursor()
    query = '''SELECT id, maquina_id, cor, data_instalacao, data_retirada,
                      contador_inicial, contador_final, custo, observacao, data_registro
               FROM toners_individual WHERE maquina_id=?'''
    if apenas_ativos:
        query += ' AND data_retirada IS NULL'
    query += ' ORDER BY cor, data_instalacao DESC'
    cursor.execute(query, (maquina_id,))
    toners = [Toner(id=r[0], maquina_id=r[1], cor=r[2], data_instalacao=r[3],
                    data_retirada=r[4] or "", contador_inicial=r[5],
                    contador_final=r[6] or 0, custo=r[7],
                    observacao=r[8] or "", data_registro=r[9])
              for r in cursor.fetchall()]
    conn.close()
    return toners


def get_toners_ativos_por_maquina(maquina_id: int) -> List[Toner]:
    return listar_toners_por_maquina(maquina_id, apenas_ativos=True)


def get_toner_atual_por_cor(maquina_id: int, cor: str) -> Optional[Toner]:
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute('''SELECT id, maquina_id, cor, data_instalacao, data_retirada,
                             contador_inicial, contador_final, custo, observacao, data_registro
                      FROM toners_individual
                      WHERE maquina_id=? AND cor=? AND data_retirada IS NULL
                      ORDER BY data_instalacao DESC LIMIT 1''', (maquina_id, cor))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Toner(id=row[0], maquina_id=row[1], cor=row[2], data_instalacao=row[3],
                     data_retirada=row[4] or "", contador_inicial=row[5],
                     contador_final=row[6] or 0, custo=row[7],
                     observacao=row[8] or "", data_registro=row[9])
    return None


def get_historico_por_cor(maquina_id: int, cor: str) -> List[Dict]:
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute('''SELECT data_instalacao, data_retirada, contador_inicial, contador_final, custo
                      FROM toners_individual
                      WHERE maquina_id=? AND cor=? AND data_retirada IS NOT NULL
                      ORDER BY data_instalacao''', (maquina_id, cor))
    historico = []
    for row in cursor.fetchall():
        total = row[3] - row[2] if row[3] else 0
        def fmt_data(d):
            if d and '-' in d:
                p = d.split('-')
                if len(p) == 3:
                    return f"{p[2]}/{p[1]}/{p[0]}"
            return d or ""
        historico.append({
            'data_instalacao': fmt_data(row[0]),
            'data_retirada': fmt_data(row[1]),
            'contador_inicial': row[2],
            'contador_final': row[3],
            'total_impressoes': total,
            'custo': row[4],
            'custo_pagina': row[4] / total if total > 0 else 0
        })
    conn.close()
    return historico


def get_ultimo_contador_por_maquina(maquina_id: int) -> int:
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute('''SELECT MAX(max_contador) FROM (
        SELECT MAX(contador_inicial) as max_contador FROM toners_individual WHERE maquina_id=?
        UNION
        SELECT MAX(contador_final) as max_contador FROM toners_individual WHERE maquina_id=? AND contador_final IS NOT NULL
    )''', (maquina_id, maquina_id))
    resultado = cursor.fetchone()
    if resultado and resultado[0]:
        ultimo = resultado[0]
    else:
        cursor.execute('SELECT contador_atual FROM maquinas WHERE id=?', (maquina_id,))
        r = cursor.fetchone()
        ultimo = r[0] if r else 0
    conn.close()
    return ultimo


def calcular_rendimento_por_cor(maquina_id: int = None, cor: str = None,
                                 data_inicio: str = None, data_fim: str = None) -> Dict[str, List[Rendimento]]:
    conn = get_conexao()
    cursor = conn.cursor()
    query = '''SELECT t.id, t.maquina_id, t.cor, t.data_instalacao, t.data_retirada,
                      t.contador_inicial, t.contador_final, t.custo, m.nome
               FROM toners_individual t
               JOIN maquinas m ON t.maquina_id = m.id
               WHERE t.data_retirada IS NOT NULL'''
    params = []
    if maquina_id:
        query += ' AND t.maquina_id=?'; params.append(maquina_id)
    if cor:
        query += ' AND t.cor=?'; params.append(cor)
    if data_inicio:
        query += ' AND t.data_retirada>=?'; params.append(data_inicio)
    if data_fim:
        query += ' AND t.data_retirada<=?'; params.append(data_fim)
    query += ' ORDER BY t.cor, t.data_retirada DESC'
    cursor.execute(query, params)
    resultado = {}
    for row in cursor.fetchall():
        cor_atual = row[2]
        total = row[6] - row[5] if row[6] else 0
        custo_pag = row[7] / total if total > 0 else 0
        r = Rendimento(cor=cor_atual, data_instalacao=row[3], data_retirada=row[4],
                       contador_inicial=row[5], contador_final=row[6], total_impressoes=total,
                       custo=row[7], custo_pagina=custo_pag, rendimento_abaixo=total < 14500,
                       maquina_nome=row[8], maquina_id=row[1])
        resultado.setdefault(cor_atual, []).append(r)
    conn.close()
    return resultado


def resumo_cores_maquina(maquina_id: int) -> Dict:
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute('''SELECT cor, COUNT(*) as total_toners,
                             AVG(contador_final-contador_inicial), SUM(contador_final-contador_inicial),
                             SUM(custo), MIN(contador_final-contador_inicial), MAX(contador_final-contador_inicial)
                      FROM toners_individual
                      WHERE maquina_id=? AND data_retirada IS NOT NULL
                      GROUP BY cor ORDER BY cor''', (maquina_id,))
    resumo = {}
    for row in cursor.fetchall():
        cor = row[0]
        resumo[cor] = {
            'total_toners': row[1], 'media_impressoes': round(row[2] or 0, 0),
            'total_impressoes': row[3] or 0, 'total_custo': row[4] or 0,
            'min_impressoes': row[5] or 0, 'max_impressoes': row[6] or 0,
            'custo_medio_toner': (row[4] or 0) / row[1] if row[1] > 0 else 0,
            'custo_por_pagina': (row[4] or 0) / (row[3] or 1) if row[3] else 0
        }
    conn.close()
    return resumo


def get_toner_atual_cores(maquina_id: int) -> Dict[str, Optional[Toner]]:
    resultado = {}
    for cor in ['Preto', 'Ciano', 'Magenta', 'Amarelo']:
        toner = get_toner_atual_por_cor(maquina_id, cor)
        if toner:
            resultado[cor] = toner
    return resultado


__all__ = [
    'listar_maquinas', 'salvar_maquina', 'deletar_maquina',
    'registrar_toner', 'finalizar_toner', 'editar_toner',
    'listar_toners_por_maquina', 'get_toners_ativos_por_maquina',
    'get_toner_atual_por_cor', 'get_toner_atual_cores',
    'get_historico_por_cor', 'get_ultimo_contador_por_maquina',
    'calcular_rendimento_por_cor', 'resumo_cores_maquina'
]


# ==================== CONTADORES SEMANAIS ====================

def registrar_contador(maquina_id: int, data: str, contador: int, observacao: str = "") -> int:
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contadores_semanais (maquina_id, data, contador, observacao) VALUES (?,?,?,?)",
        (maquina_id, data, contador, observacao)
    )
    # Atualiza contador_atual da máquina se for maior
    cursor.execute(
        "UPDATE maquinas SET contador_atual = MAX(contador_atual, ?) WHERE id = ?",
        (contador, maquina_id)
    )
    rid = cursor.lastrowid
    conn.commit()
    conn.close()
    return rid


def listar_contadores(maquina_id: int) -> list:
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, data, contador, observacao FROM contadores_semanais "
        "WHERE maquina_id=? ORDER BY data DESC, id DESC",
        (maquina_id,)
    )
    rows = [{"id": r[0], "data": r[1], "contador": r[2], "observacao": r[3] or ""}
            for r in cursor.fetchall()]
    conn.close()
    return rows


def deletar_contador(registro_id: int):
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contadores_semanais WHERE id=?", (registro_id,))
    conn.commit()
    conn.close()
