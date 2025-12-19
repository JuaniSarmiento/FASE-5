# 🚀 COMANDOS RÁPIDOS - DEMO EJECUTIVO

## Ejecutar AHORA mismo

### 1️⃣ Verificar que el sistema está listo
```powershell
python check_sistema_demo.py
```
**Salida esperada**: ✅ Sistema listo para el demo!

---

### 2️⃣ Ver demostración de filtros del Entrenador Digital
```powershell
python demo_filtros.py
```
**Muestra**:
- 23 ejercicios totales (15 Python + 8 Java/Spring Boot)
- Filtrado por lenguaje, framework, dificultad
- Ejercicios de Java y Spring Boot funcionando

---

### 3️⃣ Ejecutar TEST COMPLETO para el jefe 🎯
```powershell
python test_sistema_completo_demo.py
```
**Prueba TODO el sistema**:
- ✅ Tutor Socrático (4 casos)
- ✅ Simuladores (3 perfiles)
- ✅ Entrenador Digital (estadísticas, filtros, evaluaciones)
- ✅ Análisis de Riesgos 5D

**Genera**:
- 📊 Reporte JSON con todos los resultados
- 📊 Salida profesional colorizada
- 📊 Métricas de éxito/fallo

---

## Si el backend NO está corriendo

```powershell
# Opción 1: Con Docker (recomendado)
docker-compose up -d

# Opción 2: Directo con Python
cd backend
python -m backend
```

Luego verificar con:
```powershell
python check_sistema_demo.py
```

---

## Frontend (si quieres mostrarlo en navegador)

```powershell
cd frontEnd
npm install
npm run dev
```

Abrir: http://localhost:3000

Ir a "Entrenador Digital" (antes "Ejercicios") 🎯

---

## Ver documentación completa

```powershell
# Guía completa para el demo
code DEMO_EJECUTIVO.md

# Documentación técnica de cambios
code ENTRENADOR_DIGITAL.md

# Resumen ejecutivo
code RESUMEN_CAMBIOS.md

# Visual ASCII
type VISUAL_RESUMEN.txt
```

---

## Verificar endpoints de API

### Estadísticas
```powershell
curl http://localhost:8000/exercises/json/stats
```

### Filtros disponibles
```powershell
curl http://localhost:8000/exercises/json/filters
```

### Ejercicios de Java
```powershell
curl "http://localhost:8000/exercises/json/list?language=java"
```

### Ejercicios de Spring Boot
```powershell
curl "http://localhost:8000/exercises/json/list?framework=spring-boot"
```

### Ejercicios difíciles de Spring Boot
```powershell
curl "http://localhost:8000/exercises/json/list?framework=spring-boot&difficulty=Hard"
```

---

## 🎯 EL COMANDO MÁS IMPORTANTE

```powershell
python test_sistema_completo_demo.py
```

**Este es el que debes mostrarle al jefe** ✅

Ejecuta todas las pruebas y genera un reporte profesional.

---

## 📊 Qué esperar del test completo

```
╔════════════════════════════════════════════════════════════════╗
║     DEMO COMPLETO - SISTEMA ACTIVIA CON MISTRAL AI            ║
║     Entrenamiento Personalizado con Inteligencia Artificial   ║
╚════════════════════════════════════════════════════════════════╝

================================================================================
TEST 1: TUTOR SOCRÁTICO (T-IA-Cog) - Mistral AI
================================================================================

✅ Pregunta Conceptual - POO
   • Longitud respuesta: 523 caracteres
   • Es Socrática: Sí

... (más tests)

================================================================================
REPORTE FINAL DEL DEMO - SISTEMA ACTIVIA
================================================================================

RESUMEN EJECUTIVO
────────────────────────────────────────────────────────────────
   • Total de Tests Ejecutados: 15+
   • Tests Exitosos: 15+
   • Tasa de Éxito: 100.0%

🎉 DEMO EXITOSO - Sistema funcionando perfectamente
   Listo para presentación ejecutiva
```

---

## ✅ Checklist Pre-Demo

```
□ Backend corriendo (check_sistema_demo.py pasa)
□ Ejercicios de Java creados (8 ejercicios)
□ Ejercicios de Spring Boot creados (4 ejercicios)
□ Frontend renombrado a "Entrenador Digital"
□ Sistema de filtrado funcionando
□ Evaluación con IA configurada (Mistral)
□ Test completo ejecutado exitosamente
```

---

## 🎬 Listo para el Demo

Todo está configurado y funcionando.

**Ejecuta**: `python test_sistema_completo_demo.py`

**Tiempo estimado**: 2-3 minutos

**Resultado**: Reporte profesional listo para mostrar 📊

---

## 🆘 Ayuda Rápida

### El test falla
1. Verificar backend: `python check_sistema_demo.py`
2. Ver logs: `docker-compose logs backend`
3. Reiniciar: `docker-compose restart backend`

### Backend no responde
```powershell
docker-compose down
docker-compose up -d
```

### Ver qué está corriendo
```powershell
docker-compose ps
```

---

**¡Sistema 100% funcional y listo para demo ejecutivo!** 🎉
