import type { NextConfig } from "next";
import path from "path";

// Pin workspace root so Next does not walk up to a parent folder
const projectRoot = path.join(__dirname);

const nextConfig: NextConfig = {
  reactCompiler: true,

  // Required by frontend/Dockerfile (copies .next/standalone)
  output: "standalone",

  outputFileTracingRoot: projectRoot,
  turbopack: {
    root: projectRoot,
  },

  images: {
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "picsum.photos" },
      { protocol: "https", hostname: "*.cloudinary.com" },
      { protocol: "https", hostname: "*.amazonaws.com" },
    ],
  },

  // API proxy for development when NEXT_PUBLIC_API_URL is unset
  async rewrites() {
    if (process.env.NEXT_PUBLIC_API_URL) {
      return [];
    }
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;