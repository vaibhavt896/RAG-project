import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'LinkedIn Intelligence Agent',
  description: 'Signal-first LinkedIn automation with AI-powered outreach',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </head>
      <body>
        <div style={{ display: 'flex', minHeight: '100vh' }}>
          <Sidebar />
          <main style={{ flex: 1, marginLeft: 220, padding: '28px 32px', maxWidth: 'calc(100vw - 220px)', overflow: 'auto' }}>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
