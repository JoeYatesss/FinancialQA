import './globals.css'
import Link from 'next/link'
import { NavLink } from '@/components/nav-link'

export const metadata = {
  title: 'Financial Chat',
  description: 'AI-powered chat platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full antialiased font-space-grotesk">
        <div className="flex min-h-screen bg-background text-white">
          {/* Sidebar */}
          <div className="fixed inset-y-0 z-50 flex w-72 flex-col">
            <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-background px-6 pb-4 border-r border-secondary/20">
              <div className="flex h-16 shrink-0 items-center">
                <Link href="/" className="flex items-center space-x-2">
                  <span className="text-2xl font-bold">
                    finance<span className="text-[#d8ff00]">.ai</span>
                  </span>
                </Link>
              </div>
              
              <nav className="flex flex-1 flex-col">
                <ul role="list" className="flex flex-1 flex-col gap-y-7">
                  <li>
                    <ul role="list" className="-mx-2 space-y-1">
                      <li>
                        <NavLink href="/">
                          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" 
                            />
                          </svg>
                          Chat
                        </NavLink>
                      </li>
                      <li>
                        <NavLink href="/system-architecture">
                          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
                            />
                          </svg>
                          Architecture
                        </NavLink>
                      </li>
                      <li>
                        <NavLink href="/metrics">
                          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" 
                            />
                          </svg>
                          Metrics
                        </NavLink>
                      </li>
                    </ul>
                  </li>
                </ul>
              </nav>

              <div className="mt-auto">
                <div className="flex items-center gap-x-3 rounded-lg bg-background/50 p-3 border border-secondary/20">
                  <div className="h-8 w-8 rounded-full bg-background flex items-center justify-center">
                    <span className="text-sm font-medium text-[#d8ff00]">AI</span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[#d8ff00]">Finance AI</p>
                    <p className="text-xs text-[#d8ff00]/70">v1.0.0</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <main className="pl-72 w-full">
            <div className="h-full">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  )
}
