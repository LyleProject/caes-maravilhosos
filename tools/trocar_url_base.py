#!/usr/bin/env python3
"""
Troca a URL base do site em todos os arquivos (canonical, Open Graph, schema.org,
sitemap.xml, robots.txt e a página 404).

Uso:
    python3 tools/trocar_url_base.py https://usuario.github.io/nome-do-repo/
    python3 tools/trocar_url_base.py https://www.caesmaravilhosos.com/

A URL atual fica guardada em tools/site-config.json (o único lugar a consultar).
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "tools" / "site-config.json"


def main():
    if len(sys.argv) != 2 or not sys.argv[1].startswith(("http://", "https://")):
        print(__doc__)
        sys.exit(1)
    nova = sys.argv[1].strip()
    if not nova.endswith("/"):
        nova += "/"
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    antiga = config["url_base"]
    if antiga == nova:
        print("A URL já é", nova)
        return

    arquivos = list(RAIZ.glob("*.html")) + [RAIZ / "sitemap.xml", RAIZ / "robots.txt"]
    total = 0
    for arquivo in arquivos:
        texto = arquivo.read_text(encoding="utf-8")
        n = texto.count(antiga)
        if n:
            arquivo.write_text(texto.replace(antiga, nova), encoding="utf-8")
            total += n
            print(f"{arquivo.name}: {n} ocorrência(s)")

    config["url_base"] = nova
    CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nPronto: {antiga} -> {nova} ({total} substituições)")


if __name__ == "__main__":
    main()
