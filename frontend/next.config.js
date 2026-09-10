/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    workerThreads: false,
    cpus: 1,
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://127.0.0.1:8000/api/v1/:path*",
      },
      {
        source: "/uploads/:path*",
        destination: "http://127.0.0.1:8000/api/v1/settings/logo/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
