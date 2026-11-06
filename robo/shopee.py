# Achadinhos - Desenvolvido por Luiz Cafe
"""Lê dados do produto da Shopee (API de Afiliados quando houver chave; senão, a própria página)."""
import os, re, json, time, hashlib, urllib.request, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
API = "https://open-api.affiliate.shopee.com.br/graphql"

def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), r.read().decode("utf-8", "ignore")

def expandir(url):
    """Segue o link curto (s.shopee.com.br, shope.ee) até a página do produto."""
    try:
        final, _ = _get(url)
        return final
    except Exception:
        return url

def ids(url):
    m = re.search(r"i\.(\d+)\.(\d+)", url) or re.search(r"/product/(\d+)/(\d+)", url)
    return (m.group(1), m.group(2)) if m else (None, None)

def _api(query, variables=None):
    app, sec = os.environ.get("SHOPEE_APP_ID"), os.environ.get("SHOPEE_SECRET")
    if not (app and sec): return None
    body = json.dumps({"query": query, "variables": variables or {}}, separators=(",", ":"))
    ts = str(int(time.time()))
    sig = hashlib.sha256((app + ts + body + sec).encode()).hexdigest()
    req = urllib.request.Request(API, data=body.encode(), headers={
        "Content-Type": "application/json",
        "Authorization": f"SHA256 Credential={app}, Timestamp={ts}, Signature={sig}"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())

def link_afiliado(url):
    try:
        r = _api('mutation($u:String!){generateShortLink(input:{originUrl:$u}){shortLink}}', {"u": url})
        return r["data"]["generateShortLink"]["shortLink"]
    except Exception:
        return None

def produto(url):
    """Devolve dict: nome, preco, preco_antigo, desconto, imagem, link. Campos podem vir vazios."""
    final = expandir(url)
    shop, item = ids(final)
    p = {"nome": "", "preco": "", "preco_antigo": "", "desconto": "", "imagem": "", "link": url, "url": final}
    if shop:
        try:
            r = _api('query($s:Int64,$i:Int64){productOfferV2(shopId:$s,itemId:$i){nodes{productName price priceMin '
                     'priceMax priceDiscountRate imageUrl offerLink}}}', {"s": int(shop), "i": int(item)})
            n = (r or {}).get("data", {}).get("productOfferV2", {}).get("nodes") or []
            if n:
                n = n[0]
                p.update(nome=n.get("productName", ""), preco=fmt(n.get("priceMin") or n.get("price")),
                         imagem=n.get("imageUrl", ""), link=n.get("offerLink") or url)
                if n.get("priceDiscountRate"): p["desconto"] = f"{int(float(n['priceDiscountRate']))}%"
        except Exception:
            pass
    if not p["nome"]:
        try:
            _, html = _get(final)
            og = lambda k: (re.search(r'<meta[^>]+property="og:%s"[^>]+content="([^"]*)"' % k, html) or [None, ""])[1]
            p["nome"] = re.sub(r"\s*\|\s*Shopee.*$", "", og("title")).strip()
            p["imagem"] = p["imagem"] or og("image")
        except Exception:
            pass
    if p["link"] == url and os.environ.get("SHOPEE_APP_ID"):
        p["link"] = link_afiliado(final) or url
    return p

def fmt(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(v or "")
