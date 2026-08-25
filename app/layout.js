import Header from './Header'
import './globals.css'

export const metadata = {
  title: 'Marcel Dioverti',
}

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <Header />
        {children}
      </body>
    </html>
  )
}
