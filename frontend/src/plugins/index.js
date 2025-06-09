// Composables
import { createPinia } from 'pinia' // 確保這行存在
import router from '../router'
import vuetify from './vuetify'

export function registerPlugins (app) {
  app
    .use(createPinia()) // 確保這行存在，並且被 app.use()
    .use(vuetify)
    .use(router)
}