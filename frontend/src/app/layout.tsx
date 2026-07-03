import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AidBot",
  description: "Internal support Q&A workspace",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
