/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ["recharts"]
  },
  webpack: (config) => {
    config.watchOptions = {
      ...config.watchOptions,
      ignored: ["**/node_modules/**", "**/.venv/**", "**/.next/**", "**/UIref/**", "**/.corepack/**"]
    };
    return config;
  }
};

export default nextConfig;
