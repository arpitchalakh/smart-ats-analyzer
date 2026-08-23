import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Smart ATS Analyzer',
  description: 'Job-specific resume analysis, ATS insights, keyword gaps and practical recommendations.'
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
