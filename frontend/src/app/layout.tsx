import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG System — Intelligent Document Search",
  description: "Production RAG system with hybrid search, cross-encoder re-ranking, citation tracking and evaluation — powered by Google Gemini",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
