'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface NavLinkProps {
  href: string
  children: React.ReactNode
  className?: string
}

export function NavLink({ href, children, className = '' }: NavLinkProps) {
  const pathname = usePathname()
  const isActive = pathname === href

  return (
    <Link 
      href={href}
      className={`flex items-center px-6 py-3 transition-colors ${
        isActive ? 'text-[#d8ff00]' : 'text-gray-100 hover:text-[#d8ff00]'
      } ${className}`}
    >
      {children}
    </Link>
  )
} 