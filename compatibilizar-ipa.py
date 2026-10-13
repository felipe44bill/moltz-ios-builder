"""Reempacota IPA sem assinatura com plists XML armazenados sem compressão."""
import copy
import hashlib
from pathlib import Path
import plistlib
import stat
import sys
import zipfile

origem, destino = map(Path, sys.argv[1:])
if origem.resolve() == destino.resolve():
    raise SystemExit('Use outro nome para preservar o IPA anterior.')
raiz = 'Payload/Moltz.app/'
alterados = []
with zipfile.ZipFile(origem) as entrada, zipfile.ZipFile(destino, 'w', compression=zipfile.ZIP_DEFLATED) as saida:
    for original in entrada.infolist():
        info = copy.copy(original)
        dados = entrada.read(original)
        # Assinaturas antigas selam a representação anterior dos plists.
        # O pacote de saída será assinado novamente pelo Sideloadly.
        if '/_CodeSignature/' in info.filename or info.filename.endswith('/embedded.mobileprovision'):
            continue
        if info.filename.endswith('Info.plist'):
            dados = plistlib.dumps(plistlib.loads(dados), fmt=plistlib.FMT_XML, sort_keys=False)
            info.compress_type = zipfile.ZIP_STORED
            alterados.append(info.filename)
        info.create_system = 3
        if info.is_dir():
            info.external_attr = (stat.S_IFDIR | 0o755) << 16 | 0x10
        else:
            executavel = bool((original.external_attr >> 16) & 0o111)
            info.external_attr = (stat.S_IFREG | (0o755 if executavel else 0o644)) << 16
        info.extra = b''
        saida.writestr(info, dados)

with zipfile.ZipFile(origem) as anterior, zipfile.ZipFile(destino) as novo:
    if novo.testzip():
        raise SystemExit('IPA corrompido.')
    for info in novo.infolist():
        if info.filename.endswith('Info.plist'):
            plist = plistlib.loads(novo.read(info))
            if info.compress_type != zipfile.ZIP_STORED:
                raise SystemExit('Plist foi comprimido indevidamente.')
            if info.filename == raiz + 'Info.plist' and plist.get('CFBundleIdentifier') != 'com.moltz.corridaeletrica':
                raise SystemExit('Identificador incorreto.')
        else:
            # Conteúdo executável, texturas, cenas e sons não podem mudar.
            if hashlib.sha256(anterior.read(info.filename)).digest() != hashlib.sha256(novo.read(info.filename)).digest():
                raise SystemExit('Conteúdo do jogo mudou: ' + info.filename)
print(f'IPA compatibilizado: {destino}; {len(alterados)} plists XML sem compressão; restante do jogo preservado.')
