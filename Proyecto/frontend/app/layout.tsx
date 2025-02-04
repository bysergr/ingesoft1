import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const interFont = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "NaurBotMX - Naurat",
  description: "A bot created as a project for the IngeSoft class",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${interFont.className} text-black bg-neutral-100 antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
