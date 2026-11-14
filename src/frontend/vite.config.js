import { defineConfig } from 'vite';
export default defineConfig({ server: { proxy: { '/api': 'http://127.0.0.1:5000' } }, test: {environment:'jsdom',setupFiles:['./src/test/setup.js'],include:['src/**/*.test.jsx']} });
