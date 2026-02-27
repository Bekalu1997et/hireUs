/**@type {import('next').NextConfig}*/
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverComponentsExternalPackages: ['@prisma/client'],
  },
  output: 'standalone',
};

module.exports = nextConfig;

