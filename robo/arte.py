# Achadinhos - Desenvolvido por Luiz Cafe
"""Arte do post (1080x1350) a partir da foto e do preço."""
import io, urllib.request
from PIL import Image, ImageDraw, ImageFont

MARCA = "Achadinhos do Luiz"
LOJAS = {"Shopee": ((238, 77, 45), "white"), "Mercado Livre": ((255, 230, 0), (45, 50, 119))}
FONTES = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf", "arialbd.ttf"]

def _f(tam):
    for f in FONTES:
        try: return ImageFont.truetype(f, tam)
        except Exception: pass
    return ImageFont.load_default()

def _quebra(d, txt, fonte, larg, max_l=3):
    linhas, atual = [], ""
    for w in txt.split():
        t = (atual + " " + w).strip()
        if d.textlength(t, font=fonte) <= larg: atual = t
        else:
            linhas.append(atual); atual = w
    linhas.append(atual)
    if len(linhas) > max_l:
        linhas = linhas[:max_l]; linhas[-1] = linhas[-1].rstrip(".,") + "…"
    return linhas

def gerar(p, saida, num):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (255, 244, 238)); d = ImageDraw.Draw(img)
    loja = p.get("loja") or "Shopee"; cor, txt = LOJAS.get(loja, LOJAS["Shopee"])
    ac = (52, 131, 250) if loja == "Mercado Livre" else (238, 77, 45)
    d.rectangle([0, 0, W, 120], fill=cor)
    d.text((W // 2, 60), f"{MARCA}  •  {loja}", font=_f(46), fill=txt, anchor="mm")
    try:
        req = urllib.request.Request(p["imagem"], headers={"User-Agent": "Mozilla/5.0"})
        foto = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
        foto.thumbnail((900, 760))
        caixa = Image.new("RGB", (940, 800), "white"); caixa.paste(foto, ((940 - foto.width) // 2, (800 - foto.height) // 2))
        img.paste(caixa, (70, 150))
    except Exception:
        d.rounded_rectangle([70, 150, 1010, 950], 30, fill="white")
        d.text((W // 2, 550), "OFERTA", font=_f(120), fill=ac, anchor="mm")
    y = 985
    for l in _quebra(d, p.get("nome") or "Achadinho do dia", _f(44), 940):
        d.text((70, y), l, font=_f(44), fill=(40, 40, 40)); y += 56
    if p.get("preco_antigo"):
        d.text((70, y + 8), p["preco_antigo"], font=_f(38), fill=(150, 150, 150))
        tl = d.textlength(p["preco_antigo"], font=_f(38)); d.line([70, y + 30, 70 + tl, y + 30], fill=(150, 150, 150), width=4)
        y += 50
    d.text((70, y + 10), p.get("preco") or "", font=_f(84), fill=ac)
    if p.get("desconto"):
        d.rounded_rectangle([780, y + 14, 1010, y + 104], 24, fill=ac)
        d.text((895, y + 59), f"-{p['desconto']}", font=_f(52), fill="white", anchor="mm")
    d.rectangle([0, H - 80, W, H], fill=(40, 40, 40))
    d.text((W // 2, H - 40), f"Link na bio  •  oferta nº {num}", font=_f(36), fill="white", anchor="mm")
    img.save(saida, "JPEG", quality=90)
    return saida
# Achadinhos - Desenvolvido por Luiz Cafe
"""Arte do post (1080x1350) a partir da foto e do preço."""
import io, urllib.request
from PIL import Image, ImageDraw, ImageFont

MARCA = "Achadinhos da Shopee por Luiz"
FONTES = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf", "arialbd.ttf"]

def _f(tam):
    for f in FONTES:
        try: return ImageFont.truetype(f, tam)
        except Exception: pass
    return ImageFont.load_default()

def _quebra(d, txt, fonte, larg, max_l=3):
    linhas, atual = [], ""
    for w in txt.split():
        t = (atual + " " + w).strip()
        if d.textlength(t, font=fonte) <= larg: atual = t
        else:
            linhas.append(atual); atual = w
    linhas.append(atual)
    if len(linhas) > max_l:
        linhas = linhas[:max_l]; linhas[-1] = linhas[-1].rstrip(".,") + "…"
    return linhas

def gerar(p, saida, num):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (255, 244, 238)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 120], fill=(238, 77, 45))
    d.text((W // 2, 60), MARCA, font=_f(46), fill="white", anchor="mm")
    try:
        req = urllib.request.Request(p["imagem"], headers={"User-Agent": "Mozilla/5.0"})
        foto = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
        foto.thumbnail((900, 760))
        caixa = Image.new("RGB", (940, 800), "white"); caixa.paste(foto, ((940 - foto.width) // 2, (800 - foto.height) // 2))
        img.paste(caixa, (70, 150))
    except Exception:
        d.rounded_rectangle([70, 150, 1010, 950], 30, fill="white")
        d.text((W // 2, 550), "OFERTA", font=_f(120), fill=(238, 77, 45), anchor="mm")
    y = 985
    for l in _quebra(d, p.get("nome") or "Achadinho do dia", _f(44), 940):
        d.text((70, y), l, font=_f(44), fill=(40, 40, 40)); y += 56
    if p.get("preco_antigo"):
        d.text((70, y + 8), p["preco_antigo"], font=_f(38), fill=(150, 150, 150))
        tl = d.textlength(p["preco_antigo"], font=_f(38)); d.line([70, y + 30, 70 + tl, y + 30], fill=(150, 150, 150), width=4)
        y += 50
    d.text((70, y + 10), p.get("preco") or "", font=_f(84), fill=(238, 77, 45))
    if p.get("desconto"):
        d.rounded_rectangle([780, y + 14, 1010, y + 104], 24, fill=(238, 77, 45))
        d.text((895, y + 59), f"-{p['desconto']}", font=_f(52), fill="white", anchor="mm")
    d.rectangle([0, H - 80, W, H], fill=(40, 40, 40))
    d.text((W // 2, H - 40), f"Link na bio  •  oferta nº {num}", font=_f(36), fill="white", anchor="mm")
    img.save(saida, "JPEG", quality=90)
    return saida
