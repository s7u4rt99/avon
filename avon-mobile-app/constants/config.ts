export const BASE_URL =
  process.env.ENVIRONMENT === "dev"
    ? "http://127.0.0.1:8000"
    : "https://avon-seven.vercel.app";
