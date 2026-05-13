import { useState } from 'react'
import { ChevronDown, MessageCircle, FileText, BookOpen, Zap } from 'lucide-react'

interface FAQItem {
  id: string
  category: 'general' | 'usage' | 'documents' | 'ai'
  question: string
  answer: string
  icon?: React.ReactNode
}

const faqData: FAQItem[] = [
  {
    id: 'general-1',
    category: 'general',
    question: '¿Qué es CatIA?',
    answer: 'CatIA es una plataforma inteligente para gestionar y analizar documentos usando IA. Permite organizar documentos en notebooks, extraer información automáticamente y conversar con tus documentos usando un asistente de IA.',
    icon: <MessageCircle className="w-5 h-5" />
  },
  {
    id: 'general-2',
    category: 'general',
    question: '¿Cómo puedo crear una nueva cuenta?',
    answer: 'Haz clic en "Registrarse" en la página de inicio. Ingresa tu email, nombre de usuario y contraseña. Recibirás un email de confirmación para verificar tu cuenta.',
    icon: <MessageCircle className="w-5 h-5" />
  },
  {
    id: 'general-3',
    category: 'general',
    question: '¿CatIA es gratuito?',
    answer: 'Sí, CatIA ofrece un plan gratuito con funcionalidades básicas. También disponemos de planes de pago para usuarios con necesidades más avanzadas.',
    icon: <MessageCircle className="w-5 h-5" />
  },
  {
    id: 'usage-1',
    category: 'usage',
    question: '¿Cómo organizo mis documentos?',
    answer: 'Puedes organizar documentos en "Notebooks". Desde el dashboard, haz clic en "Crear Notebook" para crear una nueva carpeta. Luego, carga documentos en el notebook que desees.',
    icon: <BookOpen className="w-5 h-5" />
  },
  {
    id: 'usage-2',
    category: 'usage',
    question: '¿Cómo converso con mis documentos?',
    answer: 'Accede a un notebook y escribe tu pregunta en el chat. CatIA analizará automáticamente los documentos cargados y proporcionará respuestas basadas en su contenido.',
    icon: <BookOpen className="w-5 h-5" />
  },
  {
    id: 'usage-3',
    category: 'usage',
    question: '¿Puedo personalizar mis notebooks?',
    answer: 'Sí, puedes asignar nombres y descripciones personalizadas a tus notebooks. También puedes seleccionar colores e iconos para identificarlos fácilmente.',
    icon: <BookOpen className="w-5 h-5" />
  },
  {
    id: 'documents-1',
    category: 'documents',
    question: '¿Qué tipos de documentos puedo cargar?',
    answer: 'CatIA soporta PDF, DOCX, TXT e imágenes (JPG, PNG). Los archivos deben tener un tamaño máximo de 50MB.',
    icon: <FileText className="w-5 h-5" />
  },
  {
    id: 'documents-2',
    category: 'documents',
    question: '¿Cómo extraigo información de mis documentos?',
    answer: 'Puedes hacer preguntas sobre tus documentos en el chat. CatIA extrae automáticamente la información relevante y la presenta en un resumen conciso.',
    icon: <FileText className="w-5 h-5" />
  },
  {
    id: 'documents-3',
    category: 'documents',
    question: '¿Puedo eliminar documentos?',
    answer: 'Sí, en la sección de documentos puedes eliminar cualquier archivo. Ten en cuenta que esta acción es irreversible.',
    icon: <FileText className="w-5 h-5" />
  },
  {
    id: 'ai-1',
    category: 'ai',
    question: '¿Cómo personalizo las respuestas de IA?',
    answer: 'Ve a Configuración > Configuración de IA. Aquí puedes ajustar el modelo de IA, la creatividad (temperatura) y la longitud máxima de las respuestas.',
    icon: <Zap className="w-5 h-5" />
  },
  {
    id: 'ai-2',
    category: 'ai',
    question: '¿Qué es la "temperatura" en IA?',
    answer: 'La temperatura controla cuán creativas o determinísticas son las respuestas. Valores bajos (cercanos a 0) producen respuestas más predecibles. Valores altos producen respuestas más variadas y creativas.',
    icon: <Zap className="w-5 h-5" />
  },
  {
    id: 'ai-3',
    category: 'ai',
    question: '¿Qué son los tokens?',
    answer: 'Los tokens son unidades de texto que utiliza la IA. Aproximadamente, 1000 tokens equivalen a 750 palabras. El límite de tokens controla la longitud máxima de las respuestas.',
    icon: <Zap className="w-5 h-5" />
  },
]

export default function HelpPage() {
  const [selectedCategory, setSelectedCategory] = useState<'all' | FAQItem['category']>('all')
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())

  const categories = [
    { value: 'all', label: 'Todo', icon: MessageCircle },
    { value: 'general', label: 'General', icon: MessageCircle },
    { value: 'usage', label: 'Uso', icon: BookOpen },
    { value: 'documents', label: 'Documentos', icon: FileText },
    { value: 'ai', label: 'IA', icon: Zap },
  ]

  const filteredFAQ = selectedCategory === 'all' 
    ? faqData 
    : faqData.filter(item => item.category === selectedCategory)

  const toggleItem = (id: string) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedItems(newExpanded)
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-3xl font-bold text-catia-light mb-2">Ayuda y Preguntas Frecuentes</h1>
        <p className="text-catia-light/60">Encuentra respuestas a las preguntas más comunes sobre CatIA</p>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map(cat => {
          const Icon = cat.icon
          return (
            <button
              key={cat.value}
              onClick={() => setSelectedCategory(cat.value as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                selectedCategory === cat.value
                  ? 'bg-catia-purple text-white'
                  : 'bg-catia-dark/50 text-catia-light border border-catia-purple/30 hover:border-catia-purple/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {cat.label}
            </button>
          )
        })}
      </div>

      {/* FAQ Items */}
      <div className="space-y-3">
        {filteredFAQ.map(item => (
          <div
            key={item.id}
            className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl overflow-hidden"
          >
            <button
              onClick={() => toggleItem(item.id)}
              className="w-full flex items-start gap-4 p-6 hover:bg-catia-dark/60 transition-colors text-left group"
            >
              <div className="text-catia-purple group-hover:text-catia-gold transition-colors flex-shrink-0 mt-1">
                {item.icon}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-catia-light font-semibold group-hover:text-catia-gold transition-colors">
                  {item.question}
                </h3>
              </div>
              <ChevronDown
                className={`w-5 h-5 text-catia-purple/60 flex-shrink-0 transition-transform ${
                  expandedItems.has(item.id) ? 'rotate-180' : ''
                }`}
              />
            </button>

            {/* Answer */}
            {expandedItems.has(item.id) && (
              <div className="px-6 pb-6 border-t border-catia-purple/10 pt-4">
                <p className="text-catia-light/80 leading-relaxed">
                  {item.answer}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Contact Support */}
      <div className="mt-12 bg-catia-dark/50 border border-catia-gold/30 rounded-xl p-8">
        <div className="flex items-start gap-4">
          <MessageCircle className="w-6 h-6 text-catia-gold flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-catia-light font-semibold text-lg mb-2">¿No encuentras lo que buscas?</h3>
            <p className="text-catia-light/70 mb-4">
              Si tienes otras preguntas o necesitas ayuda adicional, no dudes en contactarnos.
            </p>
            <button className="bg-catia-gold hover:bg-catia-gold/80 text-catia-dark px-6 py-2 rounded-lg font-semibold transition-colors">
              Contactar Soporte
            </button>
          </div>
        </div>
      </div>

      {/* Resources */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-catia-light mb-6">Recursos Adicionales</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <a
            href="#"
            className="bg-catia-dark/40 border border-catia-purple/20 hover:border-catia-purple/60 rounded-xl p-6 transition-all group"
          >
            <h3 className="text-catia-light font-semibold group-hover:text-catia-gold transition-colors mb-2">
              Documentación Completa
            </h3>
            <p className="text-catia-light/60 text-sm">
              Accede a la documentación técnica completa de CatIA
            </p>
          </a>

          <a
            href="#"
            className="bg-catia-dark/40 border border-catia-purple/20 hover:border-catia-purple/60 rounded-xl p-6 transition-all group"
          >
            <h3 className="text-catia-light font-semibold group-hover:text-catia-gold transition-colors mb-2">
              Tutoriales en Video
            </h3>
            <p className="text-catia-light/60 text-sm">
              Aprende a usar CatIA con nuestros tutoriales paso a paso
            </p>
          </a>

          <a
            href="#"
            className="bg-catia-dark/40 border border-catia-purple/20 hover:border-catia-purple/60 rounded-xl p-6 transition-all group"
          >
            <h3 className="text-catia-light font-semibold group-hover:text-catia-gold transition-colors mb-2">
              Blog
            </h3>
            <p className="text-catia-light/60 text-sm">
              Mantente actualizado con noticias y consejos sobre IA
            </p>
          </a>

          <a
            href="#"
            className="bg-catia-dark/40 border border-catia-purple/20 hover:border-catia-purple/60 rounded-xl p-6 transition-all group"
          >
            <h3 className="text-catia-light font-semibold group-hover:text-catia-gold transition-colors mb-2">
              Comunidad
            </h3>
            <p className="text-catia-light/60 text-sm">
              Conecta con otros usuarios y comparte experiencias
            </p>
          </a>
        </div>
      </div>
    </div>
  )
}
