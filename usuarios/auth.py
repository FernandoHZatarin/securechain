"""
Cadastro e Login autentificado de usuários e controle de registro de acessos na blockchain
"""

import json
import os
import sys
from datetime import datetime, timezone

try:
    import bcrypt
except ImportError:
    print("Biblioteca bcrypt nao encontrada. Instale com: pip3 install bcrypt --break-system-packages")
    sys.exit(1)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blockchain.blockchain import registrar_evento

ARQUIVO_USUARIOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "usuarios", "usuarios.json")
PERFIS_VALIDOS = ["admin", "analista", "visitante"]


def _carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return {}
    with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar_usuarios(usuarios):
    os.makedirs(os.path.dirname(ARQUIVO_USUARIOS), exist_ok=True)
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=2, ensure_ascii=False)


def cadastrar_usuario(nome_usuario, senha, perfil):
    """
    Cadastra um novo usuario com senha protegida (admin, analista, visitante)
    """
    if perfil not in PERFIS_VALIDOS:
        raise ValueError(f"Perfil invalido. Use um de: {PERFIS_VALIDOS}")

    usuarios = _carregar_usuarios()

    if nome_usuario in usuarios:
        raise ValueError(f"Usuario '{nome_usuario}' ja existe.")

    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

    usuarios[nome_usuario] = {
        "senha_hash": senha_hash.decode("utf-8"),
        "perfil": perfil,
        "criado_em": datetime.now(timezone.utc).isoformat(),
    }
    _salvar_usuarios(usuarios)

    registrar_evento(f"Usuario criado: {nome_usuario} (perfil={perfil})")
    print(f"Usuario '{nome_usuario}' cadastrado com sucesso (perfil: {perfil}).")
    return True


def remover_usuario(nome_usuario):
    usuarios = _carregar_usuarios()
    if nome_usuario not in usuarios:
        raise ValueError(f"Usuario '{nome_usuario}' nao encontrado.")

    del usuarios[nome_usuario]
    _salvar_usuarios(usuarios)
    registrar_evento(f"Usuario removido: {nome_usuario}")
    print(f"Usuario '{nome_usuario}' removido.")


def login(nome_usuario, senha):
    """
    Verifica as credenciais do usuario e registra.
    """
    usuarios = _carregar_usuarios()

    if nome_usuario not in usuarios:
        registrar_evento(f"Tentativa de acesso negada: usuario inexistente ({nome_usuario})")
        print("Usuario ou senha invalidos.")
        return None

    senha_hash_armazenado = usuarios[nome_usuario]["senha_hash"].encode("utf-8")

    if bcrypt.checkpw(senha.encode("utf-8"), senha_hash_armazenado):
        perfil = usuarios[nome_usuario]["perfil"]
        registrar_evento(f"Login realizado: usuario={nome_usuario} perfil={perfil}")
        print(f"Login bem-sucedido. Bem-vindo, {nome_usuario} (perfil: {perfil}).")
        return perfil
    else:
        registrar_evento(f"Tentativa de acesso negada: senha incorreta para usuario {nome_usuario}")
        print("Usuario ou senha invalidos.")
        return None


def listar_usuarios():
    usuarios = _carregar_usuarios()
    for nome, dados in usuarios.items():
        print(f"  {nome} - perfil: {dados['perfil']} - criado em: {dados['criado_em']}")
    return list(usuarios.keys())


def menu_interativo():
    while True:
        print("\n--- SecureChain Audit - Autenticacao ---")
        print("1. Cadastrar usuario")
        print("2. Fazer login")
        print("3. Listar usuarios")
        print("4. Remover usuario")
        print("0. Sair")
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            nome = input("Nome de usuario: ").strip()
            senha = input("Senha: ").strip()
            print(f"Perfis disponiveis: {PERFIS_VALIDOS}")
            perfil = input("Perfil: ").strip()
            try:
                cadastrar_usuario(nome, senha, perfil)
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "2":
            nome = input("Nome de usuario: ").strip()
            senha = input("Senha: ").strip()
            login(nome, senha)

        elif opcao == "3":
            print("Usuarios cadastrados:")
            listar_usuarios()

        elif opcao == "4":
            nome = input("Nome de usuario a remover: ").strip()
            try:
                remover_usuario(nome)
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "0":
            print("Saindo...")
            break

        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    menu_interativo()
