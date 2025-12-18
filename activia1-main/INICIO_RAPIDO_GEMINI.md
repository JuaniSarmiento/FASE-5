# 🚀 Inicio Rápido: Gemini API

## Configuración en 3 Pasos

### 1️⃣ Obtener API Key (2 minutos)

1. Visita: **https://makersuite.google.com/app/apikey**
2. Inicia sesión con tu cuenta de Google
3. Click en **"Create API Key"**
4. Copia la clave generada

### 2️⃣ Configurar .env (1 minuto)

Edita tu archivo `.env` (o créalo desde `.env.example`):

```bash
# Cambiar estas dos líneas:
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...tu_api_key_aqui...
```

### 3️⃣ Reiniciar Backend (30 segundos)

**Con Docker:**
```bash
docker-compose restart backend
```

**Sin Docker:**
```bash
# Detener con Ctrl+C
python -m backend
```

---

## ✅ Verificar que Funciona

```bash
python test_gemini_integration.py
```

**Deberías ver:**
```
✅ Provider creado exitosamente
✅ Modelo Flash usado correctamente  
✅ Modelo Pro usado correctamente
✅ ÉXITO: El tutor redirigió con preguntas
✅ Streaming completado
```

---

## 🎯 Lo que Cambió

| Antes (Ollama) | Ahora (Gemini) |
|----------------|----------------|
| ⏱️ 5-10 segundos por respuesta | ⚡ 1-2 segundos |
| 🏠 Local (requiere GPU) | ☁️ Cloud (sin GPU) |
| 💰 Gratis | 💵 ~$5-15/mes |
| 📊 Calidad variable | 🎯 Alta calidad |
| 🔒 100% privado | 🔐 Encriptado en tránsito |

---

## 🤖 Tutor Mejorado

**Ahora el tutor NO da código:**

```
Estudiante: "Dame el código para sumar dos números"

Tutor Anterior: 
"def suma(a, b): return a + b"

Tutor Nuevo: 
"🤔 En vez de darte el código, ayúdame a entender:
1. ¿Qué entradas necesita tu función?
2. ¿Qué operación querés realizar?
3. ¿Qué resultado esperás?"
```

---

## 📊 Modelos Automáticos

### Gemini Flash (Rápido) 
**Para:** Conversaciones, preguntas, explicaciones
```
"¿Qué es un bucle?"
"Explícame qué son las funciones"
```

### Gemini Pro (Profundo)
**Para:** Análisis de código, algoritmos, debugging
```
"Analiza la complejidad de este algoritmo"
"¿Cómo optimizar este código?"
```

**El sistema elige automáticamente** según las palabras clave.

---

## 🆘 Problemas Comunes

### "GEMINI_API_KEY is required"
**Solución:** Verifica que agregaste la clave en `.env`

### Respuestas lentas (>10 segundos)
**Solución:** Verifica tu conexión a internet

### Error 429 (Rate Limit)
**Solución:** Espera 1 minuto, la API tiene límites

### El tutor da código
**Solución:** Asegúrate de reiniciar el backend después de actualizar

---

## 📚 Más Información

- **Guía completa:** [MIGRACION_GEMINI.md](MIGRACION_GEMINI.md)
- **Documentación técnica:** [backend/llm/README.md](backend/llm/README.md)
- **Resumen de cambios:** [RESUMEN_CAMBIOS_GEMINI.md](RESUMEN_CAMBIOS_GEMINI.md)

---

## 💡 Tips

1. **Ahorra costos:** El sistema usa Flash automáticamente cuando puede
2. **Testing:** Usa `LLM_PROVIDER=mock` para tests sin consumir API
3. **Rollback:** Puedes volver a Ollama cambiando `LLM_PROVIDER=ollama`

---

**¿Todo listo?** 🎉

```bash
# Probar ahora:
python test_gemini_integration.py

# Si todo pasa, ¡estás usando Gemini! 🚀
```
