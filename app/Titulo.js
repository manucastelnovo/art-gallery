'use client'

import { TITULO } from './title-data'
import styles from './Titulo.module.css'

/*
 * "LOS COLORES DE LA SOMBRA", pintándose letra por letra.
 *
 * Ninguna letra está compuesta ni tipografiada: son sus veinte pinceladas,
 * recortadas de la portada de la serie con su ancho, su alto y la altura
 * desigual a la que las apoyó en el renglón.
 */
export default function Titulo() {
  let orden = 0

  return (
    <h1 className={styles.titulo}>
      <span className="sr-only">Los colores de la sombra</span>
      {TITULO.map((l, k) =>
        l.espacio ? (
          <span key={k} className={styles.espacio} aria-hidden="true" />
        ) : (
          <span
            key={k}
            className={styles.letra}
            aria-hidden="true"
            style={{
              '--src': `url(${l.src})`,
              '--w': l.w,
              '--h': l.h,
              '--dy': l.dy,
              '--i': orden++,
            }}
          />
        )
      )}
    </h1>
  )
}
