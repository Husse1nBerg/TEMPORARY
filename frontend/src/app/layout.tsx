
// Root layout for the entire application


import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CROPS Price Tracker - Real-time Egyptian Grocery Price Monitoring',
  description: 'Track and monitor grocery prices across Egyptian markets in real-time. Get instant updates, price trends, and stock availability for agricultural products.',
  keywords: 'grocery prices, Egypt, price tracking, agricultural products, CROPS, SPC Agriculture',
  authors: [{ name: 'CROPS Egypt' }],
  openGraph: {
    title: 'CROPS Price Tracker',
    description: 'Real-time grocery price monitoring for Egyptian markets',
    url: 'https://cropstracker.com',
    siteName: 'CROPS Price Tracker',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'CROPS Price Tracker',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'CROPS Price Tracker',
    description: 'Real-time grocery price monitoring for Egyptian markets',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#333',
              color: '#fff',
            },
            success: {
              style: {
                background: '#10B981',
              },
            },
            error: {
              style: {
                background: '#EF4444',
              },
            },
          }}
        />
      </body>
    </html>
  );
}
