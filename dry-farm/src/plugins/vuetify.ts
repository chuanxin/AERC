/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { VStepperVertical } from 'vuetify/labs/VStepperVertical'

// Composables
import { createVuetify } from 'vuetify'
import { md1 } from 'vuetify/blueprints'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  components: {
    VStepperVertical,
  },
  theme: {
    themes: {
      light: {
        dark: false,
        colors: {
          // primary: '#4CAF50',
          // secondary: '#FF9800',
          // 'primary-light': '#81C784',
          // 'primary-dark': '#388E3C',
          // 'secondary-ight': '#FFB74D',
          // 'secondary-dark': '#F57C00',
          // background: '#F5F5F5',
          // surface: '#FFFFFF',
          // error: '#F44336',
          // typography: '#212121',
          // iconography: '#757575'
          primary: '#0B6E99',
          secondary: '#8CC152',
          'primary-lighten': '#1A8BB2',
          'primary-darken': '#00796B',
          'secondary-ighten': '#FFD54F',
          'secondary-darken': '#FFA000',
          background: '#F0F0F0',
          // background: '#FFFFFF',
          surface: '#FFFFFF',
          error: '#E74C3C',
          typography: '#424242',
          iconography: '#757575'
        }
      }
    },
    defaultTheme: 'light',
  },
  blueprint: md1,
})
