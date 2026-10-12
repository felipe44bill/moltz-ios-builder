"""Transporte autenticado de arquivos de build usando AES-256-GCM."""
import os
from pathlib import Path
import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"MOLTZAE1"

def processar(modo, origem, destino):
    cipher = AESGCM(bytes.fromhex(os.environ["IOS_BUILD_KEY"]))
    dados = Path(origem).read_bytes()
    if modo == "encrypt":
        nonce = os.urandom(12)
        resultado = MAGIC + nonce + cipher.encrypt(nonce, dados, MAGIC)
    elif modo == "decrypt":
        if dados[:8] != MAGIC:
            raise ValueError("Cabeçalho inválido")
        resultado = cipher.decrypt(dados[8:20], dados[20:], MAGIC)
    else:
        raise ValueError("Modo inválido")
    Path(destino).write_bytes(resultado)

if __name__ == "__main__":
    processar(*sys.argv[1:])
