import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "AI Design Tool - Create Stunning Designs with AI",
    template: "%s | AI Design Tool",
  },
  description: "Professional AI-powered design platform combining Canva-style graphic design, Figma-style UI/UX tools, and intelligent logo generation. Create beautiful designs in minutes.",
  keywords: ["AI design", "graphic design", "UI/UX design", "logo maker", "design tool", "Canva alternative", "Figma alternative"],
  authors: [{ name: "AI Design Tool" }],
  creator: "AI Design Tool",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://aidesigntool.com",
    siteName: "AI Design Tool",
    title: "AI Design Tool - Create Stunning Designs with AI",
    description: "Professional AI-powered design platform. Create graphics, UI/UX mockups, and logos with the power of artificial intelligence.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "AI Design Tool",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Design Tool - Create Stunning Designs with AI",
    description: "Professional AI-powered design platform. Create graphics, UI/UX mockups, and logos with the power of artificial intelligence.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    google: "your-google-verification-code",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
