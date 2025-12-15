#!/usr/bin/env python3
"""
AI-Native MVP - Security Audit Analyzer
Author: Mag. Alberto Cortez
Date: 2025-11-24

Analyzes security scan results and generates actionable insights.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import xml.etree.ElementTree as ET

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class SecurityAnalyzer:
    """Analyzes security scan results from multiple tools."""

    def __init__(self, reports_dir: str = "./reports"):
        self.reports_dir = Path(reports_dir)
        self.findings = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'informational': []
        }

    def analyze_zap_report(self, report_path: Path):
        """Analyze OWASP ZAP JSON report."""
        if not report_path.exists():
            print(f"⚠️  ZAP report not found: {report_path}")
            return

        print("Analyzing OWASP ZAP report...")

        with open(report_path, 'r') as f:
            data = json.load(f)

        site = data.get('site', [{}])[0]
        alerts = site.get('alerts', [])

        for alert in alerts:
            risk = alert.get('riskdesc', '').split()[0].lower()

            finding = {
                'tool': 'OWASP ZAP',
                'name': alert.get('name', 'Unknown'),
                'risk': risk,
                'confidence': alert.get('confidence', 'Unknown'),
                'description': alert.get('desc', ''),
                'solution': alert.get('solution', ''),
                'references': alert.get('reference', ''),
                'cweid': alert.get('cweid', ''),
                'wascid': alert.get('wascid', ''),
                'instances': len(alert.get('instances', []))
            }

            if risk in self.findings:
                self.findings[risk].append(finding)

        print(f"  Found {len(alerts)} unique alerts")

    def analyze_trivy_report(self, report_path: Path):
        """Analyze Trivy JSON report."""
        if not report_path.exists():
            print(f"⚠️  Trivy report not found: {report_path}")
            return

        print("Analyzing Trivy report...")

        with open(report_path, 'r') as f:
            data = json.load(f)

        results = data.get('Results', [])
        vuln_count = 0

        for result in results:
            vulnerabilities = result.get('Vulnerabilities', [])
            vuln_count += len(vulnerabilities)

            for vuln in vulnerabilities:
                severity = vuln.get('Severity', 'UNKNOWN').lower()

                finding = {
                    'tool': 'Trivy',
                    'name': f"{vuln.get('VulnerabilityID', 'Unknown')} in {vuln.get('PkgName', 'Unknown')}",
                    'risk': severity,
                    'description': vuln.get('Description', 'No description'),
                    'installed_version': vuln.get('InstalledVersion', ''),
                    'fixed_version': vuln.get('FixedVersion', 'Not available'),
                    'references': vuln.get('References', []),
                    'cvss_score': vuln.get('CVSS', {}).get('nvd', {}).get('V3Score', 'N/A')
                }

                if severity in self.findings:
                    self.findings[severity].append(finding)

        print(f"  Found {vuln_count} vulnerabilities")

    def analyze_kubesec_report(self, report_path: Path):
        """Analyze Kubesec JSON report."""
        if not report_path.exists():
            print(f"⚠️  Kubesec report not found: {report_path}")
            return

        print("Analyzing Kubesec report...")

        with open(report_path, 'r') as f:
            data = json.load(f)

        for manifest in data:
            score = manifest.get('score', 0)
            object_name = manifest.get('object', 'Unknown')

            # Critical scoring items
            for critical in manifest.get('scoring', {}).get('critical', []):
                finding = {
                    'tool': 'Kubesec',
                    'name': f"Kubernetes Security Issue in {object_name}",
                    'risk': 'high',
                    'description': critical.get('reason', ''),
                    'selector': critical.get('selector', ''),
                    'score': score
                }
                self.findings['high'].append(finding)

            # Advisory items
            for advisory in manifest.get('scoring', {}).get('advise', []):
                finding = {
                    'tool': 'Kubesec',
                    'name': f"Kubernetes Best Practice for {object_name}",
                    'risk': 'medium',
                    'description': advisory.get('reason', ''),
                    'selector': advisory.get('selector', ''),
                    'score': score
                }
                self.findings['medium'].append(finding)

        print(f"  Analyzed {len(data)} manifests")

    def analyze_trufflehog_report(self, report_path: Path):
        """Analyze TruffleHog JSON report."""
        if not report_path.exists():
            print(f"⚠️  TruffleHog report not found: {report_path}")
            return

        print("Analyzing TruffleHog report...")

        secrets_found = 0
        with open(report_path, 'r') as f:
            for line in f:
                try:
                    secret = json.loads(line)
                    secrets_found += 1

                    finding = {
                        'tool': 'TruffleHog',
                        'name': f"Secret detected: {secret.get('DetectorName', 'Unknown')}",
                        'risk': 'critical',
                        'description': f"Potential secret found in {secret.get('SourceMetadata', {}).get('Data', {}).get('Git', {}).get('file', 'Unknown file')}",
                        'file': secret.get('SourceMetadata', {}).get('Data', {}).get('Git', {}).get('file', ''),
                        'commit': secret.get('SourceMetadata', {}).get('Data', {}).get('Git', {}).get('commit', '')
                    }
                    self.findings['critical'].append(finding)
                except json.JSONDecodeError:
                    continue

        if secrets_found > 0:
            print(f"  ❌ Found {secrets_found} secrets!")
        else:
            print(f"  ✓ No secrets detected")

    def print_summary(self):
        """Print executive summary."""
        print()
        print("=" * 70)
        print("SECURITY AUDIT SUMMARY")
        print("=" * 70)
        print()

        total_findings = sum(len(findings) for findings in self.findings.values())

        print(f"Total Findings: {total_findings}")
        print()

        # Count by severity
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
            'informational': '🔵'
        }

        for severity, findings in self.findings.items():
            if findings:
                emoji = severity_emoji.get(severity, '⚪')
                print(f"{emoji} {severity.upper()}: {len(findings)}")

        print()

        # Count by tool
        tool_counts = defaultdict(int)
        for findings in self.findings.values():
            for finding in findings:
                tool_counts[finding['tool']] += 1

        print("Findings by Tool:")
        for tool, count in sorted(tool_counts.items()):
            print(f"  • {tool}: {count}")

        print()

    def print_critical_findings(self):
        """Print critical and high severity findings."""
        print("=" * 70)
        print("CRITICAL & HIGH SEVERITY FINDINGS")
        print("=" * 70)
        print()

        critical_and_high = self.findings['critical'] + self.findings['high']

        if not critical_and_high:
            print("✅ No critical or high severity findings!")
            print()
            return

        for i, finding in enumerate(critical_and_high, 1):
            severity_emoji = '🔴' if finding['risk'] == 'critical' else '🟠'

            print(f"{severity_emoji} Finding #{i}: {finding['name']}")
            print(f"   Tool: {finding['tool']}")
            print(f"   Severity: {finding['risk'].upper()}")
            print(f"   Description: {finding['description'][:200]}...")

            if 'solution' in finding and finding['solution']:
                print(f"   Solution: {finding['solution'][:150]}...")

            if 'fixed_version' in finding:
                print(f"   Fixed in: {finding['fixed_version']}")

            if 'file' in finding:
                print(f"   File: {finding['file']}")

            print()

    def generate_owasp_top10_mapping(self):
        """Map findings to OWASP Top 10 2021."""
        print("=" * 70)
        print("OWASP TOP 10 2021 MAPPING")
        print("=" * 70)
        print()

        owasp_mapping = {
            'A01:2021 – Broken Access Control': [],
            'A02:2021 – Cryptographic Failures': [],
            'A03:2021 – Injection': [],
            'A04:2021 – Insecure Design': [],
            'A05:2021 – Security Misconfiguration': [],
            'A06:2021 – Vulnerable and Outdated Components': [],
            'A07:2021 – Identification and Authentication Failures': [],
            'A08:2021 – Software and Data Integrity Failures': [],
            'A09:2021 – Security Logging and Monitoring Failures': [],
            'A10:2021 – Server-Side Request Forgery (SSRF)': []
        }

        # Map findings to OWASP categories
        for severity, findings in self.findings.items():
            for finding in findings:
                name = finding['name'].lower()

                if 'injection' in name or 'sql' in name or 'xss' in name:
                    owasp_mapping['A03:2021 – Injection'].append(finding)
                elif 'access control' in name or 'authorization' in name:
                    owasp_mapping['A01:2021 – Broken Access Control'].append(finding)
                elif 'crypto' in name or 'encryption' in name or 'secret' in name:
                    owasp_mapping['A02:2021 – Cryptographic Failures'].append(finding)
                elif 'authentication' in name or 'session' in name:
                    owasp_mapping['A07:2021 – Identification and Authentication Failures'].append(finding)
                elif 'ssrf' in name:
                    owasp_mapping['A10:2021 – Server-Side Request Forgery (SSRF)'].append(finding)
                elif finding['tool'] == 'Trivy':
                    owasp_mapping['A06:2021 – Vulnerable and Outdated Components'].append(finding)
                elif finding['tool'] == 'Kubesec':
                    owasp_mapping['A05:2021 – Security Misconfiguration'].append(finding)

        for category, findings in owasp_mapping.items():
            if findings:
                print(f"✗ {category}: {len(findings)} finding(s)")
            else:
                print(f"✓ {category}: No issues")

        print()

    def generate_recommendations(self):
        """Generate prioritized remediation recommendations."""
        print("=" * 70)
        print("REMEDIATION RECOMMENDATIONS")
        print("=" * 70)
        print()

        recommendations = []

        # Critical findings
        if self.findings['critical']:
            recommendations.append({
                'priority': 'IMMEDIATE',
                'category': 'Critical Vulnerabilities',
                'count': len(self.findings['critical']),
                'actions': [
                    'Review and remove all secrets from Git history',
                    'Rotate compromised credentials immediately',
                    'Implement secrets management (HashiCorp Vault, AWS Secrets Manager)',
                    'Enable Git hooks to prevent future commits with secrets'
                ]
            })

        # High severity
        if self.findings['high']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'High Severity Vulnerabilities',
                'count': len(self.findings['high']),
                'actions': [
                    'Update vulnerable dependencies to patched versions',
                    'Implement input validation and sanitization',
                    'Review and fix security misconfigurations',
                    'Enable security headers (CSP, HSTS, X-Frame-Options)'
                ]
            })

        # Kubernetes security
        kubesec_findings = [f for findings in self.findings.values() for f in findings if f['tool'] == 'Kubesec']
        if kubesec_findings:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Kubernetes Security',
                'count': len(kubesec_findings),
                'actions': [
                    'Add security contexts to all pods (runAsNonRoot: true)',
                    'Implement network policies for pod isolation',
                    'Enable Pod Security Standards (restricted)',
                    'Use read-only root filesystems where possible',
                    'Drop unnecessary capabilities (CAP_NET_RAW, etc.)'
                ]
            })

        # Container security
        trivy_findings = [f for findings in self.findings.values() for f in findings if f['tool'] == 'Trivy']
        if trivy_findings:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Container Security',
                'count': len(trivy_findings),
                'actions': [
                    'Update base images to latest secure versions',
                    'Use minimal base images (Alpine, Distroless)',
                    'Scan images in CI/CD pipeline',
                    'Implement image signing and verification',
                    'Remove unnecessary packages from containers'
                ]
            })

        # Display recommendations
        if recommendations:
            for rec in recommendations:
                priority_emoji = {
                    'IMMEDIATE': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }
                emoji = priority_emoji.get(rec['priority'], '⚪')

                print(f"{emoji} {rec['category']} ({rec['count']} finding(s))")
                print(f"   Priority: {rec['priority']}")
                print(f"   Actions:")
                for action in rec['actions']:
                    print(f"      • {action}")
                print()
        else:
            print("✅ No major security issues found!")
            print()

    def generate_compliance_report(self):
        """Generate compliance status report."""
        print("=" * 70)
        print("COMPLIANCE STATUS")
        print("=" * 70)
        print()

        compliance_checks = {
            'No critical vulnerabilities': len(self.findings['critical']) == 0,
            'No high-severity vulnerabilities': len(self.findings['high']) == 0,
            'No secrets in repository': len([f for f in self.findings['critical'] if f['tool'] == 'TruffleHog']) == 0,
            'Kubernetes security best practices': len([f for findings in self.findings.values() for f in findings if f['tool'] == 'Kubesec']) < 5,
            'No outdated dependencies': len([f for findings in self.findings.values() for f in findings if f['tool'] == 'Trivy' and f['risk'] in ['critical', 'high']]) == 0,
        }

        total_checks = len(compliance_checks)
        passed_checks = sum(1 for passed in compliance_checks.values() if passed)

        print(f"Compliance Score: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.0f}%)")
        print()

        for check, passed in compliance_checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check}")

        print()

        if passed_checks == total_checks:
            print("🎉 System is compliant with security best practices!")
        elif passed_checks >= total_checks * 0.8:
            print("⚠️  Minor compliance issues found. Review recommendations.")
        else:
            print("❌ Major compliance issues found. Immediate action required.")

        print()

    def run_full_analysis(self):
        """Run complete security analysis."""
        print()
        print("Starting security analysis...")
        print()

        # Analyze all available reports
        zap_json = self.reports_dir / "zap-security-report.json"
        zap_baseline = self.reports_dir / "zap-baseline-report.json"
        zap_full = self.reports_dir / "zap-full-report.json"

        if zap_json.exists():
            self.analyze_zap_report(zap_json)
        elif zap_baseline.exists():
            self.analyze_zap_report(zap_baseline)
        elif zap_full.exists():
            self.analyze_zap_report(zap_full)

        trivy_reports = list(self.reports_dir.glob("trivy*.json"))
        for trivy_report in trivy_reports:
            self.analyze_trivy_report(trivy_report)

        kubesec_report = self.reports_dir / "kubesec-report.json"
        self.analyze_kubesec_report(kubesec_report)

        trufflehog_report = self.reports_dir / "trufflehog-report.json"
        self.analyze_trufflehog_report(trufflehog_report)

        print()

        # Generate reports
        self.print_summary()
        self.print_critical_findings()
        self.generate_owasp_top10_mapping()
        self.generate_recommendations()
        self.generate_compliance_report()


def main():
    print()
    print("=" * 70)
    print("AI-NATIVE MVP - SECURITY AUDIT ANALYZER")
    print("=" * 70)

    reports_dir = sys.argv[1] if len(sys.argv) > 1 else "./reports"

    if not Path(reports_dir).exists():
        print(f"❌ Error: Reports directory not found: {reports_dir}")
        print()
        print("Usage: python analyze-security.py [reports_dir]")
        print()
        print("Example:")
        print("  python analyze-security.py ./reports")
        sys.exit(1)

    analyzer = SecurityAnalyzer(reports_dir)
    analyzer.run_full_analysis()

    print("=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()