# Cães Maravilhosos – Hotel e Resort para Cães

Site institucional (Cotia/SP) feito em HTML, CSS e JavaScript puros: não precisa de build nem de servidor especial.

Páginas: `index.html` (Início), `hospedagem.html`, `daycare.html`, `adestramento.html`, `sobre.html`, `galeria.html`, `contato.html` e `404.html`.

## Publicar no GitHub Pages

1. No GitHub, crie um repositório **público** chamado `caes-maravilhosos` (sem README).
2. Dentro desta pasta, rode:

   ```bash
   git init
   git add .
   git commit -m "Site Cães Maravilhosos"
   git branch -M main
   git remote add origin https://github.com/LyleProject/caes-maravilhosos.git
   git push -u origin main
   ```

3. No repositório: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / `(root)` → Save**.
4. Em 1 a 2 minutos o site fica no ar em `https://lyleproject.github.io/caes-maravilhosos/`.

## Trocar o endereço do site

A URL base (usada em canonical, Open Graph, schema.org, sitemap e robots) fica em `tools/site-config.json` e já está configurada para `https://lyleproject.github.io/caes-maravilhosos/`.
Se publicar com outro usuário, outro nome de repositório ou um domínio próprio, rode antes do `git add`:

```bash
python3 tools/trocar_url_base.py https://NOVO-ENDERECO/
```

## Testar no computador

```bash
python3 -m http.server 8000
```

Depois abra `http://localhost:8000`.

## Imagens

As fotos otimizadas (WebP + JPG em 480, 960 e 1600 px) ficam em `assets/img/`. Para gerar de novo a partir das fotos originais (requer Python 3 com Pillow e numpy):

```bash
python3 tools/otimizar_imagens.py /caminho/para/KIT_Caes_Maravilhosos
```

Fontes: Baloo 2 e Nunito (SIL Open Font License, em `assets/fonts/`).
