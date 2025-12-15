/**
 * EvaluatorPage - Page for Process Evaluator feature
 * FIX 2.1: Create missing frontend pages (Cortez2 audit)
 */
// FIX Cortez16: Use named export instead of default
import { ProcessEvaluator } from '../features/evaluator/components/ProcessEvaluator';

export default function EvaluatorPage() {
  return <ProcessEvaluator />;
}
