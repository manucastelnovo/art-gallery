import styles from './Header.module.css'

/*
 * Las palabras están pintadas con su propio pincel: cada letra se recortó del
 * lienzo donde ella escribió a mano "LOS COLORES DE LA SOMBRA", y las cinco que
 * no existían (H U T G Y) se armaron con pedazos de esos mismos trazos.
 * Ver scripts/ y dibujos/fotosmarceserieloscoloresdelasombra.
 */
const ITEMS = [
  { label: 'Home', href: '/', src: '/nav/home.png', ar: 2.725 },
  { label: 'About me', href: '/about', src: '/nav/about.png', ar: 5.427 },
  { label: 'Gallery', href: '/gallery', src: '/nav/gallery.png', ar: 4.454 },
]

export default function Header() {
  return (
    <header className={styles.header}>
      <nav className={styles.nav}>
        {ITEMS.map(({ label, href, src, ar }) => (
          <a
            key={href}
            href={href}
            className={styles.item}
            style={{ '--ar': ar, '--src': `url(${src})` }}
          >
            <span className="sr-only">{label}</span>
          </a>
        ))}
      </nav>
    </header>
  )
}
