# 🚀 Guía Rápida de Deploy - Mejoras AI-Native

## ⚡ Inicio Rápido (Todo en Uno)

```powershell
# Ejecuta el script de deploy automático
.\deploy_mejoras.ps1
```

Este script hace todo automáticamente:
1. ✓ Verifica Docker
2. ✓ Reconstruye contenedores con nuevas configs
3. ✓ Descarga modelo llama3.2:3b
4. ✓ Instala dependencias del frontend

---

## 📋 Paso a Paso Manual (Si prefieres control total)

### Backend

```powershell
# 1. Reconstruir stack
docker-compose down
docker-compose up -d --build

# 2. Descargar modelo nuevo (primera vez)
docker exec -it ai-native-ollama ollama pull llama3.2:3b

# 3. Verificar que está activo
docker exec -it ai-native-ollama ollama list
# Debe aparecer: llama3.2:3b

# 4. Ver logs
docker-compose logs -f api
docker-compose logs -f ollama
```

### Frontend

```powershell
# 1. Instalar dependencias (primera vez)
cd frontEnd
npm install

# 2. Iniciar dev server
npm run dev

# 3. Abrir navegador
# http://localhost:5173
```

---

## ✅ Verificación

### 1. Backend funcionando
```powershell
curl http://localhost:8000/api/v1/health
```

Debe retornar:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Ollama funcionando
```powershell
docker exec -it ai-native-ollama ollama list
```

Debe mostrar:
```
NAME              ID              SIZE      MODIFIED
llama3.2:3b      abc123def456    2.0 GB    X minutes ago
```

### 3. Frontend funcionando
Abre http://localhost:5173 - Debe aparecer la aplicación

---

## 🎯 Qué Cambió

### Backend
- ✅ Modelo: `llama3.2:3b` (2.3x más rápido)
- ✅ Keep-Alive: Permanente (sin latencia inicial)
- ✅ Reintentos: 3 intentos automáticos con backoff
- ✅ Fallback: Respuestas educativas si LLM falla

### Frontend
- ✅ Monaco Editor (VS Code)
- ✅ Layout resizable de 3 paneles
- ✅ AI Companion (Tutor/Juez/Simulador)
- ✅ Dashboard Docente con métricas
- ✅ Skeleton loading (percepción de velocidad)
- ✅ Sistema de toasts (feedback no-intrusivo)

---

## 🐛 Troubleshooting

### "Docker no está corriendo"
```powershell
# Inicia Docker Desktop desde el menú de Windows
# Espera a que el ícono de Docker sea verde
# Vuelve a ejecutar el script
```

### "Ollama no responde"
```powershell
# Ver logs de Ollama
docker-compose logs ollama

# Reiniciar solo Ollama
docker-compose restart ollama

# Espera 10-15 segundos y reintenta
```

### "npm install falla"
```powershell
# Asegúrate de tener Node.js 18+
node --version

# Limpia cache
npm cache clean --force
npm install
```

### "Puerto 8000 ocupado"
```powershell
# Ver qué usa el puerto
netstat -ano | findstr :8000

# Matar proceso (reemplaza PID)
taskkill /PID <PID> /F

# O cambia el puerto en docker-compose.yml
```

---

## 📊 Testing de Performance

### Medir latencia del LLM
```powershell
# Prueba simple (debe responder <1s después del primer uso)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "session_id": "test"}'
```

### Ver métricas de reintentos
```powershell
# Busca en logs cuántos reintentos hubo
docker-compose logs api | findstr "attempt"
```

---

## 📚 Documentación Completa

Ver `MEJORAS_IMPLEMENTADAS.md` para detalles técnicos completos.

---

## 🆘 Soporte

Si algo no funciona:
1. Lee los logs: `docker-compose logs -f`
2. Verifica que todos los servicios estén "healthy": `docker-compose ps`
3. Revisa el troubleshooting arriba

---

**Última actualización**: Diciembre 2025
