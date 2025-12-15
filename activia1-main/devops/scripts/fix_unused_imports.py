#!/usr/bin/env python3
"""
Script para detectar y reportar imports no utilizados en el proyecto.

Uso: python scripts/fix_unused_imports.py
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

def find_python_files(root_dir: str) -> List[Path]:
    """Encuentra todos los archivos .py en el directorio."""
    root = Path(root_dir)
    return list(root.rglob("*.py"))

def analyze_file(file_path: Path) -> Dict[str, List[str]]:
    """Analiza un archivo Python y detecta imports potencialmente no utilizados."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e)}

    # Extraer imports
    import_pattern = r'^(?:from\s+[\w.]+\s+)?import\s+([\w\s,]+)(?:\s+as\s+\w+)?'
    imports = []

    for match in re.finditer(import_pattern, content, re.MULTILINE):
        import_line = match.group(0)
        imported_names = match.group(1)

        # Separar imports múltiples (e.g., "a, b, c")
        names = [n.strip() for n in imported_names.split(',')]

        for name in names:
            # Verificar si el nombre se usa en el código (fuera del import)
            # Buscar referencias al nombre importado
            usage_pattern = rf'\b{re.escape(name)}\b'

            # Contar ocurrencias (excluyendo la línea de import)
            lines = content.split('\n')
            import_line_num = content[:match.start()].count('\n')

            usage_count = 0
            for i, line in enumerate(lines):
                if i == import_line_num:
                    continue  # Skip import line
                if re.search(usage_pattern, line):
                    usage_count += 1

            if usage_count == 0:
                imports.append({
                    'name': name,
                    'line': import_line,
                    'line_num': import_line_num + 1
                })

    return {'unused': imports}

def main():
    """Ejecuta el análisis."""
    print("Analizando archivos Python...")
    print("=" * 80)

    # Directorios a analizar
    src_dir = Path(__file__).parent.parent / "src" / "ai_native_mvp"

    if not src_dir.exists():
        print(f"Error: Directorio no encontrado: {src_dir}")
        return

    files = find_python_files(str(src_dir))
    print(f"Archivos encontrados: {len(files)}")
    print()

    total_unused = 0
    files_with_unused = []

    for file_path in files:
        rel_path = file_path.relative_to(src_dir.parent.parent)
        result = analyze_file(file_path)

        if 'error' in result:
            print(f"⚠️  Error en {rel_path}: {result['error']}")
            continue

        if result['unused']:
            files_with_unused.append((str(rel_path), result['unused']))
            total_unused += len(result['unused'])

    # Reporte
    if files_with_unused:
        print(f"\n{'=' * 80}")
        print(f"ARCHIVOS CON IMPORTS POTENCIALMENTE NO UTILIZADOS: {len(files_with_unused)}")
        print(f"{'=' * 80}\n")

        for file_path, unused in files_with_unused:
            print(f"\n📄 {file_path}")
            print("-" * 80)
            for item in unused:
                print(f"  Línea {item['line_num']}: {item['name']}")
                print(f"    {item['line']}")
    else:
        print("\n✅ No se encontraron imports no utilizados!")

    print(f"\n{'=' * 80}")
    print(f"TOTAL: {total_unused} imports potencialmente no utilizados")
    print(f"{'=' * 80}")

    print("\n⚠️  NOTA: Este es un análisis básico. Verifica manualmente antes de eliminar.")
    print("   Algunos imports pueden ser usados dinámicamente o en comentarios.")

if __name__ == "__main__":
    main()
