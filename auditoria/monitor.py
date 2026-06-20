"""
Monitora de Integridade de Arquivos e calcula hasshes
"""

import hashlib
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blockchain.blockchain import registrar_evento

DIRETORIO_MONITORADO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "documentos")
ARQUIVO_REFERENCIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hashes_referencia.json")


def calcular_hash_arquivo(caminho):
    """Calcula o hash SHA-256 do conteudo de um arquivo."""
    sha256 = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(4096), b""):
            sha256.update(bloco)
    return sha256.hexdigest()


def listar_arquivos_monitorados():
    """Retorna um dicionario {nome_arquivo: hash} de todos os arquivos no diretorio monitorado."""
    if not os.path.exists(DIRETORIO_MONITORADO):
        os.makedirs(DIRETORIO_MONITORADO)

    hashes = {}
    for nome_arquivo in os.listdir(DIRETORIO_MONITORADO):
        caminho_completo = os.path.join(DIRETORIO_MONITORADO, nome_arquivo)
        if os.path.isfile(caminho_completo):
            hashes[nome_arquivo] = calcular_hash_arquivo(caminho_completo)
    return hashes


def inicializar_referencia():
    """
    Calcula os hashes de todos os arquivos atuais e salva
    """
    hashes_atuais = listar_arquivos_monitorados()
    with open(ARQUIVO_REFERENCIA, "w", encoding="utf-8") as f:
        json.dump(hashes_atuais, f, indent=2, ensure_ascii=False)

    registrar_evento(f"Monitoramento de integridade inicializado com {len(hashes_atuais)} arquivo(s) de referencia")
    print(f"Referencia inicializada com {len(hashes_atuais)} arquivo(s).")
    return hashes_atuais


def carregar_referencia():
    """Carrega os hashes de referencia salvos"""
    if not os.path.exists(ARQUIVO_REFERENCIA):
        return inicializar_referencia()

    with open(ARQUIVO_REFERENCIA, "r", encoding="utf-8") as f:
        return json.load(f)


def verificar_integridade():
    """
    Detecta e registra na blockchain: alteracao, exclusao e inclusao dos arqiuvos.
    """
    referencia = carregar_referencia()
    atuais = listar_arquivos_monitorados()
    alertas = []

    for nome_arquivo, hash_referencia in referencia.items():
        if nome_arquivo not in atuais:
            alerta = f"ALERTA: arquivo excluido - {nome_arquivo}"
            alertas.append(alerta)
            registrar_evento(f"Integridade: arquivo excluido detectado - {nome_arquivo}")
        elif atuais[nome_arquivo] != hash_referencia:
            alerta = f"ALERTA: arquivo alterado - {nome_arquivo}"
            alertas.append(alerta)
            registrar_evento(f"Integridade: alteracao detectada no arquivo - {nome_arquivo}")

    for nome_arquivo in atuais:
        if nome_arquivo not in referencia:
            alerta = f"ALERTA: novo arquivo incluido - {nome_arquivo}"
            alertas.append(alerta)
            registrar_evento(f"Integridade: novo arquivo incluido - {nome_arquivo}")

    with open(ARQUIVO_REFERENCIA, "w", encoding="utf-8") as f:
        json.dump(atuais, f, indent=2, ensure_ascii=False)

    return alertas


if __name__ == "__main__":
    print(f"Diretorio monitorado: {DIRETORIO_MONITORADO}")
    print("Verificando integridade dos arquivos...\n")

    alertas = verificar_integridade()

    if alertas:
        print(f"{len(alertas)} alerta(s) encontrado(s):")
        for a in alertas:
            print(f"  {a}")
    else:
        print("Nenhuma alteracao detectada. Todos os arquivos estao integros.")
