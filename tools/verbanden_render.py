import json, random, sys
from playwright.sync_api import sync_playwright
T = dict(bg0='#2a2a2c', bg1='#161617', titel='#e9e4dc', sub='#9a948a', tegel0='#3a3a3d', tegel1='#2f2f32', rand='#55555a', letter='#e9e4dc', akzent='#c46a4a')
TXT = {'nl': ('VERBANDEN', 'Vind de 3 verbanden · 12 woorden'), 'de': ('VERBINDUNGEN', 'Finde die 3 Verbindungen · 12 Wörter')}
W, H = 1000, 760
def svg(p, seed):
    woorden = [w for _, ws in p['groepen'] for w in ws]; random.Random(seed).shuffle(woorden)
    tw, th, gap, x0, y0 = 220, 150, 18, (W - (4 * 220 + 3 * 18)) / 2, 175
    o = [f'''<defs><radialGradient id="bg" cx="50%" cy="35%" r="80%"><stop offset="0" stop-color="{T['bg0']}"/><stop offset="1" stop-color="{T['bg1']}"/></radialGradient>
<linearGradient id="t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T['tegel0']}"/><stop offset="1" stop-color="{T['tegel1']}"/></linearGradient>
<filter id="s" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#000" flood-opacity=".5"/></filter></defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>''']
    titel, sub = TXT[p['taal']]
    o.append(f'<text x="{W/2}" y="82" text-anchor="middle" font-family="DM Sans" font-weight="700" font-size="42" fill="{T["titel"]}" letter-spacing="6">{titel}</text>')
    o.append(f'<text x="{W/2}" y="120" text-anchor="middle" font-family="Fira Sans" font-weight="300" font-size="22" fill="{T["sub"]}">{sub}</text>')
    o.append(f'<rect x="{W/2-40}" y="138" width="80" height="4" rx="2" fill="{T["akzent"]}"/>')
    for i, w in enumerate(woorden):
        x, y = x0 + (i % 4) * (tw + gap), y0 + (i // 4) * (th + gap)
        fs = 40 if len(w) <= 7 else 36 if len(w) <= 9 else 30 if len(w) <= 11 else 26 if len(w) <= 14 else 22
        o.append(f'<g filter="url(#s)"><rect x="{x:.0f}" y="{y}" width="{tw}" height="{th}" rx="18" fill="url(#t)" stroke="{T["rand"]}" stroke-width="2"/></g>')
        o.append(f'<text x="{x+tw/2:.0f}" y="{y+th/2+fs*0.36:.0f}" text-anchor="middle" font-family="DM Sans" font-weight="700" font-size="{fs}" fill="{T["letter"]}">{w}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(o)}</svg>'
if __name__ == '__main__':
    daten = json.load(open(sys.argv[1])); ziel = sys.argv[2]; welche = [int(x) for x in sys.argv[3:]] or range(len(daten))
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H})
        pg.set_content('<html><body style="margin:0"><div id="s"></div></body></html>')
        for i in welche:
            pg.evaluate('h => document.getElementById("s").innerHTML = h', svg(daten[i], i)); pg.wait_for_timeout(120)
            pg.screenshot(path=f'{ziel}/verband-{i}.jpg', type='jpeg', quality=86, clip={'x': 0, 'y': 0, 'width': W, 'height': H})
        b.close()
    print('ok')

FARBEN = [('#c46a4a', '#e9e4dc'), ('#6f8f7a', '#e9e4dc'), ('#c9a24a', '#1e1e20')]
LOES = {'nl': 'OPLOSSING', 'de': 'LÖSUNG'}
def loesung(p):
    tw, th, gap, x0 = 220, 112, 18, (W - (4 * 220 + 3 * 18)) / 2
    o = [f'''<defs><radialGradient id="bg" cx="50%" cy="35%" r="80%"><stop offset="0" stop-color="{T['bg0']}"/><stop offset="1" stop-color="{T['bg1']}"/></radialGradient>
<filter id="s" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#000" flood-opacity=".5"/></filter></defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>''']
    o.append(f'<text x="{W/2}" y="70" text-anchor="middle" font-family="DM Sans" font-weight="700" font-size="38" fill="{T["titel"]}" letter-spacing="6">{LOES[p["taal"]]}</text>')
    for g, (naam, ws) in enumerate(p['groepen']):
        y = 120 + g * (th + 92); bg, fg = FARBEN[g]
        o.append(f'<text x="{x0}" y="{y+30}" font-family="DM Sans" font-weight="700" font-size="30" fill="{bg}">{naam}</text>')
        for i, w in enumerate(ws):
            x = x0 + i * (tw + gap); fs = 36 if len(w) <= 7 else 32 if len(w) <= 9 else 28 if len(w) <= 11 else 24 if len(w) <= 14 else 20
            o.append(f'<g filter="url(#s)"><rect x="{x:.0f}" y="{y+48}" width="{tw}" height="{th}" rx="16" fill="{bg}"/></g>')
            o.append(f'<text x="{x+tw/2:.0f}" y="{y+48+th/2+fs*0.36:.0f}" text-anchor="middle" font-family="DM Sans" font-weight="700" font-size="{fs}" fill="{fg}">{w}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(o)}</svg>'
def loesung_png(datei, i, ziel):
    p = json.load(open(datei))[i]
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H})
        pg.set_content(f'<html><body style="margin:0">{loesung(p)}</body></html>'); pg.wait_for_timeout(150)
        pg.screenshot(path=ziel, type='jpeg', quality=86, clip={'x': 0, 'y': 0, 'width': W, 'height': H}); b.close()
