"""
Punto de entrada principal para ejecutar el CLI del ecosistema AI-Native

Permite ejecutar:
    python -m ai_native_mvp

En lugar de:
    python -m src.ai_native_mvp.cli
"""
from .cli import main

if __name__ == "__main__":
    main()