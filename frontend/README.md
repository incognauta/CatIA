# CatIA Frontend - Fase 5

Frontend MVP para PDF_IA_Rework - Chat inteligente con documentos usando Groq + RAG.

## 🚀 Stack

- **React 19** - Framework UI
- **Vite** - Build tool (rápido)
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Zustand** - State management
- **TanStack Query** - Data fetching
- **Axios** - HTTP client
- **React Router** - Navigation
- **Lucide Icons** - Icons

## 📁 Estructura

```
src/
├── components/
│   ├── auth/          # Componentes autenticación
│   ├── layout/        # Header, Sidebar, Layout
│   ├── notebook/      # Canvas editable
│   ├── chat/          # Chat sidebar y mensajes
│   └── documents/     # Modal de documentos
├── pages/             # Página raíces (Login, Dashboard, Notebook)
├── hooks/             # Hooks personalizados
├── stores/            # Zustand stores
├── api/               # API endpoints
├── types/             # Interfaces TypeScript
├── ui/                # Componentes UI reutilizables
└── App.tsx            # App principal
```

## 🎨 Colores CatIA

- **Purple**: #7C3AED
- **Pink**: #EC4899
- **Gold**: #F59E0B
- **Dark**: #0F172A
- **Light**: #F1F5F9

## 🛠️ Configuración

### 1. Instalar dependencias

```bash
npm install
```

### 2. Variables de entorno

Copia `.env.example` a `.env` y ajusta:

```
VITE_API_URL=http://localhost:8001/api/v1
```

### 3. Desarrollo

```bash
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173)

## 🔒 Autenticación

- JWT en localStorage
- Interceptor automático en requests
- Redirect a login si 401

## 📝 Notas para desarrollo

- `@` es alias para `src/`
- Los hooks de React Query se cachean automáticamente
- Zustand stores se persistenAutomáticamente
- Tailwind tiene colores CatIA personalizados

## 📦 Scripts

- `npm run dev` - Desarrollo
- `npm run build` - Build producción
- `npm run preview` - Preview build local
- `npm run lint` - Lint con ESLint

---

**Fase 5A** - Setup + Auth + Dashboard (En desarrollo)
