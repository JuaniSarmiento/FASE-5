# 🎨 Frontend Minimalista - Guía de Uso

## 📋 Índice
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Sistema de Diseño](#sistema-de-diseño)
- [Componentes](#componentes)
- [Páginas](#páginas)
- [Correcciones Aplicadas](#correcciones-aplicadas)

## 🏗️ Estructura del Proyecto

```
frontEnd/src/
├── styles/
│   ├── design-system.css    # Variables y sistema de diseño base
│   ├── layout.css            # Sistema de layout y navegación
│   └── components.css        # Componentes UI reutilizables
├── components/
│   └── LayoutMinimal.tsx     # Layout principal minimalista
├── pages/
│   ├── SimulatorsPage.tsx    # ✅ Corregido: página de simuladores
│   └── DashboardPageMinimal.tsx  # Nueva página de inicio
├── index.css                 # Configuración principal de estilos
└── App.tsx                   # ✅ Actualizado para usar LayoutMinimal
```

## 🎨 Sistema de Diseño

### Paleta de Colores Minimalista

**Modo Claro:**
- Primario: `#0a0a0a` (Negro puro)
- Fondo: `#ffffff` (Blanco)
- Secundario: `#fafafa` (Gris muy claro)
- Bordes: `#e5e5e5` (Gris claro)

**Modo Oscuro:**
- Primario: `#ffffff` (Blanco)
- Fondo: `#0a0a0a` (Negro puro)
- Secundario: `#1a1a1a` (Gris muy oscuro)
- Bordes: `#262626` (Gris oscuro)

### Tipografía

- **Fuente principal:** Inter
- **Fuente monoespaciada:** JetBrains Mono / Fira Code
- **Tamaños de texto:** 12px - 28px
- **Pesos disponibles:** 400, 500, 600

### Espaciado

```css
--spacing-xs: 4px
--spacing-sm: 8px
--spacing-md: 16px
--spacing-lg: 24px
--spacing-xl: 32px
--spacing-2xl: 48px
--spacing-3xl: 64px
```

### Radios de Borde

```css
--radius-sm: 4px
--radius-md: 8px
--radius-lg: 12px
--radius-xl: 16px
```

## 🧩 Componentes

### Botones

```tsx
// Botón primario
<button className="btn btn-primary">Click me</button>

// Botón secundario
<button className="btn btn-secondary">Click me</button>

// Botón fantasma
<button className="btn btn-ghost">Click me</button>

// Tamaños
<button className="btn btn-sm">Small</button>
<button className="btn btn-lg">Large</button>
```

### Cards

```tsx
// Card básica
<div className="card">
  <div className="card-header">Header</div>
  <div className="card-body">Content</div>
  <div className="card-footer">Footer</div>
</div>

// Card con hover
<div className="card card-hover">Content</div>
```

### Badges

```tsx
<span className="badge badge-default">Default</span>
<span className="badge badge-success">Success</span>
<span className="badge badge-warning">Warning</span>
<span className="badge badge-error">Error</span>
```

### Inputs

```tsx
<input 
  type="text" 
  className="input" 
  placeholder="Enter text..."
/>
```

## 📄 Páginas

### Layout Principal (LayoutMinimal.tsx)

**Características:**
- ✅ Sidebar fijo con navegación limpia
- ✅ Responsive con menú móvil
- ✅ Toggle de tema (claro/oscuro)
- ✅ Menú de usuario integrado
- ✅ Indicadores visuales de página activa

**Navegación disponible:**
1. Inicio
2. Sesiones
3. Tutor IA
4. Ejercicios
5. Simuladores
6. Riesgos
7. Evaluaciones
8. Trazabilidad
9. Analytics

### Dashboard (DashboardPageMinimal.tsx)

**Características:**
- ✅ Grid de 6 herramientas principales
- ✅ Tarjetas con hover elegante
- ✅ Iconos coloridos por categoría
- ✅ Estado de plataforma en tiempo real

### Simuladores (SimulatorsPage.tsx)

**Características:**
- ✅ **CORREGIDO:** Error de importación de React
- ✅ 6 simuladores profesionales
- ✅ Sistema de progreso por localStorage
- ✅ Chat interactivo con IA
- ✅ Diseño Bento Grid

**Simuladores disponibles:**
1. Product Owner
2. Scrum Master
3. Tech Interviewer
4. Incident Responder
5. Cliente
6. DevSecOps

## ✅ Correcciones Aplicadas

### 1. Error en SimulatorsPage.tsx

**Problema:** Página en blanco por error de React
```
'React' refers to a UMD global, but the current file is a module.
```

**Solución:**
```tsx
// Antes
import { useState, useEffect } from 'react';

// Después
import React, { useState, useEffect } from 'react';
```

**Línea afectada:** 297
```tsx
// Ahora funciona correctamente
{React.createElement(selectedSimulator.icon, { 
  className: "w-5 h-5 text-slate-600 dark:text-slate-400" 
})}
```

### 2. Nuevo Sistema de Layout

**Actualizado:** App.tsx para usar `LayoutMinimal`
```tsx
// Antes
import { Layout } from './components/Layout';

// Después
import { LayoutMinimal } from './components/LayoutMinimal';
```

### 3. Sistema de Estilos Organizado

**Nuevo archivo:** `styles/design-system.css`
- Variables de diseño centralizadas
- Paleta monocromática profesional
- Transiciones suaves

**Nuevo archivo:** `styles/layout.css`
- Sistema de navegación
- Grid responsive
- Mobile-first design

**Nuevo archivo:** `styles/components.css`
- Componentes reutilizables
- Estados de hover/focus
- Modo oscuro integrado

## 🚀 Cómo Usar

### 1. Importar el Layout

```tsx
import { LayoutMinimal } from './components/LayoutMinimal';
```

### 2. Usar Componentes

```tsx
import './styles/components.css';

function MyPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Mi Página</h1>
      <button className="btn btn-primary">Acción</button>
      <div className="card card-hover">
        <div className="card-body">Contenido</div>
      </div>
    </div>
  );
}
```

### 3. Tema Oscuro

El tema se maneja automáticamente con el contexto `ThemeContext`. El botón de toggle está en el sidebar.

## 📱 Responsive

- **Desktop (>1024px):** Sidebar fijo, contenido amplio
- **Tablet (640-1024px):** Sidebar colapsable, grid adaptativo
- **Mobile (<640px):** Menú overlay, columna única

## 🎯 Principios de Diseño

1. **Minimalismo:** Solo lo esencial, sin elementos innecesarios
2. **Legibilidad:** Tipografía clara y espaciado generoso
3. **Consistencia:** Componentes reutilizables con mismo estilo
4. **Performance:** CSS ligero, transiciones suaves
5. **Accesibilidad:** Contraste adecuado, estados focus visibles

## 🐛 Problemas Resueltos

- ✅ Página en blanco de simuladores (faltaba import de React)
- ✅ Layout desorganizado (nuevo LayoutMinimal)
- ✅ Estilos inconsistentes (sistema de diseño unificado)
- ✅ Error de tipos en user.role (actualizado a user.roles[0])

---

**Autor:** Sistema de diseño minimalista profesional  
**Última actualización:** Diciembre 2025
