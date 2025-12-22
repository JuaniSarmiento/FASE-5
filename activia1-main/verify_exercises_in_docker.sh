#!/bin/bash
# Script para verificar que los ejercicios están en el contenedor Docker

echo "🔍 Verificando ejercicios en contenedor Docker..."

# Build imagen temporalmente
docker build -f Dockerfile.backend -t test-backend-exercises . > /dev/null 2>&1

# Verificar si los archivos existen
echo ""
echo "📁 Archivos de ejercicios en el contenedor:"
docker run --rm test-backend-exercises ls -lh backend/data/exercises/*.json 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Los ejercicios están correctamente incluidos en el contenedor"

    # Contar ejercicios
    COUNT=$(docker run --rm test-backend-exercises ls backend/data/exercises/*.json 2>/dev/null | wc -l)
    echo "📊 Total de archivos JSON: $COUNT"
else
    echo ""
    echo "❌ ERROR: Los ejercicios NO están en el contenedor"
    exit 1
fi

# Limpiar imagen de prueba
docker rmi test-backend-exercises > /dev/null 2>&1

echo ""
echo "🎉 Verificación completada"
