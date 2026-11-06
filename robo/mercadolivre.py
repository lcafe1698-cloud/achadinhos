# Achadinhos - Desenvolvido por Luiz Cafe
"""Lê dados do produto do Mercado Livre (API pública quando responder; senão, a própria página).
O link de afiliado é o que você gera no painel/app de Afiliados do Mercado Livre e manda ao robô."""
import re, json, html as H
from shopee import _get, fmt

RX = re.compile(r"https?://\S*(?:mercadoli[vb]re|meli\.la|mercadopago)\S*", re.I)
API = "https://api.mercadolibre.com"

def _id(txt):
    m = re.search(r"MLB-?(\d{6,})", txt or "", re.I)
    return "MLB" + m.group(1) if m else None

def _api(caminho):
    try: return json.loads(_get(API + caminho)[1])
    except Exception: return {}

def _desc(antigo, atual):
    try:
        a, b = float(antigo), float(atual)
        return f"{round((1 - b / a) * 100)}%" if a > b > 0 else ""
    except Exception: return ""

def produto(url):
    p = {"nome": "", "preco": "", "preco_antigo": "", "desconto": "", "imagem": "", "link": url, "url": url,
         "loja": "Mercado Livre"}
    pagina = ""
    try: p["url"], pagina = _get(url)
    except Exception: pass
    iid = _id(p["url"]) or _id(url) or _id(pagina)
    if iid:
        it = _api(f"/items/{iid}")
        if it.get("title"):
            fotos = it.get("pictures") or [{}]
            p.update(nome=it["title"], preco=fmt(it.get("price")), imagem=fotos[0].get("secure_url") or it.get("thumbnail", ""))
            if it.get("original_price"):
                p["preco_antigo"] = fmt(it["original_price"]); p["desconto"] = _desc(it["original_price"], it.get("price"))
        else:
            pr = _api(f"/products/{iid}")
            if pr.get("name"):
                bb = pr.get("buy_box_winner") or {}
                p.update(nome=pr["name"], imagem=((pr.get("pictures") or [{}])[0]).get("url", ""))
                if bb.get("price"): p["preco"] = fmt(bb["price"])
                if bb.get("original_price"):
                    p["preco_antigo"] = fmt(bb["original_price"]); p["desconto"] = _desc(bb["original_price"], bb["price"])
    if pagina and not (p["nome"] and p["preco"]):
        og = lambda k: H.unescape((re.search(r'<meta[^>]+property="og:%s"[^>]+content="([^"]*)"' % k, pagina) or [None, ""])[1])
        p["nome"] = p["nome"] or re.sub(r"\s*\|\s*Mercado Liv?re.*$", "", og("title"), flags=re.I).strip()
        p["imagem"] = p["imagem"] or og("image")
        if not p["preco"]:
            m = (re.search(r'itemprop="price"\s+content="([\d.]+)"', pagina) or
                 re.search(r'"price"\s*:\s*"?([\d.]+)', pagina))
            if m: p["preco"] = fmt(m.group(1))
    return p
