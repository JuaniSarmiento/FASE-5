"""
Script simple para verificar que el sistema está listo
Prueba la configuración completa sin arrancar el servidor
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_environment():
    """Verifica las variables de entorno necesarias"""
    print("="*60)
    print("VERIFICACIÓN DE ENTORNO")
    print("="*60)
    
    checks = [
        ("LLM_PROVIDER", "gemini"),
        ("GEMINI_API_KEY", None),
        ("GEMINI_MODEL", "gemini-2.5-flash"),
        ("DATABASE_URL", None),
        ("REDIS_URL", None),
    ]
    
    all_ok = True
    for var, expected in checks:
        value = os.getenv(var)
        
        if value:
            if expected and value != expected:
                print(f"⚠️  {var}: {value} (esperado: {expected})")
            else:
                # Ocultar valores sensibles
                if "KEY" in var or "PASSWORD" in var or "SECRET" in var:
                    display = f"{value[:20]}..." if len(value) > 20 else value
                else:
                    display = value
                print(f"✅ {var}: {display}")
        else:
            print(f"❌ {var}: NO CONFIGURADO")
            all_ok = False
    
    return all_ok

def check_imports():
    """Verifica que los módulos se puedan importar"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE IMPORTS")
    print("="*60)
    
    imports_to_check = [
        ("backend.llm.factory", "LLMProviderFactory"),
        ("backend.llm.base", "LLMMessage, LLMRole"),
        ("backend.llm.gemini_provider", "GeminiProvider"),
    ]
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    all_ok = True
    for module, items in imports_to_check:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {str(e)}")
            all_ok = False
    
    return all_ok

def check_provider():
    """Verifica que el provider se pueda crear"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE PROVIDER")
    print("="*60)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from llm.factory import LLMProviderFactory
        
        provider = LLMProviderFactory.create_from_env()
        
        print(f"✅ Provider creado: {type(provider).__name__}")
        print(f"✅ Modelo: {provider.model}")
        print(f"✅ API Key: {'Configurada' if provider.api_key else 'NO CONFIGURADA'}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando provider: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todas las verificaciones"""
    print("\n🔍 VERIFICACIÓN DEL SISTEMA\n")
    
    results = []
    
    results.append(("Entorno", check_environment()))
    results.append(("Imports", check_imports()))
    results.append(("Provider", check_provider()))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"{status} {name}")
    
    all_ok = all(r[1] for r in results)
    
    if all_ok:
        print("\n🎉 ¡SISTEMA LISTO PARA USAR!")
        print("\nPuedes arrancar el backend con:")
        print("  python -m backend.api.main")
        print("\nO ejecutar pruebas con:")
        print("  python test_gemini_integration_complete.py")
    else:
        print("\n⚠️ HAY PROBLEMAS QUE CORREGIR")
        print("Revisa los errores arriba")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
