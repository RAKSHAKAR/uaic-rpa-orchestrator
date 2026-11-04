/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    workerThreads: false,
    cpus: 1,
  },
  async rewrites() {
    const rawBackendUrl = process.env.INTERNAL_API_URL || process.env.BACKEND_URL || "http://127.0.0.1:8000";
    const internalBackendUrl = rawBackendUrl.replace(/\/+$/, "");
    return [
      {
        source: "/api/v1/:path*",
        destination: `${internalBackendUrl}/api/v1/:path*`,
      },
      {
        source: "/uploads/:path*",
        destination: `${internalBackendUrl}/api/v1/settings/logo/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
