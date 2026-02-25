import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig(({ mode }) => {
    const production = mode === 'production';
    
    return {
        plugins: [
            svelte({
                compilerOptions: {
                    dev: !production
                }
            })
        ],
        css: {
            postcss: './postcss.config.cjs'
        },
        build: {
            outDir: '../myapp/static/frontend',
            emptyOutDir: true,
            sourcemap: true,
            minify: production ? 'terser' : false,
            rollupOptions: {
                output: {
                    entryFileNames: 'bundle.js',
                    assetFileNames: (assetInfo) => {
                        // Rename the main CSS file to bundle.css
                        if (assetInfo.name === 'style.css' || assetInfo.name.endsWith('.css')) {
                            return 'bundle.css';
                        }
                        return assetInfo.name;
                    }
                }
            }
        },

        server: {
            proxy: {
                '/api': {
                    target: 'http://localhost:8000',
                    changeOrigin: true,
                    secure: false,
                    configure: (proxy, options) => {
                        proxy.on('proxyRes', (proxyRes, req, res) => {
                            // If Django redirects to login, redirect browser to Django
                            if (proxyRes.statusCode === 302 && proxyRes.headers.location?.includes('/accounts/login/')) {
                                res.writeHead(302, {
                                    Location: `http://localhost:8000${proxyRes.headers.location}`
                                });
                                res.end();
                            }
                        });
                    }
                },
                '/accounts': {
                    target: 'http://localhost:8000',
                    changeOrigin: true,
                    secure: false
                },
                '/static': {
                    target: 'http://localhost:8000',
                    changeOrigin: true,
                    secure: false
                }
            }
        },
    };
});