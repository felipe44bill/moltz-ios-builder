"""Compila em Mac, mantendo código e logs detalhados fora do log público."""
from pathlib import Path
import subprocess
import sys
import zipfile
from seal import processar

projeto = Path(sys.argv[1]).resolve()
saida = Path(sys.argv[2]).resolve()
saida.mkdir(parents=True, exist_ok=True)
with (saida / "execucao.log").open("w") as registro:
    resultado = subprocess.run(["bash", "gerar-ipa-mac.sh", str(projeto), str(saida)],
                               stdout=registro, stderr=subprocess.STDOUT)
with zipfile.ZipFile("resultado.zip", "w", zipfile.ZIP_DEFLATED) as pacote:
    for arquivo in sorted(saida.rglob("*")):
        if arquivo.is_file():
            pacote.write(arquivo, arquivo.relative_to(saida).as_posix())
processar("encrypt", "resultado.zip", "resultado.aes")
print("Compilação concluída; resultado e logs criptografados. Código:", resultado.returncode)
raise SystemExit(resultado.returncode)
