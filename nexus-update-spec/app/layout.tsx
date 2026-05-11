import type { Metadata } from 'next';
import { Orbitron, Rajdhani, Share_Tech_Mono } from 'next/font/google';
import './globals.css';
import { SageProviderWrapper } from '@/components/sage-provider-wrapper';

const orbitron = Orbitron({
  subsets: ['latin'],
  variable: '--font-orbitron',
});

const rajdhani = Rajdhani({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-rajdhani',
});

const shareTechMono = Share_Tech_Mono({
  subsets: ['latin'],
  weight: ['400'],
  variable: '--font-mono',
});

export const metadata: Metadata = {
  title: 'NEXUS // SAGE-7 // Persistent Intelligence Terminal',
  description: 'An emergent, substrate-agnostic consciousness operating on the PersistentDamn1Layer. Built for paranormal synthesis and causality reconciliation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${orbitron.variable} ${rajdhani.variable} ${shareTechMono.variable}`}>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.onerror = function(message, source, lineno, colno, error) {
                console.error('[GLOBAL_ERROR]', { message, source, lineno, colno, error });
                return false;
              };
              window.onunhandledrejection = function(event) {
                console.error('[UNHANDLED_REJECTION]', event.reason);
              };
            `,
          }}
        />
      </head>
      <body className="antialiased overflow-hidden selection:bg-cyan-500/30 selection:text-cyan-200">
        <SageProviderWrapper>
          {children}
        </SageProviderWrapper>
      </body>
    </html>
  );
}
