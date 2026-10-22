import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',

    video: false,

    setupNodeEvents() {
      // No custom Node events required.
    },
  },
})
