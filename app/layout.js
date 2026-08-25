import Header from './Header'
import Wall from './Wall'
import './globals.css'

export const metadata = {
  title: 'Marcel Dioverti',
}

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <Header />
        <Wall />
        {children}
      </body>
    </html>
  )
}
