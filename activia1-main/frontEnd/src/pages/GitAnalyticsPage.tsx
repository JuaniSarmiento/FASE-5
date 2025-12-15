/**
 * GitAnalyticsPage - Page for Git Analytics feature
 * FIX 2.1: Create missing frontend pages (Cortez2 audit)
 */
// FIX Cortez16: Use named export instead of default
import { GitAnalytics } from '../features/git/components/GitAnalytics';

export default function GitAnalyticsPage() {
  return <GitAnalytics />;
}
