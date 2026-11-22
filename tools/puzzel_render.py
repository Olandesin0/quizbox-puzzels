import json, math, os, sys, time
from playwright.sync_api import sync_playwright
T = dict(bg0='#2a2a2c', bg1='#161617', titel='#e9e4dc', sub='#9a948a', tegel0='#3a3a3d', tegel1='#2f2f32', rand='#55555a', letter='#e9e4dc',
         mitte='#c46a4a', mitteicon='#1e1e20', leer='#1e1e20', ring0='#c46a4a', ring1='#9c4f35', strich='#2a2a2c', schrift="'DM Sans', sans-serif", gewicht='700')
TXT = {('paardensprong', 'nl'): ('PAARDENSPRONG', 'Spring als het paard · 8 letters'), ('paardensprong', 'de'): ('RÖSSELSPRUNG', 'Springe wie das Pferd · 8 Buchstaben'),
       ('taart', 'nl'): ('TAARTPUZZEL', 'Rondom te lezen · 1 letter ontbreekt'), ('taart', 'de'): ('TORTENRÄTSEL', 'Im Kreis lesen · 1 Buchstabe fehlt')}
KRING = [0, 5, 6, 1, 8, 3, 2, 7]
DEFS = f'''<defs><radialGradient id="bg" cx="50%" cy="35%" r="80%"><stop offset="0" stop-color="{T['bg0']}"/><stop offset="1" stop-color="{T['bg1']}"/></radialGradient>
<linearGradient id="tegel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T['tegel0']}"/><stop offset="1" stop-color="{T['tegel1']}"/></linearGradient>
<filter id="sch" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#000" flood-opacity=".5"/></filter></defs>
<rect width="800" height="800" fill="url(#bg)"/>'''
def kop(titel, sub):
    return (f'<text x="400" y="80" text-anchor="middle" font-family="{T["schrift"]}" font-weight="700" font-size="42" fill="{T["titel"]}" letter-spacing="6">{titel}</text>'
            f'<text x="400" y="118" text-anchor="middle" font-family="Fira Sans" font-weight="300" font-size="22" fill="{T["sub"]}" letter-spacing="1">{sub}</text>')
def paard(r):
    w, start, ri = r['woord'], int(r['start']), int(r['richting']); vak = [''] * 9
    for i, ch in enumerate(w): vak[KRING[(start + ri * i) % 8]] = ch
    g, s, x0, y0 = 170, 190, 115, 170; o = []
    for i in range(9):
        x, y = x0 + (i % 3) * s, y0 + (i // 3) * s
        if i == 4: o.append(f'<rect x="{x}" y="{y}" width="{g}" height="{g}" rx="22" fill="{T["mitte"]}"/><text x="{x+g/2}" y="{y+g/2+42}" text-anchor="middle" font-family="DejaVu Sans" font-size="120" fill="{T["mitteicon"]}">♞</text>')
        else: o.append(f'<g filter="url(#sch)"><rect x="{x}" y="{y}" width="{g}" height="{g}" rx="22" fill="url(#tegel)" stroke="{T["rand"]}" stroke-width="2"/></g><text x="{x+g/2}" y="{y+g/2+38}" text-anchor="middle" font-family="{T["schrift"]}" font-weight="700" font-size="108" fill="{T["letter"]}">{vak[i]}</text>')
    return ''.join(o)
def taart(r):
    w, start, ri, leeg, n = r['woord'], int(r['start']), int(r['richting']), int(r['leeg']), 9; vak = [''] * n
    for i, ch in enumerate(w): vak[(start + ri * i) % n] = '' if i == leeg else ch
    cx, cy, R = 400, 470, 295; o = [f'<circle cx="{cx}" cy="{cy}" r="{R+14}" fill="{T["ring0"]}" filter="url(#sch)"/><circle cx="{cx}" cy="{cy}" r="{R+5}" fill="{T["ring1"]}"/>']
    for i in range(n):
        a0, a1 = math.radians(-90 + i * 40), math.radians(-50 + i * 40)
        p0, p1 = (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))
        f = T['leer'] if not vak[i] else (T['tegel0'] if i % 2 else T['tegel1'])
        o.append(f'<path d="M{cx},{cy} L{p0[0]:.1f},{p0[1]:.1f} A{R},{R} 0 0,1 {p1[0]:.1f},{p1[1]:.1f} Z" fill="{f}" stroke="{T["strich"]}" stroke-width="5"/>')
        am = math.radians(-70 + i * 40); tx, ty = cx + R * .66 * math.cos(am), cy + R * .66 * math.sin(am)
        o.append(f'<text x="{tx:.1f}" y="{ty+32:.1f}" text-anchor="middle" font-family="{T["schrift"]}" font-weight="700" font-size="88" fill="{T["letter"] if vak[i] else T["sub"]}" fill-opacity="{1 if vak[i] else .6}">{vak[i] or "?"}</text>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="56" fill="{T["mitte"]}" stroke="{T["strich"]}" stroke-width="5"/><text x="{cx}" y="{cy+15}" text-anchor="middle" font-family="{T["schrift"]}" font-weight="700" font-size="42" fill="{T["mitteicon"]}">9</text>')
    return ''.join(o)
rows = json.load(open('puzzels.json'))
ziel = sys.argv[1]; os.makedirs(ziel, exist_ok=True)
nur = sys.argv[2:]  # optionale ids
t0 = time.time()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 800, 'height': 800})
    pg.set_content('<html><body style="margin:0"><div id="s"></div></body></html>')
    for k, r in enumerate(rows):
        if nur and r['id'] not in nur: continue
        titel, sub = TXT[(r['typ'], r['taal'])]
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">{DEFS}{kop(titel, sub)}{paard(r) if r["typ"] == "paardensprong" else taart(r)}</svg>'
        pg.evaluate('h => document.getElementById("s").innerHTML = h', svg)
        if k == 0: pg.wait_for_timeout(300)
        pg.screenshot(path=f'{ziel}/{r["id"]}.jpg', type='jpeg', quality=86, clip={'x': 0, 'y': 0, 'width': 800, 'height': 800})
    b.close()
print('fertig', round(time.time() - t0, 1), 's')
