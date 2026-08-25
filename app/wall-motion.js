/*
 * Cómo se mueve cada cuadro. Editable a mano — no lo pisa make-wall.py.
 *
 *  nail  posición del clavo (transform-origin). No todos cuelgan del centro:
 *        uno clavado a un costado gira desde ahí y se lee distinto.
 *  amp   qué tan fuerte es el envión. Los grandes pesan más y se mueven menos;
 *        el que está sobre papel es el más liviano y el que más se sacude.
 *  dir   hacia qué lado sale el primer golpe.
 *  dur   cuánto tarda en apagarse.
 *  ritmo qué curva sigue: 'lento', 'medio' o 'corto'.
 */
export const MOTION = [
  { nail: '46% 3%',   amp: 0.55, dir: 1,  dur: '1.95s', ritmo: 'lento' }, // sombra (el más grande)
  { nail: '56% 5%',   amp: 1.05, dir: -1, dur: '1.15s', ritmo: 'corto' }, // yoga
  { nail: '50% 4%',   amp: 0.8,  dir: 1,  dur: '1.5s',  ritmo: 'medio' }, // la portada
  { nail: '63% 3.5%', amp: 0.95, dir: -1, dur: '1.35s', ritmo: 'corto' }, // sin nombre, clavo a la derecha
  { nail: '37% 4.5%', amp: 0.85, dir: 1,  dur: '1.65s', ritmo: 'medio' }, // bicicletear, clavo a la izquierda
  { nail: '52% 6.5%', amp: 1.0,  dir: -1, dur: '1.25s', ritmo: 'corto' }, // en la calle
  { nail: '43% 3%',   amp: 0.7,  dir: 1,  dur: '1.75s', ritmo: 'lento' }, // el rostro
  { nail: '59% 2.5%', amp: 1.2,  dir: -1, dur: '1.05s', ritmo: 'corto' }, // sobre papel, el más liviano
]
