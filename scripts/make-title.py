"""
Extrae, letra por letra, la frase que ella pinto a mano en la portada de la
serie: "LOS COLORES DE LA SOMBRA".

No se reconstruye nada. Cada letra es su pincelada, y se conserva ademas su
posicion vertical original -- su renglon es desparejo y esa irregularidad es
parte de como escribe.

  python scripts/make-title.py
"""
from PIL import Image
import json
import os
import numpy as np

SRC = 'dibujos/fotosmarceserieloscoloresdelasombra/IMG-20230119-WA0018.jpg'
OUT = 'public/title'

im = Image.open(SRC).convert('RGB')
W, H = im.size
crop = im.crop((int(W * .19), int(H * .15), int(W * .70), int(H * .46)))
lum = np.asarray(crop, dtype=float).mean(axis=2)
M = np.clip((70.0 - lum) / 45.0, 0, 1)
M[:, 640:] = 0                                  # la pincelada amarilla de la derecha

# Cajas leidas a mano sobre la foto ampliada de la portada. Se probo cortar por
# los huecos automaticamente y fallaba: en "SOMBRA" las letras se tocan y el
# algoritmo las unia de a pares.
RENGLONES = [
    (66, 186, [('L', 74, 140), ('O', 142, 200), ('S', 200, 255), (' ', 0, 0),
               ('C', 286, 348), ('O', 348, 393), ('L', 393, 437), ('O', 437, 492),
               ('R', 492, 540), ('E', 540, 588), ('S', 585, 636)]),
    (198, 300, [('D', 82, 150), ('E', 152, 202), (' ', 0, 0),
                ('L', 232, 272), ('A', 274, 322)]),
    (328, 438, [('S', 72, 148), ('O', 148, 208), ('M', 208, 272),
                ('B', 272, 322), ('R', 322, 370), ('A', 366, 414)]),
]

os.makedirs(OUT, exist_ok=True)
letras, total = [], 0
alto_ref = 0

for y0, y1, cajas in RENGLONES:
    for ch, x0, x1 in cajas:
        if ch == ' ':
            letras.append({'espacio': True})
            continue
        sub = M[y0:y1, x0:x1]
        ys, xs = np.nonzero(sub > 0.06)
        top = int(ys.min())
        sub = sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        alto_ref = max(alto_ref, sub.shape[0])

        rgba = np.zeros((*sub.shape, 4), np.uint8)
        rgba[..., :3] = 255
        rgba[..., 3] = (sub * 255).astype(np.uint8)
        slug = f'{len(letras):02d}'
        path = f'{OUT}/{slug}.webp'
        Image.fromarray(rgba, 'RGBA').save(path, 'WEBP', quality=88, method=6)
        total += os.path.getsize(path)

        letras.append({
            'src': f'/title/{slug}.webp',
            'ch': ch,
            'w': sub.shape[1],
            'h': sub.shape[0],
            'dy': top,                      # cuanto baja respecto del tope del renglon
        })

# normalizado a la altura de caja mas grande, para que el CSS solo fije una altura
for l in letras:
    if l.get('espacio'):
        continue
    l['w'] = round(l['w'] / alto_ref, 4)
    l['h'] = round(l['h'] / alto_ref, 4)
    l['dy'] = round(l['dy'] / alto_ref, 4)

with open('app/title-data.js', 'w', encoding='utf-8') as f:
    f.write('// GENERADO por scripts/make-title.py -- no editar a mano.' + chr(10))
    f.write('export const TITULO = ' + json.dumps(letras, indent=2, ensure_ascii=False) + chr(10))

n = sum(1 for l in letras if not l.get('espacio'))
print(f'{n} letras, {total/1024:.0f} KB   (alto de referencia {alto_ref}px)')
