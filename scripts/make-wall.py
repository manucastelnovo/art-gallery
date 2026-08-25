"""
Recorta cada obra de "Los colores de la sombra" y genera los datos de la pared.

Ya no arma una sola imagen: cada cuadro sale como archivo propio para que en el
navegador sea un elemento aparte y pueda moverse solo al pasarle el mouse.

La rotacion NO se hornea en el archivo -- es el angulo de reposo de cada cuadro
colgado, y va en CSS para que la animacion pueda partir de ahi.

  python scripts/make-wall.py
"""
from PIL import Image
import json, os

SRC = 'dibujos/fotosmarceserieloscoloresdelasombra'
OUT = 'public/wall'
W, H = 2400, 1350                 # sistema de coordenadas de la pared
MAX_PX = 760                      # ancho maximo de exportacion

# La luz, medida sobre "sin nombre" -- una de las obras que cuelgan en esta
# misma pared, que es justamente una pintura de cuadros colgados con la luz
# cruzandolos. El brillo crece hacia -63deg, o sea que la fuente esta arriba a
# la derecha y las sombras caen hacia 117deg: abajo y a la izquierda.
LUZ = (2010, -190)                # posicion de la fuente en coordenadas de pared

# (archivo, centro x, centro y, ancho, rotacion de reposo, texto alternativo)
HANG = [
    ('sombra.jpg',                 380,  395, 610, -1.5,
     'Un hombre cayendo, de negro sobre ocre, y su sombra deformada abajo'),
    ('yoga.jpg',                   855,  285, 395,  1.3,
     'Una figura parada de cabeza contra una cortina roja, con la sombra estirada a un lado'),
    ('IMG-20230119-WA0018.jpg',   1355,  400, 530, -0.9,
     'La portada de la serie: "Los colores de la sombra" escrito a mano sobre naranja'),
    ('sin nombre.jpg',            1945,  320, 455,  1.6,
     'Una pared con cuadritos familiares y la luz de la ventana cruzando en diagonal'),
    ('IMG_20221013_162213.jpg',    390, 1015, 505,  1.0,
     'Una chica de vestido blanco junto a una bicicleta roja en un camino de tierra'),
    ('en la calle.jpg',            890,  935, 445, -1.3,
     'Un grupo de personas amontonadas, forcejeando o abrazandose, sobre fondo negro'),
    ('IMG_20221024_165219.jpg',   1380, 1015, 510,  0.8,
     'Un rostro en primer plano junto a un caballete y una pared rosada'),
    ('IMG_20221013_232455.jpg',   1950,  960, 495, -1.1,
     'La misma caida, fotografiada sobre el papel entero, firmada y marcada P.A'),
]

os.makedirs(OUT, exist_ok=True)
pieces, total = [], 0

for i, (name, cx, cy, w, rot, alt) in enumerate(HANG):
    im = Image.open(os.path.join(SRC, name)).convert('RGB')
    px = min(MAX_PX, im.width)
    im = im.resize((px, round(im.height * px / im.width)), Image.LANCZOS)

    slug = f'p{i + 1}'
    path = f'{OUT}/{slug}.webp'
    im.save(path, 'WEBP', quality=72, method=6)
    total += os.path.getsize(path)

    h = w * im.height / im.width          # alto en coordenadas de pared

    # Sombra propia: direccion y largo salen de donde esta cada cuadro respecto
    # de la luz. Los de arriba a la derecha, cerca de la fuente, la tiran corta;
    # los de abajo a la izquierda, larga.
    dx, dy = cx - LUZ[0], cy - LUZ[1]
    dist = (dx * dx + dy * dy) ** .5
    lejania = min(1.0, dist / 2250)
    largo = 9 + 26 * lejania
    sx, sy = dx / dist * largo, dy / dist * largo

    pieces.append({
        'src': f'/wall/{slug}.webp',
        'alt': alt,
        'left': round((cx - w / 2) / W * 100, 3),
        'top': round((cy - h / 2) / H * 100, 3),
        'width': round(w / W * 100, 3),
        'rot': rot,
        # en cqw: 1cqw = 1% del ancho de la pared, para que la sombra escale con ella
        'sx': round(sx / W * 100, 3),
        'sy': round(sy / W * 100, 3),
        'sb': round((5 + 13 * lejania) / W * 100, 3),
    })
    print(f'{slug}  {im.size}  sombra {sx:+5.0f},{sy:+5.0f} px  {os.path.getsize(path)/1024:5.0f} KB  {name}')

with open('app/wall-data.js', 'w', encoding='utf-8') as f:
    f.write('// GENERADO por scripts/make-wall.py -- no editar a mano.\n')
    f.write(f'export const WALL = {{ w: {W}, h: {H} }}\n')
    f.write('export const PIECES = ' + json.dumps(pieces, indent=2, ensure_ascii=False) + '\n')

print(f'\n{len(pieces)} obras, {total/1024:.0f} KB en total')
