"""
Prueba de interacción con el tutor usando Gemini 2.5
"""
import requests

# Crear sesión
print("🔄 Creando sesión de tutor...")
create_response = requests.post("http://localhost:8000/api/v1/sessions/create-tutor", json={})
session_data = create_response.json()
print(f"✅ Sesión creada: {session_data['data']['session_id']}")
print(f"Welcome message: {session_data['data']['welcome_message'][:100]}...\n")

session_id = session_data['data']['session_id']

# Interactuar
print("🔄 Enviando mensaje al tutor...")
interact_response = requests.post(
    f"http://localhost:8000/api/v1/sessions/{session_id}/interact",
    json={
        "message": "Explícame el patrón Observer en programación",
        "student_profile": {}
    }
)

if interact_response.status_code == 200:
    interaction_data = interact_response.json()
    print(f"✅ Respuesta del tutor:")
    print(f"\n{interaction_data['data']['response']}\n")
    print(f"Metadata: {interaction_data['data']['metadata']}")
else:
    print(f"❌ Error {interact_response.status_code}")
    print(interact_response.text)
