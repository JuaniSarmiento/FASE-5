/**
 * RisksPage - Page for Risk Analyzer feature
 * FIX 2.1: Create missing frontend pages (Cortez2 audit)
 */
// FIX Cortez16: Use named export instead of default
import { RiskAnalyzer } from '../features/risks/components/RiskAnalyzer';

export default function RisksPage() {
  return <RiskAnalyzer />;
}
