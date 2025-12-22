# Script de diagnóstico rápido para el Entrenador Digital
# Verifica que todo esté configurado correctamente

import os
from pathlib import Path
import json

print("=" * 80)
print("🔍 DIAGNÓSTICO - ENTRENADOR DIGITAL")
print("=" * 80)

# Colores
class C:
    G = '\033[92m'  # Green
    R = '\033[91m'  # Red
    Y = '\033[93m'  # Yellow
    E = '\033[0m'   # End

def check(condition, message):
    symbol = f"{C.G}✅{C.E}" if condition else f"{C.R}❌{C.E}"
    print(f"{symbol} {message}")
    return condition

print("\n📁 VERIFICANDO ESTRUCTURA DE ARCHIVOS:\n")

# 1. Verificar directorio de training
training_dir = Path("backend/data/training")
exists_dir = check(training_dir.exists(), f"Directorio existe: {training_dir}")

# 2. Verificar archivo JSON
json_file = training_dir / "programacion1_temas.json"
exists_json = check(json_file.exists(), f"Archivo JSON existe: {json_file}")

# 3. Verificar contenido del JSON
if exists_json:
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        has_materia = check('materia' in data, "JSON tiene campo 'materia'")
        has_temas = check('temas' in data, "JSON tiene campo 'temas'")
        
        if has_temas:
            temas_count = len(data['temas'])
            check(temas_count > 0, f"JSON tiene {temas_count} temas")
            
            print(f"\n{C.Y}📚 TEMAS ENCONTRADOS:{C.E}")
            for i, tema in enumerate(data['temas'], 1):
                print(f"   {i}. {tema.get('nombre', 'Sin nombre')} ({tema.get('dificultad', 'N/A')})")
        
        print(f"\n{C.Y}📊 ESTRUCTURA DEL JSON:{C.E}")
        print(f"   Materia: {data.get('materia', 'N/A')}")
        print(f"   Código: {data.get('codigo', 'N/A')}")
        print(f"   Temas: {len(data.get('temas', []))}")
        
    except json.JSONDecodeError as e:
        check(False, f"Error parseando JSON: {e}")
    except Exception as e:
        check(False, f"Error leyendo JSON: {e}")

print(f"\n🔌 VERIFICANDO BACKEND:\n")

# 4. Verificar archivo training.py
training_router = Path("backend/api/routers/training.py")
exists_router = check(training_router.exists(), f"Router existe: {training_router}")

# 5. Verificar que esté importado en main.py
main_file = Path("backend/api/main.py")
if main_file.exists():
    with open(main_file, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    has_import = check(
        'from .routers.training import router as training_router' in main_content,
        "Router importado en main.py"
    )
    
    has_include = check(
        'app.include_router(training_router' in main_content,
        "Router incluido en app"
    )
else:
    check(False, "main.py no encontrado")

print(f"\n🎨 VERIFICANDO FRONTEND:\n")

# 6. Verificar servicio
service_file = Path("frontEnd/src/services/api/training.service.ts")
exists_service = check(service_file.exists(), f"Servicio existe: {service_file}")

# 7. Verificar páginas
page1 = Path("frontEnd/src/pages/TrainingPage.tsx")
exists_page1 = check(page1.exists(), f"TrainingPage existe: {page1}")

page2 = Path("frontEnd/src/pages/TrainingExamPage.tsx")
exists_page2 = check(page2.exists(), f"TrainingExamPage existe: {page2}")

# 8. Verificar rutas en App.tsx
app_file = Path("frontEnd/src/App.tsx")
if app_file.exists():
    with open(app_file, 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    has_import_training = check(
        'TrainingPage' in app_content,
        "TrainingPage importada en App.tsx"
    )
    
    has_route = check(
        'path="training"' in app_content,
        "Ruta /training configurada"
    )
else:
    check(False, "App.tsx no encontrado")

print(f"\n📋 INSTRUCCIONES:\n")

# Resumen
all_ok = all([
    exists_dir, exists_json, exists_router, 
    exists_service, exists_page1, exists_page2
])

if all_ok:
    print(f"{C.G}✅ TODO ESTÁ CONFIGURADO CORRECTAMENTE{C.E}")
    print(f"\n{C.Y}Para iniciar el sistema:{C.E}")
    print(f"1. Terminal 1 - Backend:")
    print(f"   uvicorn backend.api.main:app --reload")
    print(f"\n2. Terminal 2 - Frontend:")
    print(f"   cd frontEnd")
    print(f"   npm run dev")
    print(f"\n3. Abrir navegador:")
    print(f"   http://localhost:5173/training")
else:
    print(f"{C.R}❌ HAY PROBLEMAS DE CONFIGURACIÓN{C.E}")
    print(f"\nRevisa los elementos marcados con ❌ arriba")

print(f"\n{C.Y}🔍 DEBUGGING:{C.E}")
print(f"- Abre la consola del navegador (F12) para ver errores")
print(f"- Verifica que el backend esté corriendo en http://localhost:8000")
print(f"- Verifica que el endpoint responda: http://localhost:8000/api/v1/training/materias")

print("\n" + "=" * 80)
