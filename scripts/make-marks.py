"""
Genera las manchas de pintura de la pared.

Ni las formas ni los colores se inventan:

  FORMA  -- trozos de sus propias pinceladas, recortados del lienzo donde
            escribio a mano "LOS COLORES DE LA SOMBRA". Aislados y girados ya no
            se leen como letras: son marcas de pincel con punta seca y el borde
            comido por la trama de la tela.
  COLOR  -- zonas de pintura pura de sus cuadros (el campo naranja, el ocre del
            piso, el rojo de la cortina, el lavado oliva), con su grano incluido.

  python scripts/make-marks.py
"""
from PIL import Image, ImageFilter
import json, os
import numpy as np

SRC = 'dibujos/fotosmarceserieloscoloresdelasombra'
OUT = 'public/wall/marks'
W, H = 2400, 1350                      # coordenadas de la pared


# ---------- 1. formas: pinceladas sueltas de su lettering ----------

def lettering_mask():
    im = Image.open(os.path.join(SRC, 'IMG-20230119-WA0018.jpg')).convert('RGB')
    w, h = im.size
    crop = im.crop((int(w * .19), int(h * .15), int(w * .70), int(h * .46)))
    lum = np.asarray(crop, dtype=float).mean(axis=2)
    a = np.clip((70.0 - lum) / 45.0, 0, 1)
    a[:, 640:] = 0
    return (a * 255).astype(np.uint8)


def trim(a, t=14):
    ys, xs = np.nonzero(a > t)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


M = lettering_mask()
# Solo barras y manchas. Descartadas la curva de la C y el vertice de la A: aun
# giradas se seguian leyendo como letras.
SHAPES = {
    'barra':    trim(M[70:170,  74:100]),      # el asta de la L
    'smear':    trim(M[70:100, 560:604]),      # el brazo de arriba de la E
    'diagonal': trim(M[380:435, 330:368]),     # la pata de la R
    'mancha':   trim(M[335:395, 205:270]),     # el vertice interior de la M
}


def feather(alpha):
    """Apaga los bordes del recorte.

    Cada forma sale de cortar una foto, y ese corte deja lineas rectas que
    delatan que es un recorte. Una caida eliptica hacia el borde las disuelve.
    """
    a = np.asarray(alpha, dtype=float) / 255
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    return Image.fromarray((a * np.clip((1.15 - r) / 0.45, 0, 1) * 255).astype(np.uint8))


# ---------- 2. color y grano: zonas de pintura pura de sus cuadros ----------

ZONES = {
    'naranja':  ('IMG-20230119-WA0018.jpg', .16, .60, .42, .80),
    'amarillo': ('IMG-20230119-WA0018.jpg', .56, .34, .74, .46),
    'ocre':     ('yoga.jpg',                .04, .70, .34, .94),
    'rojo':     ('yoga.jpg',                .78, .08, .97, .34),
    'oliva':    ('sombra.jpg',              .06, .60, .34, .86),
    'negro':    ('en la calle.jpg',         .06, .03, .34, .18),
}


def texture(tag, size):
    f, x0, y0, x1, y1 = ZONES[tag]
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    w, h = im.size
    return im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1))).resize(size, Image.LANCZOS)


# ---------- 3. las manchas: forma + pintura + donde va en la pared ----------

# ---------- 3. biblioteca de trazos ----------
#
# Cada combinacion forma+color se exporta una sola vez y se reusa. Asi se pueden
# sembrar decenas de manchas por el mismo peso, y cada una elige su largo,
# grosor, giro y opacidad al colocarse.

os.makedirs(OUT, exist_ok=True)
TINTAS = ['naranja', 'amarillo', 'ocre', 'rojo', 'oliva', 'negro']
CANON = (320, 44)                      # tamano canonico del archivo

library, total = [], 0
for shape in SHAPES:
    for tag in TINTAS:
        alpha = Image.fromarray(SHAPES[shape]).resize(CANON, Image.LANCZOS)
        alpha = feather(alpha.filter(ImageFilter.GaussianBlur(0.7)))
        rgba = Image.merge('RGBA', (*texture(tag, CANON).split(), alpha))
        slug = f'{shape}-{tag}'
        path = f'{OUT}/{slug}.webp'
        rgba.save(path, 'WEBP', quality=80, method=6)
        total += os.path.getsize(path)
        library.append(f'/wall/marks/{slug}.webp')
print(f'biblioteca: {len(library)} trazos, {total/1024:.0f} KB')


# ---------- 4. siembra sobre la pared ----------
#
# Tamano medido, no estimado: en yoga.jpg una pincelada mide 40-60 px sobre 1527
# de ancho, y ese cuadro ocupa 395 px de pared -> unos 12 px de grosor aca. Se
# usan aun mas finas, entre 5 y 11 px.
#
# Se reparten por franjas del perimetro a intervalos regulares con un desvio
# menor que el intervalo, de modo que siempre quede aire entre una y otra.

import random
rng = random.Random(20260825)

# (nombre, x0, x1, y0, y1, cuantas, giro base, eje)
BANDAS = [
    ('izquierda', 18,   95,   70, 1290, 11,  84, 'v'),
    ('derecha',   2205, 2385,  70, 1290, 11,  84, 'v'),
    ('arriba',    120,  2290,  12,   88, 14,   0, 'h'),
    ('abajo',     120,  2290, 1252, 1338, 14,   0, 'h'),
]

marks = []
for nombre, x0, x1, y0, y1, n, giro, eje in BANDAS:
    largo_eje = (y1 - y0) if eje == 'v' else (x1 - x0)
    paso = largo_eje / n
    for k in range(n):
        # posicion regular + desvio acotado: garantiza separacion
        centro = (y0 if eje == 'v' else x0) + paso * (k + 0.5)
        centro += rng.uniform(-paso * 0.22, paso * 0.22)
        if eje == 'v':
            cy, cx = centro, rng.uniform(x0, x1)
        else:
            cx, cy = centro, rng.uniform(y0, y1)
        marks.append((cx, cy, giro + rng.uniform(-34, 34)))

# unas pocas en los huecos entre los cuadros, para que no sea solo un marco
for cx, cy in [(655, 645), (1078, 598), (1668, 682), (2232, 660), (905, 1208), (1352, 700)]:
    marks.append((cx, cy, rng.uniform(0, 180)))

placed = []
for cx, cy, rot in marks:
    largo = rng.uniform(48, 140)
    grosor = rng.uniform(5, 11)
    placed.append({
        'src': rng.choice(library),
        'left': round((cx - largo / 2) / W * 100, 3),
        'top': round((cy - grosor / 2) / H * 100, 3),
        'width': round(largo / W * 100, 3),
        'rot': round(rot, 1),
        'op': round(rng.uniform(0.24, 0.5), 2),
    })

with open('app/wall-marks.js', 'w', encoding='utf-8') as f:
    f.write('// GENERADO por scripts/make-marks.py -- no editar a mano.' + chr(10))
    f.write('export const MARKS = ' + json.dumps(placed, indent=2) + chr(10))

print(f'{len(placed)} manchas sembradas (largo 48-140, grosor 5-11 px de pared)')
