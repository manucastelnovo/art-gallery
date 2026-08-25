'use client'

import { useState } from 'react'
import { PIECES } from './wall-data'
import { MOTION } from './wall-motion'
import { MARKS } from './wall-marks'
import styles from './Wall.module.css'

/*
 * Cada obra se mueve al tocarla, como un cuadro colgado que alguien roza.
 *
 * La animación no vive en :hover sino en una clase que se quita en
 * `animationend`: si dependiera del hover, sacar el mouse a mitad del vaivén
 * cortaría el movimiento y el cuadro volvería de golpe. Así el péndulo siempre
 * termina de apagarse solo, que es lo que hace un cuadro de verdad.
 *
 * Los parámetros de movimiento de cada uno están en wall-motion.js.
 */
function Piece({ src, alt, left, top, width, rot, sx, sy, sb, motion }) {
  const [swinging, setSwinging] = useState(false)

  return (
    <img
      src={src}
      alt={alt}
      className={`${styles.piece} ${swinging ? `${styles.swinging} ${styles[motion.ritmo]}` : ''}`}
      style={{
        left: `${left}%`,
        top: `${top}%`,
        width: `${width}%`,
        '--rest': `${rot}deg`,
        '--nail': motion.nail,
        '--amp': motion.amp,
        '--dir': motion.dir,
        '--dur': motion.dur,
        '--sx': sx,
        '--sy': sy,
        '--sb': sb,
      }}
      onPointerEnter={() => setSwinging(true)}
      onAnimationEnd={() => setSwinging(false)}
      draggable={false}
    />
  )
}

export default function Wall({ muro = null, marcas = true }) {
  return (
    <div
      className={styles.wall}
      style={muro ? { '--muro': `url(${muro})` } : undefined}
    >
      <div className={styles.hang}>
        <div className={styles.inner}>
          {/* La clave es el índice: muchas manchas reusan el mismo archivo de
              la biblioteca, así que la ruta no las distingue. La lista es fija
              y nunca se reordena. */}
          {marcas &&
            MARKS.map((m, i) => (
              <img
                key={i}
                src={m.src}
                alt=""
                aria-hidden="true"
                className={styles.mark}
                style={{
                  left: `${m.left}%`,
                  top: `${m.top}%`,
                  width: `${m.width}%`,
                  '--rot': `${m.rot}deg`,
                  '--op': m.op,
                }}
                draggable={false}
              />
            ))}

          {PIECES.map((p, i) => (
            <Piece key={p.src} {...p} motion={MOTION[i]} />
          ))}
        </div>
      </div>
    </div>
  )
}
