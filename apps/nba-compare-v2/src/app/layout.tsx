import type { Viewport } from "next";
import { cookies } from "next/headers";

import { cn } from "@repo/ui/lib/utils";

import { SiteHeader } from "@/components/site-header";
import { TRPCReactProvider } from "@/trpc/client";

import "./globals.css";

const META_THEME_COLORS = {
  light: "#ffffff",
  dark: "#09090b",
};

export const viewport: Viewport = {
  themeColor: META_THEME_COLORS.light,
};

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
        )}
      >
        <TRPCReactProvider>
          <SiteHeader />
          <main>{children}</main>
        </TRPCReactProvider>
      </body>
    </html>
  );
}
