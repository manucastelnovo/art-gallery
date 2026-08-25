/** @type {import('next').NextConfig} */
const nextConfig = {
  // Sin esto Turbopack sube buscando un lockfile y toma C:\Users\manue como raíz.
  turbopack: {
    root: import.meta.dirname,
  },
  // No generar AGENTS.md / CLAUDE.md automáticamente.
  agentRules: false,
}

export default nextConfig
