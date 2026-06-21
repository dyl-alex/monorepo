import type { Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { cookies } from "next/headers";

import { cn } from "@repo/ui/lib/utils";

import { SiteHeader } from "@/components/site-header";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const META_THEME_COLORS = {
  light: "#ffffff",
  dark: "#09090b",
};

export const viewport: Viewport = {
  themeColor: META_THEME_COLORS.light,
};

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const fontVariables = `${geistSans.variable} ${geistMono.variable}`;

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const activeThemeValue = cookieStore.get("active_theme")?.value;
  const isScaled = activeThemeValue?.endsWith("-scaled");

  return (
    <html lang="en">
      <body
        className={cn(
          "bg-background overflow-x-hidden overscroll-none font-sans antialiased",
          activeThemeValue ? `theme-${activeThemeValue}` : "",
          isScaled ? "theme-scaled" : "",
          fontVariables,
        )}
      >
        <SiteHeader />
        <main>{children}</main>
      </body>
    </html>
  );
}
