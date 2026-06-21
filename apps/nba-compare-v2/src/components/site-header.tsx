"use client";

import Link from "next/link";
import { BarChart3, Swords } from "lucide-react";

import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@repo/ui/components/navigation-menu";

const compareLinks = [
  {
    href: "/compare",
    title: "Player comparison",
    description: "Compare player performance and statistics side by side.",
  },
  {
    href: "/compare",
    title: "Season statistics",
    description: "Review the numbers that matter across NBA seasons.",
  },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="flex shrink-0 items-center gap-2 font-semibold tracking-tight"
        >
          <BarChart3 className="size-5" aria-hidden="true" />
          <span>NBA Compare</span>
        </Link>

        <NavigationMenu viewport={false}>
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuLink
                asChild
                className={navigationMenuTriggerStyle()}
              >
                <Link href="/">Home</Link>
              </NavigationMenuLink>
            </NavigationMenuItem>

            <NavigationMenuItem>
              <NavigationMenuTrigger>Compare</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid w-[min(24rem,calc(100vw-2rem))] gap-1">
                  {compareLinks.map((link) => (
                    <li key={link.title}>
                      <NavigationMenuLink asChild>
                        <Link href={link.href}>
                          <span className="font-medium leading-none">
                            {link.title}
                          </span>
                          <span className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                            {link.description}
                          </span>
                        </Link>
                      </NavigationMenuLink>
                    </li>
                  ))}
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            <NavigationMenuItem>
              <NavigationMenuTrigger>Battle</NavigationMenuTrigger>
              <NavigationMenuContent>
                <div className="w-[min(20rem,calc(100vw-2rem))] p-2">
                  <div className="flex gap-3 rounded-md bg-muted/50 p-3">
                    <Swords
                      className="mt-0.5 size-5 shrink-0 text-muted-foreground"
                      aria-hidden="true"
                    />
                    <div className="space-y-1">
                      <p className="text-sm font-medium leading-none">
                        Battle mode
                      </p>
                      <p className="text-sm leading-snug text-muted-foreground">
                        Head-to-head player battles are coming soon.
                      </p>
                    </div>
                  </div>
                </div>
              </NavigationMenuContent>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
      </div>
    </header>
  );
}
