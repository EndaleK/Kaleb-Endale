import { ClerkProvider } from '@clerk/nextjs'
import "./globals.css"
import type { Metadata } from "next"
import { Inter } from 'next/font/google'
import { ThemeProvider } from './ThemeContext';

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: "Calendar",
  description: "A shared calendar for events and activities",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <ThemeProvider>
          <body className={inter.className}>{children}</body>
        </ThemeProvider>
      </html>
    </ClerkProvider>
  )
}
