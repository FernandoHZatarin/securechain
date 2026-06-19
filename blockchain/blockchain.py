"""
Cria uma blockchain
"""

import hashlib
import json
import os
from datetime import datetime, timezone

CHAIN_FILE = os.path.join(os.path.dirname(__file__), "chain.json")


class Bloco:
    def __init__(self, id_bloco, evento, hash_anterior, timestamp=None):
        self.id = id_bloco
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.evento = evento
        self.hash_anterior = hash_anterior
        self.hash_atual = self.calcular_hash()

    def calcular_hash(self):
        conteudo = f"{self.id}{self.timestamp}{self.evento}{self.hash_anterior}"
        return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "evento": self.evento,
            "hash_anterior": self.hash_anterior,
            "hash_atual": self.hash_atual,
        }

    @staticmethod
    def from_dict(data):
        bloco = Bloco(
            id_bloco=data["id"],
            evento=data["evento"],
            hash_anterior=data["hash_anterior"],
            timestamp=data["timestamp"],
        )
        bloco.hash_atual = data["hash_atual"]
        return bloco


class Blockchain:
    def __init__(self, caminho_arquivo=CHAIN_FILE):
        self.caminho_arquivo = caminho_arquivo
        self.cadeia = []
        self._carregar_ou_criar_genesis()

    def _carregar_ou_criar_genesis(self):
        if os.path.exists(self.caminho_arquivo) and os.path.getsize(self.caminho_arquivo) > 0:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.cadeia = [Bloco.from_dict(b) for b in dados]

        if not self.cadeia:
            genesis = Bloco(
                id_bloco=0,
                evento="Bloco genese - inicializacao da blockchain",
                hash_anterior="0" * 64
            )
            self.cadeia = [genesis]
            self._salvar()

    def _salvar(self):
        with open(self.caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(
                [b.to_dict() for b in self.cadeia],
                f,
                indent=2,
                ensure_ascii=False
            )

    def adicionar_bloco(self, evento):
        ultimo_bloco = self.cadeia[-1]
        novo_id = ultimo_bloco.id + 1

        novo_bloco = Bloco(
            id_bloco=novo_id,
            evento=evento,
            hash_anterior=ultimo_bloco.hash_atual
        )

        self.cadeia.append(novo_bloco)
        self._salvar()
        return novo_bloco

    def imprimir_cadeia(self):
        for bloco in self.cadeia:
            print(json.dumps(bloco.to_dict(), indent=2, ensure_ascii=False))
            print("-" * 60)


def registrar_evento(evento):
    bc = Blockchain()
    return bc.adicionar_bloco(evento)


if __name__ == "__main__":
    bc = Blockchain()
    bc.adicionar_bloco("Teste manual de execucao do modulo blockchain.py")

    print(f"Total de blocos na cadeia: {len(bc.cadeia)}")
    bc.imprimir_cadeia()
