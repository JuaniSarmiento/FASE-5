"""
Script para generar claves secretas seguras para la aplicación

CRÍTICO #2 - Auditoría 2025-11-21

Este script genera claves criptográficamente seguras para:
- SECRET_KEY (general application secret)
- JWT_SECRET_KEY (JWT token signing)

Las claves generadas tienen 43 caracteres (32 bytes en base64url),
lo cual proporciona 256 bits de entropía - suficiente para uso en producción.

Uso:
    python scripts/generate_secrets.py [--output FILE]

Opciones:
    --output FILE    Guardar directamente en archivo (default: imprime en pantalla)
    --append         Agregar al final del archivo en lugar de sobrescribir
    --check FILE     Verificar si un archivo .env tiene claves válidas

Ejemplos:
    # Generar e imprimir en pantalla
    python scripts/generate_secrets.py

    # Guardar en .env (sobrescribe)
    python scripts/generate_secrets.py --output .env

    # Agregar al .env existente
    python scripts/generate_secrets.py --output .env --append

    # Verificar .env actual
    python scripts/generate_secrets.py --check .env

Autor: Alberto Cortez (Auditoría Arquitectónica)
Fecha: 2025-11-21
"""

import sys
import secrets
import argparse
import os
from pathlib import Path


def generate_secret_key() -> str:
    """
    Genera una clave secreta criptográficamente segura.

    Uses secrets.token_urlsafe(32) que genera 32 bytes aleatorios
    y los codifica en base64url (43 caracteres).

    Returns:
        String de 43 caracteres con 256 bits de entropía
    """
    return secrets.token_urlsafe(32)


def generate_env_content() -> str:
    """
    Genera contenido completo para archivo .env con claves seguras.

    Returns:
        String con variables de entorno formateadas
    """
    secret_key = generate_secret_key()
    jwt_secret_key = generate_secret_key()

    return f"""# ============================================================================
# SECURITY KEYS (REQUIRED)
# ============================================================================
# Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# CRITICAL: Keep these secrets safe. Do NOT commit to version control.
# CRITICAL: Generate NEW keys for each environment (dev, staging, production).

# General application secret key
SECRET_KEY={secret_key}

# JWT token signing key
JWT_SECRET_KEY={jwt_secret_key}

# ============================================================================
# IMPORTANT NOTES
# ============================================================================
# 1. Each key has 256 bits of entropy (cryptographically secure)
# 2. These keys are unique and should NEVER be reused
# 3. Regenerate keys if:
#    - You suspect they were compromised
#    - Moving to production
#    - Rotating keys for security policy compliance
# 4. Changing these keys will invalidate all existing JWT tokens
"""


def check_env_file(file_path: str) -> None:
    """
    Verifica si un archivo .env tiene claves válidas.

    Args:
        file_path: Ruta al archivo .env

    Prints:
        Reporte de validación
    """
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        sys.exit(1)

    print(f"\n🔍 Verificando {file_path}...\n")

    with open(file_path, 'r') as f:
        content = f.read()

    issues = []
    warnings = []

    # Verificar SECRET_KEY
    if 'SECRET_KEY=' not in content:
        issues.append("❌ SECRET_KEY no encontrado")
    elif 'SECRET_KEY=CHANGE_THIS' in content or 'SECRET_KEY=dev-secret' in content:
        issues.append("❌ SECRET_KEY tiene valor inseguro por defecto")
    else:
        # Extraer valor
        for line in content.split('\n'):
            if line.startswith('SECRET_KEY='):
                value = line.split('=', 1)[1].strip()
                if len(value) < 32:
                    issues.append(f"❌ SECRET_KEY demasiado corto ({len(value)} chars, mínimo 32)")
                else:
                    print(f"✅ SECRET_KEY válido ({len(value)} caracteres)")

    # Verificar JWT_SECRET_KEY
    if 'JWT_SECRET_KEY=' not in content:
        issues.append("❌ JWT_SECRET_KEY no encontrado")
    elif 'JWT_SECRET_KEY=CHANGE_THIS' in content or 'JWT_SECRET_KEY=development_' in content:
        issues.append("❌ JWT_SECRET_KEY tiene valor inseguro por defecto")
    else:
        for line in content.split('\n'):
            if line.startswith('JWT_SECRET_KEY='):
                value = line.split('=', 1)[1].strip()
                if len(value) < 32:
                    issues.append(f"❌ JWT_SECRET_KEY demasiado corto ({len(value)} chars, mínimo 32)")
                else:
                    print(f"✅ JWT_SECRET_KEY válido ({len(value)} caracteres)")

    # Verificar si las claves son iguales (mala práctica)
    secret_key = None
    jwt_secret_key = None
    for line in content.split('\n'):
        if line.startswith('SECRET_KEY='):
            secret_key = line.split('=', 1)[1].strip()
        if line.startswith('JWT_SECRET_KEY='):
            jwt_secret_key = line.split('=', 1)[1].strip()

    if secret_key and jwt_secret_key and secret_key == jwt_secret_key:
        warnings.append("⚠️  SECRET_KEY y JWT_SECRET_KEY son idénticos (deberían ser diferentes)")

    # Mostrar resultados
    print()
    if issues:
        print("🔴 PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  {issue}")
        print()
        print("💡 Regenerar claves con:")
        print(f"  python scripts/generate_secrets.py --output {file_path}")
        sys.exit(1)

    if warnings:
        print("⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"  {warning}")
        print()

    if not issues and not warnings:
        print("✅ Todas las validaciones pasaron correctamente")
        print()


def main():
    # Fix Windows encoding issue
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(
        description="Generar claves secretas seguras para la aplicación",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--output',
        '-o',
        metavar='FILE',
        help='Guardar en archivo (default: imprime en pantalla)'
    )
    parser.add_argument(
        '--append',
        '-a',
        action='store_true',
        help='Agregar al final del archivo en lugar de sobrescribir'
    )
    parser.add_argument(
        '--check',
        '-c',
        metavar='FILE',
        help='Verificar si un archivo .env tiene claves válidas'
    )

    args = parser.parse_args()

    # Modo verificación
    if args.check:
        check_env_file(args.check)
        return

    # Generar contenido
    content = generate_env_content()

    # Guardar o imprimir
    if args.output:
        mode = 'a' if args.append else 'w'
        action = "Agregando" if args.append else "Guardando"

        # Advertencia si va a sobrescribir
        if not args.append and os.path.exists(args.output):
            response = input(f"⚠️  {args.output} ya existe. ¿Sobrescribir? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Operación cancelada")
                sys.exit(0)

        with open(args.output, mode, encoding='utf-8') as f:
            if args.append:
                f.write('\n')  # Nueva línea antes de agregar
            f.write(content)

        print(f"✅ {action} claves en: {args.output}")
        print()
        print("🔒 IMPORTANTE:")
        print(f"  - NO comitear {args.output} a Git")
        print(f"  - Agregar {args.output} a .gitignore")
        print("  - Generar claves DIFERENTES para cada entorno")
        print()
        print("📋 Siguiente paso:")
        print(f"  python scripts/generate_secrets.py --check {args.output}")

    else:
        # Imprimir en pantalla
        print()
        print("=" * 70)
        print("CLAVES SEGURAS GENERADAS")
        print("=" * 70)
        print()
        print(content)
        print("=" * 70)
        print()
        print("💾 Para guardar en .env:")
        print("  python scripts/generate_secrets.py --output .env")
        print()
        print("🔄 Para agregar a .env existente:")
        print("  python scripts/generate_secrets.py --output .env --append")
        print()


if __name__ == "__main__":
    main()
