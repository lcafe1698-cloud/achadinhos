# Achadinhos - Desenvolvido por Luiz Cafe
"""Página do 'link na bio' (GitHub Pages, pasta docs)."""
import html, os

def gerar(postados, canal, saida="docs/index.html"):
    e = html.escape
    cards = "".join(
        f'<a class="c" href="{e(p["link"])}" target="_blank" rel="noopener">'
        f'<span class="n">nº {p["num"]}</span><img src="img/{p["id"]}.jpg" alt="" loading="lazy">'
        f'<b>{e(p.get("nome") or "Oferta")}</b><i>{e(p.get("preco") or "")}</i><u>Ver oferta</u></a>'
        for p in reversed(postados[-40:]))
    doc = f"""<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Achadinhos da Shopee por Luiz</title>
<style>body{{margin:0;font-family:system-ui,sans-serif;background:#fff4ee;color:#222}}
header{{background:#ee4d2d;color:#fff;padding:22px 16px;text-align:center}}h1{{margin:0;font-size:22px}}
p{{margin:6px 0 0;font-size:14px}}.tg{{display:inline-block;margin-top:12px;background:#fff;color:#ee4d2d;
padding:10px 18px;border-radius:24px;font-weight:700;text-decoration:none}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;padding:16px;max-width:900px;margin:auto}}
.c{{background:#fff;border-radius:14px;padding:10px;text-decoration:none;color:#222;display:flex;flex-direction:column;gap:6px;
box-shadow:0 1px 4px #0001}}.c img{{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:10px}}
.n{{font-size:12px;color:#ee4d2d;font-weight:700}}.c b{{font-size:13px;line-height:1.3}}.c i{{font-style:normal;
color:#ee4d2d;font-weight:800}}.c u{{text-decoration:none;background:#ee4d2d;color:#fff;text-align:center;padding:8px;
border-radius:8px;font-weight:700;font-size:13px}}footer{{text-align:center;font-size:12px;color:#888;padding:20px}}</style>
</head><body><header><h1>Achadinhos da Shopee por Luiz</h1><p>Procure pelo número da oferta que você viu no post.</p>
<a class="tg" href="{e(canal)}">Ofertas todo dia no Telegram</a></header><main>{cards or "<p>Em breve as primeiras ofertas.</p>"}</main>
<footer>Links de afiliado: posso ganhar uma comissão sem custo extra para você.</footer></body></html>"""
    os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
    with open(saida, "w", encoding="utf-8") as f: f.write(doc)
