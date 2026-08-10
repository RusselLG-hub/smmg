export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',

  app: {
    head: {
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' },
        { rel: 'apple-touch-icon', href: '/images/ssmg-logo.webp' },
      ],
    },
  },

  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    'nuxt-lucide-icons',
  ],

  runtimeConfig: {
    apiInternalBaseUrl: '',
    public: {
      apiBaseUrl: '',
    },
  },

  css: ['~/assets/css/main.css'],

  devtools: { enabled: true },
})
