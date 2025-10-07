/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// HunInn Font (粉圓體) - 僅用於 login 頁面
const style = document.createElement('style')
style.textContent = `
  @font-face {
    font-family: 'HunInn';
    src: url(https://cdn.jsdelivr.net/gh/marsnow/open-huninn-font@1.1/font/jf-openhuninn.woff2) format('woff2'),
         url(https://cdn.jsdelivr.net/gh/marsnow/open-huninn-font@1.1/font/jf-openhuninn.woff) format('woff'),
         url(https://cdn.jsdelivr.net/gh/marsnow/open-huninn-font@1.1/font/jf-openhuninn.ttf) format('truetype');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
  }
`
document.head.appendChild(style)
// import { VStepperVertical } from 'vuetify/labs/VStepperVertical'
import { VDateInput } from 'vuetify/labs/VDateInput'

// Composables
import { createVuetify } from 'vuetify'
import { md1 } from 'vuetify/blueprints'

// FontAwesome
// import { aliases as faAliases, fa } from 'vuetify/iconsets/fa'

// Material Design Icons
// import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  components: {
    // VStepperVertical,
    VDateInput,
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
          primary: '#3ea0a3',
          secondary: '#8CC152',
          'primary-lighten': '#5ebdc0',
          'primary-darken': '#358b8e',
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
  icons: {
    // defaultSet: 'mdi',
    // aliases: {
    //   ...faAliases,
    // },
    // sets: {
    //   fa,
    // },
  },
  blueprint: md1,
})
