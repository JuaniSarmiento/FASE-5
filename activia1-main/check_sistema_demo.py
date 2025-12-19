"""
Script rápido para verificar que el backend esté listo antes del demo
"""

import requests
import sys
import time

BASE_URL = "http://localhost:8000"

def check_backend():
    """Verifica que el backend esté funcionando"""
    print("🔍 Verificando backend en", BASE_URL)
    
    try:
        # Intentar varios endpoints
        endpoints = [
            "/health",
            "/",
            "/docs"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                if response.status_code in [200, 307]:
                    print(f"✅ Backend respondiendo en {endpoint}")
                    return True
            except:
                continue
        
        print("❌ Backend no responde")
        print("\nPara iniciar el backend:")
        print("1. cd backend")
        print("2. python -m backend")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if check_backend():
        print("\n✅ Sistema listo para el demo!")
        sys.exit(0)
    else:
        print("\n❌ Sistema NO listo - Iniciar backend primero")
        sys.exit(1)
