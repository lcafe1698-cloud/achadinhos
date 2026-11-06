# Achadinhos - Desenvolvido por Luiz Cafe
"""Envio para Telegram e Instagram (APIs oficiais)."""
import os, json, time, urllib.request, urllib.parse

def _post(url, data, timeout=60):
    body = urllib.parse.urlencode(data).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=timeout) as r:
        return json.loads(r.read())

def tg(metodo, **dados):
    tok = os.environ["TELEGRAM_TOKEN"]
    for k, v in list(dados.items()):
        if isinstance(v, (dict, list)): dados[k] = json.dumps(v)
    try:
        return _post(f"https://api.telegram.org/bot{tok}/{metodo}", dados)
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}")

def tg_updates(offset):
    return tg("getUpdates", offset=offset, timeout=0).get("result", [])

def tg_post_oferta(chat, texto, foto, link):
    botao = {"inline_keyboard": [[{"text": "🛒 Ver oferta", "url": link}]]}
    if foto:
        r = tg("sendPhoto", chat_id=chat, photo=foto, caption=texto, parse_mode="HTML", reply_markup=botao)
        if r.get("ok"): return r
    return tg("sendMessage", chat_id=chat, text=texto, parse_mode="HTML", reply_markup=botao)

def ig_publicar(img_url, legenda):
    """Publica no feed do Instagram profissional. Precisa IG_USER_ID e IG_TOKEN."""
    uid, tok = os.environ.get("IG_USER_ID"), os.environ.get("IG_TOKEN")
    if not (uid and tok): return {"pulado": "Instagram ainda não configurado"}
    base = "https://graph.facebook.com/v21.0"
    try:
        c = _post(f"{base}/{uid}/media", {"image_url": img_url, "caption": legenda, "access_token": tok})
        cid = c["id"]
        for _ in range(10):
            s = json.loads(urllib.request.urlopen(f"{base}/{cid}?fields=status_code&access_token={tok}", timeout=30).read())
            if s.get("status_code") == "FINISHED": break
            time.sleep(5)
        return _post(f"{base}/{uid}/media_publish", {"creation_id": cid, "access_token": tok})
    except urllib.error.HTTPError as e:
        return {"erro": e.read().decode()[:300]}
    except Exception as e:
        return {"erro": str(e)[:300]}
