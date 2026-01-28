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
            outDir: 'dist',
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
            host: "127.0.0.1",
            port: 5000,
            strictPort: false,
        },
    };
});