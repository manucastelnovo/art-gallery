"""
Genera la superficie de la pared: la trama del lienzo crudo de ella.

Sale del borde sin pintar de la portada de la serie -- la tela deshilachada
donde escribio "7/10". No es una textura de stock: es su lienzo.

El mosaico no se espeja. Espejar deja un motivo simetrico que, repetido, se lee
como empapelado. En cambio se mide el periodo de la trama del lino (4 px) y se
corta el mosaico en un multiplo exacto: al ser la trama periodica, encaja sola.

  python scripts/make-surface.py
"""
from PIL import Image, ImageFilter
import numpy as np
import os

SRC = 'dibujos/fotosmarceserieloscoloresdelasombra/IMG-20230119-WA0018.jpg'
OUT = 'public/wall'

im = Image.open(SRC).convert('RGB')
W, H = im.size
patch = im.crop((int(W * .098), int(H * .15), int(W * .168), int(H * .78)))

# Un mosaico solo puede repetir lo que no tiene rasgos: cualquier mota o mancha
# se convierte, al repetirse, en un patron. Se deja unicamente la trama.
#
# Nada de filtro de mediana: la trama mide 3 px y cualquier suavizado la borra
# justo a ella. En cambio se separa el detalle del degrade de luz y se recortan
# los extremos, que es donde viven las motas -- la trama, regular, sobrevive.
f = np.asarray(patch, dtype=float)
suave = np.asarray(patch.filter(ImageFilter.GaussianBlur(12)), dtype=float)
base = f.reshape(-1, 3).mean(axis=0)
detalle = f - suave
lim = 1.6 * detalle.std()
f = np.clip(detalle, -lim, lim) + base

# periodo de la trama, medido por autocorrelacion
g = f.mean(axis=2)
g = g - g.mean()


def periodo(sig, lo=3, hi=40):
    sig = sig - sig.mean()
    ac = np.correlate(sig, sig, 'full')[len(sig) - 1:]
    return lo + int(np.argmax(ac[lo:hi] / ac[0]))


px, py = periodo(g.mean(axis=0)), periodo(g.mean(axis=1))
side = (min(f.shape[1], f.shape[0]) // max(px, py)) * max(px, py)  # multiplo exacto

# de todas las franjas posibles, la que menos variacion de fondo tiene
mejor, mejor_var = 0, 1e9
for y in range(0, f.shape[0] - side, py):
    v = np.asarray(Image.fromarray(np.clip(f[y:y + side], 0, 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(10)), dtype=float).std()
    if v < mejor_var:
        mejor, mejor_var = y, v

tile = np.clip(f[mejor:mejor + side, :side], 0, 255).astype(np.uint8)

os.makedirs(OUT, exist_ok=True)
path = f'{OUT}/lienzo.webp'
Image.fromarray(tile).save(path, 'WEBP', quality=88, method=6, lossless=False)
print(f'periodo trama  x={px}px  y={py}px   -> mosaico {side}x{side}')
print(f'{path}  {os.path.getsize(path)/1024:.1f} KB   color {tile.reshape(-1,3).mean(axis=0).round(0)}')
