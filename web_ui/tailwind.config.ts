import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "var(--background)",
                foreground: "var(--foreground)",
                sidebar: {
                    bg: "var(--sidebar-bg)",
                    hover: "var(--sidebar-hover)",
                    text: "var(--sidebar-text)",
                }
            },
        },
    },
    plugins: [],
};
export default config;
