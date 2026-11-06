# Achadinhos - Desenvolvido por Luiz Cafe
"""Roda a cada 15 min no GitHub Actions: lê os links que você manda ao robô, monta a fila e posta nos horários."""
import os, re, json, time, datetime, subprocess, html
import shopee, mercadolivre, redes, arte, pagina

EST = "data/estado.json"
HORAS = [int(h) for h in os.environ.get("HORARIOS", "9,12,15,18,21").split(",")]
CANAL = os.environ.get("TELEGRAM_CANAL", "")
CONVITE = os.environ.get("CANAL_LINK", "https://t.me/")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
RX_LINK = re.compile(r"https?://\S*(?:shopee|shope\.ee|mercadoli[vb]re|meli\.la)\S*", re.I)
AJUDA = ("Mande o link de um produto da Shopee ou do Mercado Livre (seu link de afiliado) e eu coloco na fila.\n"
         "Opcional, nas linhas de baixo: nome | preço | preço antigo\n\n"
         "/fila ver a fila  •  /agora postar o próximo já  •  /remover N")

def agora_br(): return datetime.datetime.utcnow() - datetime.timedelta(hours=3)

def carregar():
    try: return json.load(open(EST, encoding="utf-8"))
    except Exception: return {"offset": 0, "dono": None, "fila": [], "postados": [], "num": 0, "ultimo": ""}

def salvar(s):
    os.makedirs("data", exist_ok=True)
    json.dump(s, open(EST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def git_push(msg):
    for c in (["git", "config", "user.name", "robo-achadinhos"], ["git", "config", "user.email", "robo@users.noreply.github.com"],
              ["git", "add", "-A"], ["git", "commit", "-q", "-m", msg], ["git", "pull", "-q", "--rebase"], ["git", "push", "-q"]):
        subprocess.run(c, check=False)

def responder(s, chat, txt): redes.tg("sendMessage", chat_id=chat, text=txt, disable_web_page_preview=True)

def novo_item(s, texto, foto_id):
    link = RX_LINK.search(texto).group(0)
    p = mercadolivre.produto(link) if mercadolivre.RX.match(link) else dict(shopee.produto(link), loja="Shopee")
    extra = [l.strip() for l in texto.replace(link, "").splitlines() if l.strip()]
    if extra:
        partes = [x.strip() for x in extra[0].split("|")]
        if partes[0]: p["nome"] = partes[0]
        if len(partes) > 1: p["preco"] = partes[1] if partes[1].startswith("R$") else "R$ " + partes[1]
        if len(partes) > 2: p["preco_antigo"] = partes[2] if partes[2].startswith("R$") else "R$ " + partes[2]
    if foto_id: p["foto_tg"] = foto_id
    p["id"] = str(int(time.time() * 1000))
    s["fila"].append(p)
    return p

def ler_mensagens(s):
    for u in redes.tg_updates(s["offset"]):
        s["offset"] = u["update_id"] + 1
        m = u.get("message") or {}
        chat = (m.get("chat") or {}).get("id"); txt = m.get("text") or m.get("caption") or ""
        if not chat or m["chat"].get("type") != "private": continue
        if s["dono"] is None and txt.startswith("/start"): s["dono"] = chat
        if chat != s["dono"]:
            responder(s, chat, "Este robô é privado. Siga o canal para receber as ofertas 😉"); continue
        if txt.startswith(("/start", "/ajuda", "/help")): responder(s, chat, AJUDA)
        elif txt.startswith("/fila"):
            l = "\n".join(f"{i+1}. {p.get('nome') or p['link']} {p.get('preco','')}" for i, p in enumerate(s["fila"]))
            responder(s, chat, l or "A fila está vazia.")
        elif txt.startswith("/remover"):
            try: p = s["fila"].pop(int(txt.split()[1]) - 1); responder(s, chat, f"Removido: {p.get('nome') or p['link']}")
            except Exception: responder(s, chat, "Use /remover 2 (o número da fila).")
        elif txt.startswith("/agora"): s["forcar"] = True
        elif RX_LINK.search(txt):
            foto = (m.get("photo") or [{}])[-1].get("file_id")
            p = novo_item(s, txt, foto)
            falta = "" if p.get("nome") and p.get("preco") else ("\n\n⚠️ Não consegui ler nome/preço. Reenvie o link com a "
                                                              "linha: nome | preço | preço antigo")
            responder(s, chat, f"✅ Na fila (posição {len(s['fila'])}): {p.get('nome') or 'produto'} {p.get('preco','')}{falta}")
        else: responder(s, chat, AJUDA)

def textos(p, n):
    de = f"De <s>{p['preco_antigo']}</s>\n" if p.get("preco_antigo") else ""
    desc = f" (-{p['desconto']})" if p.get("desconto") else ""
    nome_h = html.escape(p.get('nome') or 'Achadinho do dia')
    loja = p.get("loja") or "Shopee"
    tg = f"🔥 <b>{nome_h}</b>\n🏷️ {loja}\n\n{de}💰 Por <b>{p.get('preco','')}</b>{desc}\n\n🛒 {p['link']}"
    ig = (f"🔥 {p.get('nome') or 'Achadinho do dia'}\n💰 {p.get('preco','')}{desc}\n\n🔗 Link na bio: oferta nº {n}\n"
          f"📲 Ofertas todo dia no nosso canal do Telegram (link na bio)\n\n#achadinhos " + ("#mercadolivre #achadinhosmercadolivre" if loja == "Mercado Livre" else "#achadinhosshopee #shopee") + " #ofertas #promoção")
    wa = f"🔥 {p.get('nome') or 'Achadinho do dia'} ({loja})\n💰 {p.get('preco','')}{desc}\n🛒 {p['link']}"
    return tg, ig, wa

def postar(s):
    p = s["fila"].pop(0); s["num"] += 1; n = p["num"] = s["num"]
    os.makedirs("docs/img", exist_ok=True)
    if not p.get("imagem") and p.get("foto_tg"):          # foto mandada por você no Telegram
        f = redes.tg("getFile", file_id=p["foto_tg"]).get("result", {}).get("file_path")
        if f: p["_img"] = f"https://api.telegram.org/file/bot{os.environ['TELEGRAM_TOKEN']}/{f}"
    arte.gerar(dict(p, imagem=p.get("imagem") or p.get("_img", "")), f"docs/img/{p['id']}.jpg", n)
    p.pop("_img", None)
    tg, ig, wa = textos(p, n)
    foto = p.get("imagem") or p.get("foto_tg")
    r = redes.tg_post_oferta(CANAL, tg, foto, p["link"]) if CANAL else {"pulado": "sem canal"}
    s["postados"].append({k: p.get(k) for k in ("id", "num", "nome", "preco", "link", "loja")})
    pagina.gerar(s["postados"], CONVITE)
    salvar(s); git_push(f"oferta {n}")
    time.sleep(20)
    url = f"https://raw.githubusercontent.com/{REPO}/main/docs/img/{p['id']}.jpg"
    ri = redes.ig_publicar(url, ig)
    if s.get("dono"):
        st = "✅ Telegram" if r.get("ok") else f"❌ Telegram: {r.get('description', r)}"
        si = "✅ Instagram" if ri.get("id") else f"ℹ️ Instagram: {ri.get('pulado') or ri.get('erro')}"
        responder(s, s["dono"], f"Postei a oferta nº {n}. {st} • {si}\n\nTexto para o WhatsApp:\n\n{wa}")

def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    s = carregar(); ler_mensagens(s)
    t = agora_br(); chave = t.strftime("%Y-%m-%d %H")
    if s["fila"] and (s.pop("forcar", False) or (t.hour in HORAS and s.get("ultimo") != chave)):
        s["ultimo"] = chave; postar(s)
    s.pop("forcar", None)
    if not os.path.exists("docs/index.html"): pagina.gerar(s["postados"], CONVITE)
    salvar(s); git_push("estado")

if __name__ == "__main__":
    main()
