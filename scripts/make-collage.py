"""
Arma el collage de fondo con las 8 fotos de "Los colores de la sombra".

Las coloca como un salon hang -- cuadros colgados en una pared, con tamanos
distintos, alturas desparejas, ligeras rotaciones y sombra propia. La idea no es
decorativa: una de las pinturas de la serie ("sin nombre") muestra exactamente
eso, cuadros colgados con la luz cruzandolos en diagonal.

  python scripts/make-collage.py
"""
from PIL import Image, ImageFilter
import os

SRC = 'dibujos/fotosmarceserieloscoloresdelasombra'
OUT = 'public/bg'
W, H = 2400, 1350
PARED = (142, 134, 124)          # promedio de los bordes del propio cuadro

# (archivo, centro x, centro y, ancho, rotacion)
# Las dos fotos de la misma obra -- sombra.jpg y IMG_20221013_232455.jpg, una
# recortada y otra mostrando el papel firmado -- van en esquinas opuestas.
HANG = [
    ('sombra.jpg',                 380,  395, 610, -1.5),
    ('yoga.jpg',                   855,  285, 395,  1.3),
    ('IMG-20230119-WA0018.jpg',   1355,  400, 530, -0.9),
    ('sin nombre.jpg',            1945,  320, 455,  1.6),
    ('IMG_20221013_162213.jpg',    390, 1015, 505,  1.0),
    ('en la calle.jpg',            890,  935, 445, -1.3),
    ('IMG_20221024_165219.jpg',   1380, 1015, 510,  0.8),
    ('IMG_20221013_232455.jpg',   1950,  960, 495, -1.1),
]


def placed(name, w, ang):
    """Devuelve la imagen girada y su mascara, sin esquinas de relleno."""
    im = Image.open(os.path.join(SRC, name)).convert('RGB')
    h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    mask = Image.new('L', (w, h), 255)
    return (im.rotate(ang, resample=Image.BICUBIC, expand=True, fillcolor=PARED),
            mask.rotate(ang, resample=Image.BICUBIC, expand=True, fillcolor=0))


shadow = Image.new('L', (W, H), 0)
for name, cx, cy, w, ang in HANG:
    im, mask = placed(name, w, ang)
    shadow.paste(Image.eval(mask, lambda v: int(v * 0.55)),
                 (cx - im.width // 2 + 10, cy - im.height // 2 + 15))
shadow = shadow.filter(ImageFilter.GaussianBlur(14))

canvas = Image.new('RGB', (W, H), PARED)
canvas.paste(Image.new('RGB', (W, H), (44, 40, 36)), (0, 0), shadow)
for name, cx, cy, w, ang in HANG:
    im, mask = placed(name, w, ang)
    canvas.paste(im, (cx - im.width // 2, cy - im.height // 2), mask)

os.makedirs(OUT, exist_ok=True)
for width, q in [(1400, 72), (2000, 74)]:
    r = canvas.resize((width, round(H * width / W)), Image.LANCZOS)
    p = f'{OUT}/collage-{width}.webp'
    r.save(p, 'WEBP', quality=q, method=6)
    print(f'{p}  {r.size}  {os.path.getsize(p)/1024:.0f} KB')
