"""
Test Rápido del Tutor Socrático V2.0

Verifica que todos los componentes estén funcionando correctamente.
"""
import sys
import os

# Añadir el backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_imports():
    """Test 1: Verificar que todos los módulos se importen correctamente"""
    print("🧪 Test 1: Verificando imports...")
    
    try:
        from backend.agents import (
            TutorCognitivoAgent,
            TutorRulesEngine,
            TutorGovernanceEngine,
            TutorMetadataTracker,
            TutorSystemPrompts,
            CognitiveScaffoldingLevel,
            SemaforoState,
            InterventionType,
            StudentCognitiveEvent
        )
        print("   ✅ Todos los imports exitosos\n")
        return True
    except ImportError as e:
        print(f"   ❌ Error en imports: {e}\n")
        return False


def test_rules_engine():
    """Test 2: Verificar TutorRulesEngine"""
    print("🧪 Test 2: Verificando TutorRulesEngine...")
    
    try:
        from backend.agents import TutorRulesEngine, CognitiveScaffoldingLevel
        
        rules = TutorRulesEngine()
        
        # Test regla anti-solución
        result = rules.check_anti_solution_rule(
            student_request="Haceme el código completo",
            student_level=CognitiveScaffoldingLevel.INTERMEDIO
        )
        
        assert result.get("violated") == True, "Debería detectar violación de anti-solución"
        assert "message" in result or "rejection_message" in result
        
        print("   ✅ TutorRulesEngine funcionando correctamente\n")
        return True
    except AssertionError as e:
        print(f"   ❌ Assertion Error: {e}\n")
        return False
    except Exception as e:
        print(f"   ❌ Error en TutorRulesEngine: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_governance_engine():
    """Test 3: Verificar TutorGovernanceEngine"""
    print("🧪 Test 3: Verificando TutorGovernanceEngine...")
    
    try:
        from backend.agents import TutorGovernanceEngine, TutorRulesEngine
        
        rules = TutorRulesEngine()
        governance = TutorGovernanceEngine(rules)
        
        result = governance.process_student_request(
            student_prompt="¿Cómo funciona esto?",
            student_profile={
                "avg_ai_involvement": 0.5,
                "successful_autonomous_solutions": 5
            },
            conversation_history=[]
        )
        
        assert "analysis" in result
        assert "semaforo" in result
        assert "strategy" in result
        
        print("   ✅ TutorGovernanceEngine funcionando correctamente\n")
        return True
    except Exception as e:
        print(f"   ❌ Error en TutorGovernanceEngine: {e}\n")
        return False


def test_metadata_tracker():
    """Test 4: Verificar TutorMetadataTracker"""
    print("🧪 Test 4: Verificando TutorMetadataTracker...")
    
    try:
        from backend.agents import (
            TutorMetadataTracker,
            InterventionType,
            CognitiveScaffoldingLevel,
            SemaforoState
        )
        
        tracker = TutorMetadataTracker()
        
        # Registrar intervención
        metadata = tracker.record_intervention(
            session_id="test_session",
            interaction_id="test_interaction",
            intervention_type=InterventionType.PREGUNTA_SOCRATICA,
            student_level=CognitiveScaffoldingLevel.INTERMEDIO,
            help_level="bajo",
            semaforo_state=SemaforoState.VERDE,
            cognitive_state="exploracion",
            student_intent="clarificacion",
            autonomy_level=0.6,
            rules_applied=["modo_socratico"],
            restrictions_applied=[]
        )
        
        assert metadata is not None
        assert len(tracker.intervention_history) == 1
        
        print("   ✅ TutorMetadataTracker funcionando correctamente\n")
        return True
    except Exception as e:
        print(f"   ❌ Error en TutorMetadataTracker: {e}\n")
        return False


def test_system_prompts():
    """Test 5: Verificar TutorSystemPrompts"""
    print("🧪 Test 5: Verificando TutorSystemPrompts...")
    
    try:
        from backend.agents import (
            TutorSystemPrompts,
            InterventionType,
            CognitiveScaffoldingLevel,
            SemaforoState
        )
        
        prompts = TutorSystemPrompts()
        
        # Generar prompt base
        base_prompt = prompts.get_base_tutor_prompt()
        assert len(base_prompt) > 100
        assert "REGLAS INQUEBRANTABLES" in base_prompt
        
        # Generar prompt específico
        intervention_prompt = prompts.get_intervention_prompt(
            intervention_type=InterventionType.PREGUNTA_SOCRATICA,
            student_level=CognitiveScaffoldingLevel.INTERMEDIO,
            semaforo_state=SemaforoState.VERDE,
            context={}
        )
        
        assert len(intervention_prompt) > 100
        
        print("   ✅ TutorSystemPrompts funcionando correctamente\n")
        return True
    except Exception as e:
        print(f"   ❌ Error en TutorSystemPrompts: {e}\n")
        return False


def test_tutor_agent():
    """Test 6: Verificar TutorCognitivoAgent (integración completa)"""
    print("🧪 Test 6: Verificando TutorCognitivoAgent...")
    
    try:
        from backend.agents import TutorCognitivoAgent
        
        tutor = TutorCognitivoAgent()
        
        # Test 1: Solicitud de código directo (debe rechazar)
        response = tutor.process_student_request(
            session_id="test_session",
            student_prompt="Haceme el código de una cola",
            student_profile={
                "avg_ai_involvement": 0.5,
                "successful_autonomous_solutions": 5
            },
            conversation_history=[]
        )
        
        assert response is not None
        assert "message" in response
        assert "semaforo" in response
        assert "intervention_type" in response
        
        print(f"   📊 Semáforo: {response['semaforo']}")
        print(f"   📊 Intervención: {response['intervention_type']}")
        
        print("   ✅ TutorCognitivoAgent funcionando correctamente\n")
        return True
    except Exception as e:
        print(f"   ❌ Error en TutorCognitivoAgent: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("  TEST RÁPIDO - TUTOR SOCRÁTICO V2.0")
    print("="*60 + "\n")
    
    tests = [
        test_imports,
        test_rules_engine,
        test_governance_engine,
        test_metadata_tracker,
        test_system_prompts,
        test_tutor_agent
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*60)
    print("  RESULTADOS")
    print("="*60 + "\n")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!\n")
        print("El sistema está listo para usar.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) fallaron\n")
        print("Revisar errores arriba.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
