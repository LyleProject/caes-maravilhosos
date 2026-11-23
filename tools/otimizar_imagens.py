#!/usr/bin/env python3
"""
Gera as imagens otimizadas do site a partir das fotos originais.

Uso:
    python3 tools/otimizar_imagens.py /caminho/para/KIT_Caes_Maravilhosos

Para cada foto gera WebP + JPG nas larguras 480, 960 e 1600 px (sem ampliar:
se a original for menor, a maior versão fica com a largura original) em
assets/img/. Também gera o logo com fundo transparente, os favicons, a imagem
de compartilhamento (Open Graph) e o arquivo tools/imagens.json com as
larguras e proporções de cada foto.

Requer: Python 3.9+ e Pillow (pip install Pillow numpy)
"""
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "assets" / "img"
LARGURAS = (480, 960, 1600)
QUALIDADE_WEBP = 72
QUALIDADE_JPG = 74
QUALIDADE_MINIMA = 50
# Orçamento de peso por largura (fotos com muita textura, como grama, ganham
# compressão um pouco maior até caber no orçamento, sem passar da qualidade mínima)
ORCAMENTO_KB = {480: 48, 960: 135, 1600: 300}

# (arquivo dentro de FOTOS/, nome final, recorte opcional (esq, topo, dir, base))
FOTOS = [
    ("01_hotel_area-externa_e_piscina/01_HERO-sugerido_casa-gramado-caes.jpg", "hotel-casa-gramado-caes", None),
    ("01_hotel_area-externa_e_piscina/02_piscina-gramado-caes.jpg", "piscina-gramado-caes", None),
    ("01_hotel_area-externa_e_piscina/04_piscina-caes-ao-sol.jpg", "piscina-caes-ao-sol", None),
    ("01_hotel_area-externa_e_piscina/05_deck-piscina-caes.jpg", "deck-piscina-caes", None),
    ("01_hotel_area-externa_e_piscina/06_border-collie-na-piscina.jpg", "border-collie-piscina", None),
    ("01_hotel_area-externa_e_piscina/07_shiba-na-piscina.jpg", "shiba-beira-piscina", None),
    ("01_hotel_area-externa_e_piscina/08_caes-brincando-na-arvore.jpg", "caes-brincando-arvore", None),
    ("01_hotel_area-externa_e_piscina/09_golden-e-amigos-com-bola.jpg", "golden-amigos-bola", None),
    ("01_hotel_area-externa_e_piscina/10_shibas-brincando-gramado.jpg", "shibas-brincando-gramado", None),
    ("01_hotel_area-externa_e_piscina/11_caes-brincando-gramado.jpg", "caes-brincando-gramado", None),
    ("01_hotel_area-externa_e_piscina/12_caes-socializando-gramado.jpg", "caes-socializando-gramado", None),
    ("01_hotel_area-externa_e_piscina/13_shiba-na-varanda.jpg", "shiba-varanda", None),
    # recorte remove a marca d'água do celular no canto inferior
    ("01_hotel_area-externa_e_piscina/14_gramado-VERTICAL-celular.jpg", "gramado-vertical", (0, 0, 738, 1500)),
    ("02_retratos_de_caes/01_shiba-preto-sorrindo.jpg", "retrato-shiba-preto", None),
    ("02_retratos_de_caes/02_shiba-caramelo.jpg", "retrato-shiba-caramelo", None),
    ("02_retratos_de_caes/03_dois-goldens.jpg", "retrato-dois-goldens", None),
    ("02_retratos_de_caes/04_husky-olhos-azuis.jpg", "retrato-husky", None),
    ("02_retratos_de_caes/05_border-collie.jpg", "retrato-border-collie", None),
    ("03_aconchego_lareira/01_maltes-na-lareira.jpg", "lareira-maltes", None),
    ("03_aconchego_lareira/02_caes-na-manta.jpg", "aconchego-manta", None),
    ("03_aconchego_lareira/03_labradores-na-lareira.jpg", "lareira-labradores", None),
    ("03_aconchego_lareira/04_caes-no-sofa.jpg", "aconchego-sofa", None),
    ("03_aconchego_lareira/05_cavalier-descansando.jpg", "aconchego-cavalier", None),
    ("04_daycare_creche/01_cao-no-playground.jpg", "daycare-playground", None),
    ("04_daycare_creche/02_cao-feliz-playground.jpg", "daycare-playground-feliz", None),
    ("04_daycare_creche/03_buldogues.jpg", "daycare-buldogues", None),
    ("04_daycare_creche/04_amigos-beagle-buldogue.jpg", "daycare-beagle-buldogue", None),
    ("04_daycare_creche/05_carinho-da-equipe.jpg", "daycare-carinho-equipe", None),
    ("04_daycare_creche/06_cao-de-bandana.jpg", "daycare-bandana", None),
    ("04_daycare_creche/07_hidratacao-1.jpg", "daycare-hidratacao-1", None),
    ("04_daycare_creche/08_hidratacao-2.jpg", "daycare-hidratacao-2", None),
    ("04_daycare_creche/09_hidratacao-3.jpg", "daycare-hidratacao-3", None),
    ("04_daycare_creche/10_cineminha-sensorial.jpg", "daycare-cineminha", None),
    ("05_dono_andre/01_andre-com-seus-caes.jpg", "andre-com-caes", None),
]

LOGO = "IDENTIDADE_VISUAL/logo_recortado_do-post_(pedir-original-ao-cliente).png"
SELO = "IDENTIDADE_VISUAL/selo_premio-melhores-do-ano_foto-perfil-instagram_150px.jpg"
CREME = (254, 253, 235)

# Pata do logo (mesmas formas do favicon.svg, em grade 64x64):
# (cx, cy, rx, ry, rotação em graus, cor, opacidade)
PATA = [
    (12.5, 22, 6, 7.2, 0, "#F5BB2E", 1),
    (25, 11.5, 8.4, 9.6, -14, "#178FE8", 1),
    (44, 12, 8.4, 10.4, 12, "#FDE511", 1),
    (55, 29.5, 6.4, 7.6, 10, "#178FE8", 1),
    (43, 41, 9.5, 12, -32, "#FDE511", 1),
    (36, 42.5, 11.5, 13.5, -38, "#F5BB2E", 1),
    (24.5, 35, 13, 9.4, -20, "#015655", 0.93),
]


def larguras_para(largura_original):
    alvo = [w for w in LARGURAS if w < largura_original]
    alvo.append(min(largura_original, LARGURAS[-1]))
    return sorted(set(alvo))


def salvar_no_orcamento(img, destino, largura, formato, qualidade):
    """Salva dentro do orçamento de peso. Primeiro reduz a qualidade (até 56);
    se ainda passar, aplica uma suavização bem leve no ruído e tenta de novo."""
    limite = ORCAMENTO_KB.get(min(ORCAMENTO_KB, key=lambda k: abs(k - largura))) * 1024
    if formato == "JPEG":
        limite = int(limite * 1.25)

    def codificar(imagem, q):
        buf = io.BytesIO()
        if formato == "WEBP":
            imagem.save(buf, "WEBP", quality=q, method=6)
        else:
            imagem.save(buf, "JPEG", quality=q, optimize=True, progressive=True, subsampling="4:2:0")
        return buf

    tentativas = [(img, q) for q in range(qualidade, 55, -4)]
    suave = img.filter(ImageFilter.GaussianBlur(0.55))
    tentativas += [(suave, q) for q in range(68, QUALIDADE_MINIMA - 1, -4)]
    for imagem, q in tentativas:
        buf = codificar(imagem, q)
        if buf.tell() <= limite:
            break
    destino.write_bytes(buf.getvalue())


def salvar_versoes(img, nome):
    img = ImageOps.exif_transpose(img).convert("RGB")
    w0, h0 = img.size
    feitas = []
    for w in larguras_para(w0):
        h = round(h0 * w / w0)
        v = img if w == w0 else img.resize((w, h), Image.LANCZOS)
        salvar_no_orcamento(v, SAIDA / f"{nome}-{w}.webp", w, "WEBP", QUALIDADE_WEBP)
        salvar_no_orcamento(v, SAIDA / f"{nome}-{w}.jpg", w, "JPEG", QUALIDADE_JPG)
        feitas.append(w)
    return {"larguras": feitas, "proporcao": [w0, h0]}


def remover_fundo(img):
    """Remove o fundo creme do logo, com borda suave."""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    borda = np.concatenate([a[:6].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    fundo = np.median(borda, axis=0)
    dist = np.sqrt(((a - fundo) ** 2).sum(axis=2))
    alfa = np.clip((dist - 18) / (70 - 18), 0, 1)[..., None]
    cor = np.where(alfa > 0.02, (a - (1 - alfa) * fundo) / np.maximum(alfa, 1e-3), a)
    cor[alfa[..., 0] <= 0.02] = 0  # pixels invisíveis sem ruído (arquivo menor)
    rgba = np.dstack([np.clip(cor, 0, 255), alfa[..., 0] * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def desenhar_pata(tamanho, fundo=None, margem=0.0):
    escala_ss = 8
    S = tamanho * escala_ss
    base = Image.new("RGBA", (S, S), fundo + (255,) if fundo else (0, 0, 0, 0))
    util = S * (1 - 2 * margem)
    k = util / 64
    off = S * margem
    for cx, cy, rx, ry, ang, cor, op in PATA:
        camada = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(camada)
        x, y = off + cx * k, off + cy * k
        rgb = tuple(int(cor[i:i + 2], 16) for i in (1, 3, 5))
        d.ellipse((x - rx * k, y - ry * k, x + rx * k, y + ry * k), fill=rgb + (round(255 * op),))
        if ang:
            camada = camada.rotate(-ang, resample=Image.BICUBIC, center=(x, y))
        base = Image.alpha_composite(base, camada)
    return base.resize((tamanho, tamanho), Image.LANCZOS)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    kit = Path(sys.argv[1]).expanduser().resolve()
    fotos = kit / "FOTOS"
    SAIDA.mkdir(parents=True, exist_ok=True)
    manifesto = {}

    for arquivo, nome, recorte in FOTOS:
        img = Image.open(fotos / arquivo)
        if recorte:
            img = img.crop(recorte)
        manifesto[nome] = salvar_versoes(img, nome)
        print(f"ok  {nome}  {manifesto[nome]['larguras']}")

    # Logo com fundo transparente (recorta um resíduo no canto inferior)
    logo = remover_fundo(Image.open(kit / LOGO))
    logo = logo.crop((6, 4, 546, 268))
    logo = logo.crop(logo.getbbox())
    # 440 px de largura: nítido em telas retina até ~220 px de exibição
    lw = 440
    logo_web = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    logo_web.quantize(256, method=Image.Quantize.FASTOCTREE).save(SAIDA / "logo-caes-maravilhosos.png", optimize=True)
    manifesto["logo"] = {"proporcao": list(logo_web.size)}

    # Selo do prêmio (arquivo original pequeno, mantido no tamanho real)
    selo = Image.open(kit / SELO).convert("RGB")
    selo.save(SAIDA / "selo-premio.webp", "WEBP", quality=88, method=6)
    selo.save(SAIDA / "selo-premio.jpg", "JPEG", quality=88, optimize=True)

    # Favicons a partir da pata do logo
    desenhar_pata(32).save(SAIDA / "favicon-32.png", optimize=True)
    desenhar_pata(192, margem=0.04).save(SAIDA / "favicon-192.png", optimize=True)
    desenhar_pata(180, fundo=CREME, margem=0.12).convert("RGB").save(SAIDA / "apple-touch-icon.png", optimize=True)
    ico = desenhar_pata(256)
    ico.save(RAIZ / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    # Imagem de compartilhamento 1200x630 (WhatsApp, Facebook, etc.)
    hero = ImageOps.fit(Image.open(fotos / FOTOS[0][0]).convert("RGB"), (1200, 630), Image.LANCZOS, centering=(0.5, 0.62))
    lw = 400
    lg = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    pad = 26
    caixa = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(caixa).rounded_rectangle((0, 0, caixa.width - 1, caixa.height - 1), radius=34, fill=CREME + (255,))
    caixa.alpha_composite(lg, (pad, pad))
    sombra = Image.new("RGBA", caixa.size, (2, 76, 101, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((0, 0, caixa.width - 1, caixa.height - 1), radius=34, fill=(2, 76, 101, 110))
    sombra = sombra.filter(ImageFilter.GaussianBlur(14))
    og = hero.convert("RGBA")
    og.alpha_composite(sombra, (40, 630 - caixa.height - 30))
    og.alpha_composite(caixa, (40, 630 - caixa.height - 40))
    og.convert("RGB").save(SAIDA / "og-caes-maravilhosos.jpg", "JPEG", quality=82, optimize=True, progressive=True)

    (RAIZ / "tools" / "imagens.json").write_text(json.dumps(manifesto, indent=1), encoding="utf-8")
    print("Pronto:", len(manifesto), "itens em", SAIDA)


if __name__ == "__main__":
    main()
