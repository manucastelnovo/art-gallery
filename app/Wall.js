'use client'

import { useEffect, useLayoutEffect, useRef, useState } from 'react'
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
function Piece({ src, alt, left, top, width, rot, sx, sy, sb, motion, onSelect, selected }) {
  const [swinging, setSwinging] = useState(false)

  return (
    <button
      type="button"
      className={`${styles.piece} ${selected?.travel ? `${styles.lifted} ${selected.closing ? styles.returningPiece : ''}` : ''} ${swinging ? `${styles.swinging} ${styles[motion.ritmo]}` : ''}`}
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
        ...(selected?.travel
          ? {
              '--travel-x': `${selected.travel.x}px`,
              '--travel-y': `${selected.travel.y}px`,
              '--travel-scale': selected.travel.scale,
              '--origin-left': `${selected.origin.left}px`,
              '--origin-top': `${selected.origin.top}px`,
              '--origin-width': `${selected.origin.width}px`,
            }
          : {}),
      }}
      onPointerEnter={() => setSwinging(true)}
      onAnimationEnd={() => setSwinging(false)}
      onClick={(event) => {
        const bounds = event.currentTarget.getBoundingClientRect()
        onSelect({
          src,
          alt,
          origin: {
            x: bounds.left + bounds.width / 2,
            y: bounds.top + bounds.height / 2,
            left: bounds.left,
            top: bounds.top,
            width: bounds.width,
            height: bounds.height,
          },
        })
      }}
      aria-label={`Ver obra: ${alt}`}
    >
      <img src={src} alt="" draggable={false} />
    </button>
  )
}

export default function Wall({ muro = null, marcas = true }) {
  const [selected, setSelected] = useState(null)
  const [closing, setClosing] = useState(false)
  const [arrived, setArrived] = useState(false)
  const [travel, setTravel] = useState(null)
  const closeButtonRef = useRef(null)
  const artFrameRef = useRef(null)
  const closeTimerRef = useRef(null)

  const finishClose = () => {
    if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current)
    closeTimerRef.current = null
    setSelected(null)
    setArrived(false)
    setClosing(false)
    setTravel(null)
  }

  const closeViewer = () => {
    if (!selected || closing) return
    if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current)
    setArrived(true)
    setClosing(true)
    closeTimerRef.current = window.setTimeout(finishClose, 1400)
  }

  useEffect(() => {
    document.body.classList.toggle('viewer-open', Boolean(selected))

    if (!selected) return undefined

    const closeOnEscape = (event) => {
      if (event.key === 'Escape') closeViewer()
    }

    document.addEventListener('keydown', closeOnEscape)
    closeButtonRef.current?.focus()
    return () => {
      document.removeEventListener('keydown', closeOnEscape)
      document.body.classList.remove('viewer-open')
    }
  }, [selected])

  useLayoutEffect(() => {
    if (!selected || !artFrameRef.current) return undefined

    const frame = artFrameRef.current.getBoundingClientRect()
    setTravel({
      x: frame.left + frame.width / 2 - selected.origin.x,
      y: frame.top + frame.height / 2 - selected.origin.y,
      scale: Math.min(
        frame.width / selected.origin.width,
        (window.innerHeight * 0.63) / selected.origin.height,
      ),
    })
    return undefined
  }, [selected])

  return (
    <div
      className={`${styles.wall} ${selected && arrived ? styles.hasViewer : ''}`}
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
            <Piece
              key={p.src}
              {...p}
              motion={MOTION[i]}
              onSelect={(work) => {
                if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current)
                setClosing(false)
                setArrived(false)
                setTravel(null)
                setSelected({ ...work, closing: false })
                closeTimerRef.current = window.setTimeout(() => {
                  setArrived(true)
                  closeTimerRef.current = null
                }, 1400)
              }}
              selected={selected?.src === p.src ? { ...selected, closing, travel } : null}
            />
          ))}
        </div>
      </div>
      {selected && (
        <div
          className={`${styles.viewer} ${arrived ? styles.viewerReady : ''} ${closing ? styles.viewerClosing : ''}`}
          role="presentation"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) closeViewer()
          }}
        >
          <section className={styles.selectedWork} role="dialog" aria-modal="true" aria-label="Obra seleccionada">
            <button
              ref={closeButtonRef}
              type="button"
              className={`${styles.close} ${arrived ? '' : styles.controlHidden}`}
              onPointerDown={(event) => {
                event.preventDefault()
                event.stopPropagation()
                closeViewer()
              }}
              onClick={(event) => event.stopPropagation()}
              aria-label="Cerrar obra"
            >
              <span aria-hidden="true">×</span>
            </button>
            <div
              className={styles.artFrame}
              ref={artFrameRef}
              style={{ aspectRatio: `${selected.origin.width} / ${selected.origin.height}` }}
              aria-hidden="true"
            />
            <div className={`${styles.description} ${arrived ? styles.descriptionReady : ''}`}>
              <span className={styles.kicker}>Obra seleccionada</span>
              <p>{selected.alt}</p>
            </div>
          </section>
        </div>
      )}
    </div>
  )
}
