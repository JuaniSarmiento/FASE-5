# 🚀 INICIO RÁPIDO - ENTRENADOR DIGITAL

## ⚡ Instrucciones de 1 Minuto

### 1. Iniciar Backend
```powershell
# Desde la raíz del proyecto
cd activia1-main
uvicorn backend.api.main:app --reload
```

**Esperado**: Backend corriendo en `http://localhost:8000`

### 2. Iniciar Frontend
```powershell
# En otra terminal
cd activia1-main/frontEnd
npm run dev
```

**Esperado**: Frontend corriendo en `http://localhost:5173`

### 3. Probar Entrenador Digital

1. Abrir navegador: `http://localhost:5173`
2. Login (o registro si no tienes cuenta)
3. Click en **"Entrenador Digital"** en el menú lateral
4. Verás **"Programación 1"** con 5 temas
5. Selecciona un tema (ej: **"Condicionales"**)
6. Click **"Iniciar Entrenamiento"**
7. ¡Comienza el examen! 🎯

---

## 🎯 Lo Que Verás

### Página de Selección
- Tarjetas con 5 temas diferentes
- Indicadores de dificultad (Verde/Amarillo/Rojo)
- Tiempo estimado por tema
- Botón grande para iniciar

### Página de Examen
- **Header sticky**: Temporizador + Pistas + Botón Enviar
- **Izquierda**: Consigna, contexto, requisitos
- **Derecha**: Editor Monaco con código precargado
- **Modal de pistas**: 4 pistas disponibles con penalización

### Resultados
- Nota final (0-100)
- Tests pasados/totales
- Feedback detallado de IA
- Fortalezas y mejoras

---

## 🧪 Test Rápido del Backend

```powershell
python test_entrenador_digital_completo.py
```

Esto verificará:
- ✅ Endpoints funcionando
- ✅ Materias cargándose desde JSON
- ✅ Sesiones creándose correctamente
- ✅ Sistema de pistas operativo

---

## 📝 Temas Disponibles

1. **Condicionales** (60 min) - Fácil
2. **Secuenciales** (45 min) - Muy Fácil
3. **Bucles** (75 min) - Media
4. **Funciones** (60 min) - Media
5. **Listas/Arrays** (60 min) - Media

---

## 🎮 Cómo Usar

### Durante el Examen
- **Escribe código** en el editor Monaco
- **Solicita pistas** si necesitas ayuda (máximo 4)
- **Revisa el tiempo** en el header (cambia de color)
- **Envía cuando estés listo** o espera que termine el tiempo

### Sistema de Pistas
- Pista 1: -5 puntos
- Pista 2: -10 puntos
- Pista 3: -15 puntos
- Pista 4: -20 puntos

### Evaluación
- **70%**: Tests automáticos
- **30%**: Calidad de código (evaluada por IA)
- **Penalización**: Se resta la suma de pistas usadas

---

## 🐛 Solución de Problemas

### Backend no inicia
```powershell
# Verificar dependencias
pip install -r requirements.txt

# Verificar puerto libre
netstat -ano | findstr :8000
```

### Frontend no inicia
```powershell
# Instalar dependencias
npm install

# Limpiar cache
npm run clean
```

### Error 404 en /training
- Verificar que `training.py` esté en `backend/api/routers/`
- Verificar que esté importado en `main.py`
- Reiniciar backend

### No aparecen temas
- Verificar que existe `backend/data/training/programacion1_temas.json`
- Verificar sintaxis JSON válida
- Revisar logs del backend

---

## 📚 Documentación Completa

Ver: [ENTRENADOR_DIGITAL_MODO_EXAMEN.md](./ENTRENADOR_DIGITAL_MODO_EXAMEN.md)

---

## ✅ Checklist de Funcionalidades

- [x] Selección de materia y tema
- [x] Inicio de sesión de entrenamiento
- [x] Editor Monaco precargado
- [x] Temporizador con cuenta regresiva
- [x] Sistema de 4 pistas con penalización
- [x] Evaluación automática con tests
- [x] Análisis de calidad con IA
- [x] Resultados con feedback detallado
- [x] Fortalezas y mejoras sugeridas
- [x] Botón volver a temas

---

## 🎉 Todo Listo!

El sistema está **100% funcional** y listo para usar.

**Disfruta del Entrenador Digital!** 🚀
