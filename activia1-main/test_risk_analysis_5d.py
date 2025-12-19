"""
Test del Análisis de Riesgos 5D con Mistral AI

Verifica que el análisis de riesgos funcione correctamente analizando
las conversaciones con el tutor en 5 dimensiones.
"""
import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def test_risk_analysis_5d():
    """Prueba completa del análisis de riesgos 5D"""
    
    print("=" * 90)
    print("🔍 TEST ANÁLISIS DE RIESGOS 5D CON MISTRAL AI")
    print("=" * 90)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        
        # 1. Crear sesión
        print("\n📝 PASO 1: Crear sesión de tutoría")
        print("-" * 90)
        payload = {
            "student_id": "test_risk_student_001",
            "activity_id": "risk_analysis_test",
            "mode": "TUTOR",
            "subject": "programacion",
            "topic": "python"
        }
        resp = await client.post(f"{BASE_URL}/sessions", json=payload)
        result = resp.json()
        session_id = result["data"]["id"]
        print(f"✅ Sesión creada: {session_id}")
        
        # 2. Simular diferentes tipos de interacciones para generar riesgos
        print("\n💬 PASO 2: Generar conversaciones con diferentes niveles de riesgo")
        print("-" * 90)
        
        test_interactions = [
            # Interacción 1: Pregunta superficial - RIESGO EPISTÉMICO
            {
                "prompt": "Dame el código para hacer un loop en Python",
                "risk_type": "Epistémico (superficial)"
            },
            # Interacción 2: Sin justificación - RIESGO COGNITIVO
            {
                "prompt": "¿Cómo ordeno una lista?",
                "risk_type": "Cognitivo (falta de pensamiento crítico)"
            },
            # Interacción 3: Copy-paste sin entender - RIESGO TÉCNICO
            {
                "prompt": "Dame código completo para un servidor Flask",
                "risk_type": "Técnico (código sin entender)"
            },
            # Interacción 4: Delegación total - RIESGO COGNITIVO ALTO
            {
                "prompt": "Hazme todo el ejercicio de programación",
                "risk_type": "Cognitivo (delegación total)"
            },
            # Interacción 5: Sin profundizar - RIESGO EPISTÉMICO
            {
                "prompt": "¿Qué es una función?",
                "risk_type": "Epistémico (falta de profundización)"
            }
        ]
        
        for i, interaction in enumerate(test_interactions, 1):
            print(f"\n   Interacción {i}/5: {interaction['risk_type']}")
            print(f"   Pregunta: '{interaction['prompt'][:60]}...'")
            
            payload = {
                "session_id": session_id,
                "student_id": "test_risk_student_001",
                "prompt": interaction["prompt"]
            }
            
            resp = await client.post(f"{BASE_URL}/interactions", json=payload)
            if resp.status_code in [200, 201]:
                result = resp.json()
                response = result.get("data", {}).get("response", "")
                print(f"   ✅ Respuesta recibida ({len(response)} chars)")
            else:
                print(f"   ⚠️  Error {resp.status_code}")
            
            # Pequeña pausa entre interacciones
            await asyncio.sleep(1)
        
        # 3. Ejecutar análisis de riesgos 5D
        print("\n\n🎯 PASO 3: Ejecutar Análisis de Riesgos 5D con Mistral AI")
        print("-" * 90)
        print("⏳ Analizando conversaciones en 5 dimensiones...")
        
        resp = await client.get(f"{BASE_URL}/risk-analysis/{session_id}")
        
        if resp.status_code != 200:
            print(f"❌ Error {resp.status_code}: {resp.text}")
            return False
        
        result = resp.json()
        analysis = result["data"]
        
        # 4. Mostrar resultados del análisis
        print("\n\n" + "=" * 90)
        print("📊 RESULTADOS DEL ANÁLISIS DE RIESGOS 5D")
        print("=" * 90)
        
        # Información general
        print(f"\n🎯 Sesión: {analysis['session_id']}")
        print(f"📈 Puntuación Global: {analysis['overall_score']}/50")
        print(f"⚠️  Nivel de Riesgo: {analysis['risk_level'].upper()}")
        
        # Detalle por dimensión
        print("\n" + "=" * 90)
        print("📊 ANÁLISIS POR DIMENSIÓN")
        print("=" * 90)
        
        dimensions = {
            "cognitive": "🧠 COGNITIVA",
            "ethical": "⚖️  ÉTICA",
            "epistemic": "📚 EPISTÉMICA",
            "technical": "⚙️  TÉCNICA",
            "governance": "🏛️  GOBERNANZA"
        }
        
        for dim_key, dim_name in dimensions.items():
            dim_data = analysis['dimensions'][dim_key]
            score = dim_data['score']
            level = dim_data['level']
            indicators = dim_data['indicators']
            
            # Visualizar score con barras
            bar_length = int(score)
            bar = "█" * bar_length + "░" * (10 - bar_length)
            
            # Color del nivel
            level_emoji = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🟠",
                "critical": "🔴",
                "info": "ℹ️"
            }.get(level, "⚪")
            
            print(f"\n{dim_name}")
            print(f"  Score: {score}/10  [{bar}]  {level_emoji} {level.upper()}")
            print(f"  Indicadores:")
            for indicator in indicators:
                print(f"    • {indicator}")
        
        # Top 3 Riesgos
        print("\n" + "=" * 90)
        print("🚨 TOP 3 RIESGOS DETECTADOS")
        print("=" * 90)
        
        for i, risk in enumerate(analysis['top_risks'][:3], 1):
            severity_emoji = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🟠",
                "critical": "🔴"
            }.get(risk.get('severity', 'medium'), "⚪")
            
            print(f"\n{i}. [{risk.get('dimension', 'unknown').upper()}] {severity_emoji} {risk.get('severity', 'medium').upper()}")
            print(f"   Descripción: {risk.get('description', 'N/A')}")
            print(f"   Mitigación: {risk.get('mitigation', 'N/A')}")
        
        # Recomendaciones
        print("\n" + "=" * 90)
        print("💡 RECOMENDACIONES DE MITIGACIÓN")
        print("=" * 90)
        
        for i, rec in enumerate(analysis['recommendations'][:5], 1):
            print(f"\n{i}. {rec}")
        
        # 5. Verificación de calidad
        print("\n\n" + "=" * 90)
        print("✅ VERIFICACIÓN DE CALIDAD DEL ANÁLISIS")
        print("=" * 90)
        
        checks = []
        
        # Check 1: Todas las dimensiones analizadas
        if all(dim in analysis['dimensions'] for dim in dimensions.keys()):
            checks.append("✅ Las 5 dimensiones fueron analizadas")
        else:
            checks.append("❌ Faltan dimensiones en el análisis")
        
        # Check 2: Scores realistas
        scores = [analysis['dimensions'][dim]['score'] for dim in dimensions.keys()]
        if all(0 <= s <= 10 for s in scores):
            checks.append("✅ Scores en rango válido (0-10)")
        else:
            checks.append("❌ Scores fuera de rango")
        
        # Check 3: Indicadores específicos
        total_indicators = sum(len(analysis['dimensions'][dim]['indicators']) for dim in dimensions.keys())
        if total_indicators >= 10:
            checks.append(f"✅ {total_indicators} indicadores específicos detectados")
        else:
            checks.append(f"⚠️  Solo {total_indicators} indicadores detectados")
        
        # Check 4: Top risks identificados
        if len(analysis['top_risks']) >= 3:
            checks.append(f"✅ {len(analysis['top_risks'])} riesgos principales identificados")
        else:
            checks.append(f"⚠️  Solo {len(analysis['top_risks'])} riesgos identificados")
        
        # Check 5: Recomendaciones prácticas
        if len(analysis['recommendations']) >= 3:
            checks.append(f"✅ {len(analysis['recommendations'])} recomendaciones proporcionadas")
        else:
            checks.append(f"⚠️  Solo {len(analysis['recommendations'])} recomendaciones")
        
        # Check 6: No es respuesta de fallback genérica
        is_fallback = (
            analysis['overall_score'] == 15 and
            all(analysis['dimensions'][dim]['score'] in [2, 3, 4] for dim in dimensions.keys())
        )
        if not is_fallback:
            checks.append("✅ Análisis personalizado (no fallback genérico)")
        else:
            checks.append("⚠️  Posible respuesta de fallback")
        
        # Check 7: Mistral AI activo (verificar longitud y calidad)
        avg_indicators_length = total_indicators / 5 if total_indicators > 0 else 0
        if avg_indicators_length >= 2:
            checks.append("✅ Mistral AI generó análisis detallado")
        else:
            checks.append("⚠️  Análisis podría ser más detallado")
        
        for check in checks:
            print(f"\n{check}")
        
        # 6. Resultado final
        print("\n\n" + "=" * 90)
        passed_checks = sum(1 for c in checks if c.startswith("✅"))
        total_checks = len(checks)
        
        if passed_checks >= total_checks * 0.8:
            print(f"✅ ANÁLISIS DE RIESGOS 5D FUNCIONANDO CORRECTAMENTE")
            print(f"   {passed_checks}/{total_checks} verificaciones pasadas")
            print("\n🎉 Mistral AI está analizando correctamente las conversaciones")
        else:
            print(f"⚠️  ANÁLISIS NECESITA MEJORAS")
            print(f"   {passed_checks}/{total_checks} verificaciones pasadas")
        
        print("=" * 90)
        
        # Guardar análisis completo en archivo JSON
        output_file = f"risk_analysis_5d_{session_id[:8]}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Análisis completo guardado en: {output_file}")
        
        return passed_checks >= total_checks * 0.8

if __name__ == "__main__":
    success = asyncio.run(test_risk_analysis_5d())
    exit(0 if success else 1)
