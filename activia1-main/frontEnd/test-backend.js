/**
 * Test Script - Verificar todos los agentes del backend
 */

const API_BASE = 'http://localhost:8000/api/v1';

async function testBackend() {
  console.log('🧪 INICIANDO TESTS DEL BACKEND...\n');

  // 1. Health Check
  console.log('1️⃣ Testing Health Check...');
  try {
    const health = await fetch(`${API_BASE}/health`);
    const data = await health.json();
    console.log('✅ Health:', data);
  } catch (error) {
    console.error('❌ Health failed:', error);
  }

  // 2. Crear Sesión
  console.log('\n2️⃣ Testing Session Creation...');
  let sessionId = '';
  try {
    const sessionResponse = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: 'test_student_001',
        activity_id: 'test_activity',
        mode: 'TUTOR' // Backend expects uppercase
      })
    });
    const sessionData = await sessionResponse.json();
    sessionId = sessionData.data.id; // Backend wraps response in {success, data}
    console.log('✅ Session created:', sessionData);
  } catch (error) {
    console.error('❌ Session creation failed:', error);
  }

  if (!sessionId) {
    console.error('❌ No se pudo crear sesión. Abortando tests.');
    return;
  }

  // 3. Test Tutor (T-IA-Cog)
  console.log('\n3️⃣ Testing Tutor Cognitivo (T-IA-Cog)...');
  try {
    const tutorResponse = await fetch(`${API_BASE}/interactions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        prompt: '¿Qué es una función recursiva en programación?',
        context: {}
      })
    });
    const tutorData = await tutorResponse.json();
    console.log('✅ Tutor response:', tutorData.data ? tutorData.data.response.substring(0, 150) + '...' : tutorData);
  } catch (error) {
    console.error('❌ Tutor failed:', error);
  }

  // 4. Test Evaluator (E-IA-Proc)
  console.log('\n4️⃣ Testing Evaluador (E-IA-Proc)...');
  try {
    // Primero necesitamos algunas trazas
    const evalResponse = await fetch(`${API_BASE}/risks/analyze/${sessionId}`, {
      method: 'POST'
    });
    const evalData = await evalResponse.json();
    console.log('✅ Evaluator response:', evalData);
  } catch (error) {
    console.error('❌ Evaluator failed:', error);
  }

  // 5. Test Risk Analyst (AR-IA)
  console.log('\n5️⃣ Testing Risk Analyst (AR-IA)...');
  try {
    const riskResponse = await fetch(`${API_BASE}/risks/analyze/${sessionId}`, {
      method: 'POST'
    });
    const riskData = await riskResponse.json();
    console.log('✅ Risk analysis:', riskData);
  } catch (error) {
    console.error('❌ Risk analysis failed:', error);
  }

  // 6. Test Simulators (S-IA-X)
  console.log('\n6️⃣ Testing Simuladores (S-IA-X)...');
  const simulators = ['product_owner', 'scrum_master', 'tech_interviewer'];
  
  for (const simulator of simulators) {
    try {
      const simResponse = await fetch(`${API_BASE}/simulators/interact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          simulator_type: simulator,
          student_input: 'Hola, necesito ayuda con una feature',
          context: {}
        })
      });
      const simData = await simResponse.json();
      console.log(`✅ ${simulator}:`, simData.message.substring(0, 100) + '...');
    } catch (error) {
      console.error(`❌ ${simulator} failed:`, error);
    }
  }

  // 7. Test Traces (TC-N4)
  console.log('\n7️⃣ Testing Trazabilidad (TC-N4)...');
  try {
    const tracesResponse = await fetch(`${API_BASE}/traces/session/${sessionId}`);
    const tracesData = await tracesResponse.json();
    console.log('✅ Traces:', tracesData);
  } catch (error) {
    console.error('❌ Traces failed:', error);
  }

  console.log('\n✅ TESTS COMPLETADOS!');
}

// Ejecutar tests
testBackend().catch(console.error);
