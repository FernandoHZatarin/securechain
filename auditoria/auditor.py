"""
Script de auditoria do sistema operacional (RF06).
Coleta dados sobre conexões, logins, portas e rede e salva em relatório.
"""

import os
import subprocess
import sys
from datetime import datetime

# Adicionar o diretório pai ao sys.path para importar a blockchain
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blockchain.blockchain import registrar_evento

DIRETORIO_RELATORIOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relatorios")

def executar_comando(comando_lista, descricao):
    """Executa um comando no sistema operacional e retorna sua saída."""
    comando_str = " ".join(comando_lista)
    resultado = f"--- {descricao} ({comando_str}) ---\n"
    try:
        processo = subprocess.run(comando_lista, capture_output=True, text=True)
        resultado += processo.stdout if processo.stdout else "Nenhuma saída.\n"
        if processo.stderr:
            resultado += f"\nErros:\n{processo.stderr}"
    except FileNotFoundError:
        resultado += f"Comando não encontrado no sistema: {comando_str}\n"
    except Exception as e:
        resultado += f"Falha ao executar comando: {e}\n"
    resultado += "\n" + "="*50 + "\n\n"
    return resultado

def gerar_relatorio_auditoria():
    """Coleta as informações do sistema e gera o relatório datado."""
    if not os.path.exists(DIRETORIO_RELATORIOS):
        os.makedirs(DIRETORIO_RELATORIOS)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"auditoria_SO_{timestamp}.txt"
    caminho_arquivo = os.path.join(DIRETORIO_RELATORIOS, nome_arquivo)

    print("Iniciando coleta de dados do sistema operacional...")

    conteudo_relatorio = f"Relatório de Auditoria do SO\nGerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    conteudo_relatorio += "=" * 70 + "\n\n"

    # Comandos exigidos pelo RF06
    comandos = [
        (["who"], "Usuários atualmente conectados"),
        (["last"], "Histórico de logins"),
        (["ss", "-tulpn"], "Portas e serviços em escuta"),
        (["ip", "a"], "Interfaces de rede e endereços IP")
    ]

    for comando, descricao in comandos:
        print(f"Executando: {' '.join(comando)}...")
        conteudo_relatorio += executar_comando(comando, descricao)

    # Escreve o resultado no arquivo dentro de auditoria/relatorios/
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo_relatorio)

    print(f"\nRelatório gerado com sucesso em: {caminho_arquivo}")

    # Registra o evento na blockchain
    registrar_evento(f"Auditoria do SO executada. Relatorio gerado: {nome_arquivo}")

if __name__ == "__main__":
    gerar_relatorio_auditoria()
