import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    transpilePackages: ["@repo/ui"], // ensures UI package is compiled
};

export default nextConfig;
