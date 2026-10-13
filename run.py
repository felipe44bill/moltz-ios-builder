"""Compila em Mac, mantendo código e logs detalhados fora do log público."""
from pathlib import Path
import subprocess
import sys
import time
import zipfile
from seal import processar

projeto = Path(sys.argv[1]).resolve()
saida = Path(sys.argv[2]).resolve()
saida.mkdir(parents=True, exist_ok=True)
with (saida / "execucao.log").open("w") as registro:
    processo = subprocess.Popen(["bash", "gerar-ipa-mac.sh", str(projeto), str(saida)],
                                stdout=registro, stderr=subprocess.STDOUT)
    inicio = time.monotonic()
    while True:
        try:
            codigo = processo.wait(timeout=45)
            break
        except subprocess.TimeoutExpired:
            print(f"Compilação nativa em andamento ({int(time.monotonic() - inicio)} s).", flush=True)
with zipfile.ZipFile("resultado.zip", "w", zipfile.ZIP_DEFLATED) as pacote:
    for arquivo in sorted(saida.rglob("*")):
        if arquivo.is_file():
            pacote.write(arquivo, arquivo.relative_to(saida).as_posix())
processar("encrypt", "resultado.zip", "resultado.aes")
print("Compilação concluída; resultado e logs criptografados. Código:", codigo)
raise SystemExit(codigo)
