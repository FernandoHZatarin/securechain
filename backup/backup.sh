#!/bin/bash

# Script de Backup Seguro Automatizado (RF05)
# Deve ser executado no Linux (Debian 13)

# Diretórios baseados no local do script
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOC_DIR="$BASE_DIR/documentos"
BACKUP_DIR="$BASE_DIR/backup"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/backup.log"

# Garante que os diretórios existam
mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"

# Timestamp para o nome do arquivo (Formato: YYYYMMDD_HHMMSS)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TAR_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
ENC_FILE="${TAR_FILE}.enc"

# Senha da criptografia (Em um cenário real, usar variável de ambiente ou cofre de senhas)
SENHA_CRIPTOGRAFIA="SecureChain2026"

echo "--- Iniciando processo de backup ---"

# 1. Compactação dos documentos em arquivo .tar.gz
# Entramos no BASE_DIR para que no tar o caminho fique apenas "documentos/..."
echo "Compactando a pasta de documentos..."
if tar -czf "$TAR_FILE" -C "$BASE_DIR" "documentos"; then
    echo "[OK] Compactação concluída: $TAR_FILE"
else
    STATUS="FALHA na compactação"
    echo "$(date +"%Y-%m-%d %H:%M:%S") | 0 bytes | $STATUS | N/A" >> "$LOG_FILE"
    echo "[ERRO] Falha na compactação. Abortando."
    exit 1
fi

# 2. Aplicação de criptografia simétrica ao arquivo compactado (AES-256-CBC via openssl)
# A flag -pbkdf2 é o padrão moderno de derivação de chave do openssl
echo "Criptografando o backup com AES-256..."
if openssl enc -aes-256-cbc -salt -pbkdf2 -in "$TAR_FILE" -out "$ENC_FILE" -pass pass:"$SENHA_CRIPTOGRAFIA"; then
    echo "[OK] Criptografia concluída: $ENC_FILE"
    
    # Remove o arquivo .tar.gz original que está sem criptografia por segurança
    rm "$TAR_FILE"
else
    STATUS="FALHA na criptografia"
    echo "$(date +"%Y-%m-%d %H:%M:%S") | 0 bytes | $STATUS | $TAR_FILE" >> "$LOG_FILE"
    echo "[ERRO] Falha na criptografia. Abortando."
    exit 1
fi

# Pega o tamanho do arquivo final criptografado (compatível com Linux GNU stat)
TAMANHO=$(stat -c%s "$ENC_FILE" 2>/dev/null || stat -f%z "$ENC_FILE")
STATUS="SUCESSO"

# 3. Log local com data, tamanho do arquivo e status da operação
echo "$(date +"%Y-%m-%d %H:%M:%S") | $TAMANHO bytes | $STATUS | $(basename "$ENC_FILE")" >> "$LOG_FILE"
echo "[OK] Log local atualizado em: $LOG_FILE"

# 4. Registro do evento de backup na blockchain
# Usando python3 para invocar a função registrar_evento do módulo blockchain.py
echo "Registrando evento na blockchain..."
python3 -c "
import sys
import os
sys.path.append(os.path.abspath('$BASE_DIR'))
from blockchain.blockchain import registrar_evento

evento = f'Backup executado com SUCESSO: {os.path.basename(\"$ENC_FILE\")} ({$TAMANHO} bytes)'
registrar_evento(evento)
"

if [ $? -eq 0 ]; then
    echo "[OK] Evento registrado na blockchain com sucesso."
else
    echo "[AVISO] Falha ao registrar evento na blockchain."
fi

echo "--- Processo de backup finalizado com segurança ---"
