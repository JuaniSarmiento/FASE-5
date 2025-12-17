# ============================================================================
# DIAGNÓSTICO Y SOLUCIÓN: Ollama usando solo 1/33 capas en GPU
# ============================================================================
# Arquitecto: AI Senior Architect
# Fecha: 2025-12-16
# Problema: Regresión de rendimiento - Ollama pasó de 29/33 a 1/33 capas en GPU
# ============================================================================

## ÍNDICE
1. [Análisis del Problema](#análisis-del-problema)
2. [Comandos de Diagnóstico](#comandos-de-diagnóstico)
3. [Causas Probables](#causas-probables)
4. [Solución Implementada](#solución-implementada)
5. [Verificación Post-Deploy](#verificación-post-deploy)
6. [Troubleshooting Avanzado](#troubleshooting-avanzado)

---

## ANÁLISIS DEL PROBLEMA

### Síntomas Observados
```
load_tensors: offloaded 1/33 layers to GPU
```

**Antes (funcionando):**
- 29/33 capas en GPU
- Latencia aceptable (~2-5 segundos)
- VRAM usage: ~4.5 GB

**Ahora (regresión):**
- 1/33 capas en GPU
- 32/33 capas en CPU (fallback)
- Latencia inutilizable (>30 segundos)

### Por qué Ollama decide usar solo 1 capa en GPU

Ollama usa una heurística automática para decidir cuántas capas offloadear:

```python
# Pseudo-código de lógica de Ollama
available_vram = get_available_vram()
model_layer_size = model_total_size / num_layers

layers_to_offload = min(
    num_layers,
    available_vram / layer_size
)
```

**Causas de que solo use 1 capa:**

1. **VRAM fragmentada o ocupada** → Solo ~200MB disponibles
2. **Otro proceso usando la GPU** → Docker Desktop, Chrome, etc.
3. **Variable OLLAMA_NUM_GPU no configurada** → Usa heurística conservadora
4. **Límites de memoria Docker insuficientes** → OOM killer mata capas
5. **Driver NVIDIA desactualizado** → Reporting incorrecto de VRAM

---

## COMANDOS DE DIAGNÓSTICO

### 1. Verificar uso de VRAM ANTES de levantar contenedores

```powershell
# Comando 1: Ver estado actual de GPU (NVIDIA-SMI)
nvidia-smi

# Output esperado:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.xx       Driver Version: 535.xx       CUDA Version: 12.2    |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
# |===============================+======================+======================|
# |   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0  On |                  N/A |
# | 45%   45C    P0    15W /  75W |   1234MiB /  6144MiB |      5%      Default |
# +-------------------------------+----------------------+----------------------+
#
# ⚠️ VERIFICAR: Memory-Usage debe ser < 1500MB antes de Docker

# Comando 2: Ver procesos usando la GPU
nvidia-smi pmon -c 1

# Output esperado:
# # gpu        pid  type    sm   mem   enc   dec   command
# # Idx          #   C/G     %     %     %     %   name
#     0       1234     G    10    15     0     0   dwm.exe        ← Windows Desktop Manager
#     0       5678     G     2     5     0     0   chrome.exe     ← ⚠️ Chrome usando VRAM
#     0       9012     G     0     3     0     0   docker-desktop ← ⚠️ Docker Desktop GUI
#
# ACCIÓN: Cerrar Chrome y Docker Desktop GUI si usan >500MB

# Comando 3: Ver procesos usando GPU con detalles de memoria
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

# Output esperado:
# pid, process_name, used_memory [MiB]
# 1234, chrome.exe, 856
# 5678, docker-desktop.exe, 234
# 
# ACCIÓN: Matar procesos innecesarios que usen >200MB
```

### 2. Limpiar VRAM antes de levantar Ollama

```powershell
# Detener todos los contenedores Docker
docker compose -f docker-compose.yml -f docker-compose.gpu.yml down

# Esperar 10 segundos para que se libere VRAM
Start-Sleep -Seconds 10

# Verificar que la VRAM se liberó
nvidia-smi

# Debe mostrar Memory-Usage < 500MB (solo Windows DWM)

# Opcional: Reiniciar Docker Desktop para limpiar completamente
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
& "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### 3. Verificar que el contenedor tiene acceso a GPU

```powershell
# Levantar stack con GPU
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build

# Verificar que el contenedor ve la GPU
docker exec ai-native-ollama nvidia-smi

# Output esperado:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.xx       Driver Version: 535.xx       CUDA Version: 12.2    |
# |-------------------------------+----------------------+----------------------+
# |   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0  On |                  N/A |
# | 45%   45C    P0    15W /  75W |    234MiB /  6144MiB |      5%      Default |
# +-------------------------------+----------------------+----------------------+
#
# ✅ Si ves esto, el contenedor tiene acceso correcto a la GPU

# ❌ Si dice "nvidia-smi: not found", el runtime GPU no está configurado

# Verificar variables de entorno dentro del contenedor
docker exec ai-native-ollama env | Select-String "NVIDIA|OLLAMA|CUDA"

# Output esperado:
# NVIDIA_VISIBLE_DEVICES=all
# NVIDIA_DRIVER_CAPABILITIES=compute,utility
# OLLAMA_NUM_GPU=99
# OLLAMA_GPU_MEMORY_FRACTION=0.85
# CUDA_VISIBLE_DEVICES=0
# OLLAMA_DEBUG=1
```

### 4. Monitorear offloading de capas en tiempo real

```powershell
# Ver logs de Ollama mientras carga el modelo
docker logs -f ai-native-ollama

# Output esperado (CORRECTO - 33/33 capas):
# time=2025-12-16T10:30:15.123Z level=INFO source=gpu.go:123 msg="looking for GPU"
# time=2025-12-16T10:30:15.234Z level=INFO source=gpu.go:145 msg="found 1 NVIDIA GPU"
# time=2025-12-16T10:30:15.345Z level=INFO source=gpu.go:178 msg="VRAM available: 5.8 GiB"
# time=2025-12-16T10:30:16.123Z level=INFO source=llm.go:234 msg="loading model" model=mistral:7b-instruct
# time=2025-12-16T10:30:18.456Z level=INFO source=llm.go:456 msg="load_tensors: offloaded 33/33 layers to GPU"
# time=2025-12-16T10:30:18.567Z level=INFO source=llm.go:478 msg="model loaded successfully"
#
# ✅ 33/33 layers → TODO EN GPU (CORRECTO)

# Output problemático (INCORRECTO - 1/33 capas):
# time=2025-12-16T10:30:18.456Z level=WARN source=llm.go:456 msg="insufficient VRAM, using CPU fallback"
# time=2025-12-16T10:30:18.567Z level=INFO source=llm.go:478 msg="load_tensors: offloaded 1/33 layers to GPU"
# time=2025-12-16T10:30:18.678Z level=WARN source=llm.go:490 msg="performance will be degraded"
#
# ❌ 1/33 layers → PROBLEMA DE VRAM

# Hacer una request de prueba y ver el offloading
docker exec ai-native-ollama ollama run mistral:7b-instruct "Test" --verbose

# Debe mostrar:
# total duration:       2.3s
# load duration:        1.2s
# prompt eval duration: 0.8s
# eval duration:        0.3s
#
# ✅ Si total < 5s → GPU funcionando correctamente
# ❌ Si total > 15s → CPU fallback (problema)
```

---

## CAUSAS PROBABLES

### 1. Fragmentación de VRAM (MÁS PROBABLE)

**Diagnóstico:**
```powershell
nvidia-smi
# Memory-Usage: 2500MiB / 6144MiB (41% usado)
```

**Causa:** Aunque hay 3.6GB "disponibles", pueden estar fragmentados.

**Solución:**
1. Reiniciar PC (limpia completamente la VRAM)
2. Cerrar Chrome, VS Code, Docker Desktop GUI
3. Levantar solo el contenedor de Ollama primero

```powershell
# Levantar solo Ollama
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d ollama

# Esperar a que cargue el modelo
docker logs -f ai-native-ollama

# Luego levantar el resto
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

### 2. Docker Desktop usando GPU

**Diagnóstico:**
```powershell
nvidia-smi pmon
# 5678, docker-desktop.exe, 1200MB  ← ⚠️ Usando mucha VRAM
```

**Solución:**
Deshabilitar GPU para Docker Desktop GUI:
1. Docker Desktop → Settings → Resources
2. Deshabilitar "Use GPU for Docker Desktop"
3. Restart Docker Desktop

### 3. Variable OLLAMA_NUM_GPU no tomada

**Diagnóstico:**
```powershell
docker exec ai-native-ollama env | grep OLLAMA_NUM_GPU
# (vacío o no aparece)
```

**Solución:** Ya implementada en [docker-compose.gpu.yml](../docker-compose.gpu.yml)

### 4. Límites de memoria Docker insuficientes

**Diagnóstico:**
```powershell
docker stats ai-native-ollama
# CONTAINER           MEM USAGE / LIMIT
# ai-native-ollama    7.8GB / 8GB  ← ⚠️ Cerca del límite
```

**Solución:** Ya implementada (limits: 12GB, reservations: 4GB)

### 5. Driver NVIDIA desactualizado

**Diagnóstico:**
```powershell
nvidia-smi
# Driver Version: 472.xx  ← ⚠️ Muy viejo (< 525)
```

**Solución:**
Actualizar a driver >= 525.60.13
```powershell
# Descargar desde:
# https://www.nvidia.com/Download/index.aspx
```

---

## SOLUCIÓN IMPLEMENTADA

### Cambios en `docker-compose.gpu.yml`

```yaml
# ANTES (PROBLEMA)
environment:
  - OLLAMA_NUM_GPU=1  # ❌ Solo 1 capa

# DESPUÉS (SOLUCIÓN)
environment:
  - OLLAMA_NUM_GPU=99                  # Forzar máximo offloading
  - OLLAMA_GPU_MEMORY_FRACTION=0.85    # Usar 85% VRAM
  - OLLAMA_MAX_LOADED_MODELS=1         # Un solo modelo
  - OLLAMA_CONTEXT_LENGTH=4096         # Balance memoria/rendimiento
  - OLLAMA_DEBUG=1                     # Logs detallados
  - OLLAMA_LLM_LIBRARY=cuda            # Forzar CUDA backend
```

### Límites de recursos optimizados

```yaml
deploy:
  resources:
    limits:
      memory: 12G    # Suficiente para modelo + context
      cpus: '6.0'
    reservations:
      memory: 4G     # Mínimo garantizado
      cpus: '2.0'
```

---

## VERIFICACIÓN POST-DEPLOY

### 1. Rebuild y deploy

```powershell
# Limpiar todo
docker compose -f docker-compose.yml -f docker-compose.gpu.yml down -v

# Rebuild (importante: --build para aplicar cambios de env)
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build

# Ver logs en tiempo real
docker logs -f ai-native-ollama
```

### 2. Verificar offloading correcto

```powershell
# Debe mostrar: "load_tensors: offloaded 33/33 layers to GPU"
docker logs ai-native-ollama | Select-String "offloaded"

# Output esperado:
# load_tensors: offloaded 33/33 layers to GPU
```

### 3. Test de rendimiento

```powershell
# Request de prueba
Measure-Command {
    curl -X POST http://localhost:11434/api/generate `
        -H "Content-Type: application/json" `
        -d '{"model":"mistral:7b-instruct","prompt":"What is 2+2?","stream":false}'
}

# Output esperado:
# TotalSeconds: 2.3  ← ✅ GPU funcionando
#
# ❌ Si > 15 segundos → CPU fallback (problema persiste)
```

### 4. Monitoreo continuo

```powershell
# Watch GPU usage en tiempo real
while ($true) {
    Clear-Host
    nvidia-smi
    Start-Sleep -Seconds 2
}

# Durante inferencia debe mostrar:
# GPU-Util: 80-100%       ← ✅ GPU activa
# Memory-Usage: 4500MB    ← ✅ Modelo cargado en VRAM
```

---

## TROUBLESHOOTING AVANZADO

### Problema persiste después de aplicar solución

#### Opción A: Modelo corrupto en cache

```powershell
# Eliminar modelo y re-descargarlo
docker exec ai-native-ollama ollama rm mistral:7b-instruct
docker exec ai-native-ollama ollama pull mistral:7b-instruct

# Ver logs de pull
docker logs -f ai-native-ollama
```

#### Opción B: Volumen Docker corrupto

```powershell
# Eliminar volumen de Ollama (CUIDADO: borra modelos descargados)
docker compose down -v
docker volume rm activia1-main_ollama_data

# Re-deploy
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

#### Opción C: Cambiar a modelo más pequeño temporalmente

```powershell
# Probar con modelo más pequeño (2GB vs 4GB)
docker exec ai-native-ollama ollama pull phi3:3.8b

# Actualizar .env
# OLLAMA_MODEL=phi3:3.8b

# Restart
docker compose restart api
```

#### Opción D: Usar cuantización más agresiva

```powershell
# Q4_K_M (actual) → ~4GB
# Q3_K_M (más agresivo) → ~3GB

docker exec ai-native-ollama ollama pull mistral:7b-instruct-q3_K_M
```

### Logs de debugging avanzado

```powershell
# Habilitar logs CUDA
docker compose -f docker-compose.yml -f docker-compose.gpu.yml down
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up ollama

# Ver logs en vivo (sin -d)
# Debe mostrar detalles de CUDA initialization
```

### Verificar compatibilidad CUDA

```powershell
# Dentro del contenedor
docker exec ai-native-ollama bash -c "ldconfig -p | grep cuda"

# Output esperado:
# libcuda.so.1 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libcuda.so.1
```

---

## RESUMEN DE ACCIONES

### ANTES de reiniciar contenedores:

1. ✅ Cerrar Chrome, VS Code, aplicaciones pesadas
2. ✅ Verificar VRAM disponible: `nvidia-smi` (debe mostrar < 1GB usado)
3. ✅ Matar procesos GPU innecesarios: `nvidia-smi pmon`

### AL reiniciar contenedores:

1. ✅ Usar configuración optimizada: `docker-compose.gpu.yml`
2. ✅ Rebuild obligatorio: `--build` flag
3. ✅ Verificar variables de entorno: `docker exec ... env`

### DESPUÉS de reiniciar:

1. ✅ Verificar logs: `docker logs ai-native-ollama | grep offloaded`
2. ✅ Debe mostrar: **"33/33 layers to GPU"**
3. ✅ Test de latencia: debe ser < 5 segundos

---

## MÉTRICAS ESPERADAS (POST-FIX)

| Métrica | Antes (CPU) | Después (GPU) |
|---------|-------------|---------------|
| Capas en GPU | 1/33 | 33/33 |
| Latencia primera token | 25-40s | 1-2s |
| Latencia total (50 tokens) | 60-90s | 3-5s |
| VRAM usage | 200MB | 4.5GB |
| GPU utilization | 0-5% | 85-100% |
| CPU utilization | 80-100% | 10-20% |

---

**Arquitecto:** AI Senior Architect  
**Documento:** GPU Diagnostic & Optimization Guide  
**Versión:** 1.0  
**Última actualización:** 2025-12-16
