import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import esTranslations from './locales/es.json'
import enTranslations from './locales/en.json'

// Configuración de i18next
i18n
  // Detectar idioma del navegador
  .use(LanguageDetector)
  // Inicializar React
  .use(initReactI18next)
  // Configurar
  .init({
    resources: {
      es: { translation: esTranslations },
      en: { translation: enTranslations }
    },
    fallbackLng: 'es',
    defaultNS: 'translation',
    interpolation: {
      escapeValue: false // React ya protege contra XSS
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage']
    }
  })

export default i18n
