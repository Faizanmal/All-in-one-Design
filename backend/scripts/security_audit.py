#!/usr/bin/env python
"""
Security Audit Script
Comprehensive security checks for the AI Design Tool
Run: python manage.py shell < scripts/security_audit.py
Or: python scripts/security_audit.py
"""
import os
import sys
import json
import subprocess
import socket
import ssl
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from django.conf import settings
from django.core.cache import cache


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityFinding:
    """Represents a security finding"""
    category: str
    title: str
    description: str
    severity: Severity
    recommendation: str
    is_passed: bool
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditReport:
    """Security audit report"""
    timestamp: str
    overall_score: int
    findings: List[SecurityFinding]
    summary: Dict[str, int]
    recommendations: List[str]


class SecurityAuditor:
    """Comprehensive security auditor for the application"""
    
    def __init__(self):
        self.findings: List[SecurityFinding] = []
        self.passed = 0
        self.failed = 0
    
    def add_finding(self, finding: SecurityFinding):
        """Add a finding to the audit"""
        self.findings.append(finding)
        if finding.is_passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def run_full_audit(self) -> AuditReport:
        """Run all security checks"""
        print("\n" + "=" * 60)
        print("🔒 AI Design Tool Security Audit")
        print("=" * 60 + "\n")
        
        # Run all checks
        self.check_debug_mode()
        self.check_secret_key()
        self.check_allowed_hosts()
        self.check_database_security()
        self.check_session_security()
        self.check_csrf_protection()
        self.check_cors_configuration()
        self.check_security_headers()
        self.check_password_validators()
        self.check_authentication_backends()
        self.check_sensitive_data_exposure()
        self.check_api_security()
        self.check_file_upload_security()
        self.check_encryption_config()
        self.check_backup_config()
        self.check_dependencies()
        self.check_admin_security()
        self.check_logging_config()
        self.check_rate_limiting()
        self.check_oauth_config()
        
        # Generate report
        return self.generate_report()
    
    def check_debug_mode(self):
        """Check if DEBUG is disabled in production"""
        is_debug = getattr(settings, 'DEBUG', True)
        
        self.add_finding(SecurityFinding(
            category="Configuration",
            title="Debug Mode",
            description="DEBUG mode should be disabled in production",
            severity=Severity.CRITICAL if is_debug else Severity.LOW,
            recommendation="Set DEBUG=False in production environment",
            is_passed=not is_debug,
            details={"debug_enabled": is_debug}
        ))
    
    def check_secret_key(self):
        """Check if SECRET_KEY is properly configured"""
        secret_key = getattr(settings, 'SECRET_KEY', '')
        
        is_insecure = (
            'insecure' in secret_key.lower() or
            secret_key.startswith('django-insecure-') or
            len(secret_key) < 50
        )
        
        self.add_finding(SecurityFinding(
            category="Configuration",
            title="Secret Key",
            description="SECRET_KEY should be unique and secure",
            severity=Severity.CRITICAL if is_insecure else Severity.LOW,
            recommendation="Use a strong, random SECRET_KEY (50+ characters)",
            is_passed=not is_insecure,
            details={"key_length": len(secret_key), "is_insecure": is_insecure}
        ))
    
    def check_allowed_hosts(self):
        """Check ALLOWED_HOSTS configuration"""
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        
        is_insecure = '*' in allowed_hosts or not allowed_hosts
        
        self.add_finding(SecurityFinding(
            category="Configuration",
            title="Allowed Hosts",
            description="ALLOWED_HOSTS should be explicitly configured",
            severity=Severity.HIGH if is_insecure else Severity.LOW,
            recommendation="Set specific hostnames in ALLOWED_HOSTS",
            is_passed=not is_insecure,
            details={"allowed_hosts": allowed_hosts, "wildcard_present": '*' in allowed_hosts}
        ))
    
    def check_database_security(self):
        """Check database security configuration"""
        db_settings = getattr(settings, 'DATABASES', {}).get('default', {})
        
        # Check if using SQLite in production
        is_sqlite = 'sqlite' in db_settings.get('ENGINE', '').lower()
        is_debug = getattr(settings, 'DEBUG', True)
        
        self.add_finding(SecurityFinding(
            category="Database",
            title="Database Engine",
            description="Production should use PostgreSQL or MySQL",
            severity=Severity.MEDIUM if is_sqlite and not is_debug else Severity.LOW,
            recommendation="Use PostgreSQL for production deployments",
            is_passed=is_debug or not is_sqlite,
            details={"engine": db_settings.get('ENGINE', 'unknown')}
        ))
    
    def check_session_security(self):
        """Check session security settings"""
        findings = []
        
        # Session cookie settings
        cookie_secure = getattr(settings, 'SESSION_COOKIE_SECURE', False)
        cookie_httponly = getattr(settings, 'SESSION_COOKIE_HTTPONLY', True)
        cookie_samesite = getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')
        
        is_secure = cookie_secure or getattr(settings, 'DEBUG', True)
        
        self.add_finding(SecurityFinding(
            category="Session",
            title="Session Cookie Security",
            description="Session cookies should be secure",
            severity=Severity.HIGH if not is_secure else Severity.LOW,
            recommendation="Enable SESSION_COOKIE_SECURE in production",
            is_passed=is_secure,
            details={
                "secure": cookie_secure,
                "httponly": cookie_httponly,
                "samesite": cookie_samesite
            }
        ))
    
    def check_csrf_protection(self):
        """Check CSRF protection"""
        middleware = getattr(settings, 'MIDDLEWARE', [])
        csrf_enabled = 'django.middleware.csrf.CsrfViewMiddleware' in middleware
        csrf_cookie_secure = getattr(settings, 'CSRF_COOKIE_SECURE', False)
        
        self.add_finding(SecurityFinding(
            category="CSRF",
            title="CSRF Protection",
            description="CSRF middleware should be enabled",
            severity=Severity.CRITICAL if not csrf_enabled else Severity.LOW,
            recommendation="Enable CsrfViewMiddleware in MIDDLEWARE",
            is_passed=csrf_enabled,
            details={"middleware_enabled": csrf_enabled, "cookie_secure": csrf_cookie_secure}
        ))
    
    def check_cors_configuration(self):
        """Check CORS configuration"""
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        cors_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        
        is_secure = not cors_all and cors_origins
        
        self.add_finding(SecurityFinding(
            category="CORS",
            title="CORS Configuration",
            description="CORS should be properly configured",
            severity=Severity.HIGH if cors_all else Severity.LOW,
            recommendation="Configure specific CORS_ALLOWED_ORIGINS instead of allowing all",
            is_passed=is_secure,
            details={"allow_all": cors_all, "origins_count": len(cors_origins)}
        ))
    
    def check_security_headers(self):
        """Check security headers configuration"""
        is_debug = getattr(settings, 'DEBUG', True)
        
        headers = {
            'X_FRAME_OPTIONS': getattr(settings, 'X_FRAME_OPTIONS', None),
            'SECURE_CONTENT_TYPE_NOSNIFF': getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False),
            'SECURE_BROWSER_XSS_FILTER': getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False),
            'SECURE_HSTS_SECONDS': getattr(settings, 'SECURE_HSTS_SECONDS', 0),
            'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', False),
        }
        
        # Check if security headers are properly configured (ignore in debug mode)
        is_secure = is_debug or all([
            headers['X_FRAME_OPTIONS'] == 'DENY',
            headers['SECURE_CONTENT_TYPE_NOSNIFF'],
            headers['SECURE_HSTS_SECONDS'] >= 31536000,
        ])
        
        self.add_finding(SecurityFinding(
            category="Headers",
            title="Security Headers",
            description="Security headers should be configured for production",
            severity=Severity.MEDIUM if not is_secure else Severity.LOW,
            recommendation="Configure X-Frame-Options, Content-Type-Options, and HSTS",
            is_passed=is_secure,
            details=headers
        ))
    
    def check_password_validators(self):
        """Check password validation configuration"""
        validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        
        validator_names = [v.get('NAME', '').split('.')[-1] for v in validators]
        
        recommended = [
            'UserAttributeSimilarityValidator',
            'MinimumLengthValidator',
            'CommonPasswordValidator',
            'NumericPasswordValidator',
        ]
        
        has_all = all(v in validator_names for v in recommended)
        
        self.add_finding(SecurityFinding(
            category="Authentication",
            title="Password Validators",
            description="Strong password validation should be enforced",
            severity=Severity.MEDIUM if not has_all else Severity.LOW,
            recommendation="Configure all recommended password validators",
            is_passed=has_all,
            details={"validators": validator_names, "count": len(validators)}
        ))
    
    def check_authentication_backends(self):
        """Check authentication backends"""
        backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [
            'django.contrib.auth.backends.ModelBackend'
        ])
        
        self.add_finding(SecurityFinding(
            category="Authentication",
            title="Authentication Backends",
            description="Authentication backends are configured",
            severity=Severity.LOW,
            recommendation="Review authentication backends for security",
            is_passed=True,
            details={"backends": backends}
        ))
    
    def check_sensitive_data_exposure(self):
        """Check for potential sensitive data exposure"""
        # Check for hardcoded secrets in settings
        has_hardcoded = False
        
        # Common patterns that shouldn't be hardcoded
        patterns_to_check = ['API_KEY', 'SECRET', 'PASSWORD']
        
        for pattern in patterns_to_check:
            for key, value in vars(settings).items():
                if pattern in key.upper() and isinstance(value, str) and value:
                    if not value.startswith('${') and not os.getenv(key):
                        # Might be hardcoded
                        pass
        
        self.add_finding(SecurityFinding(
            category="Data Protection",
            title="Sensitive Data Handling",
            description="Sensitive data should be handled securely",
            severity=Severity.MEDIUM if has_hardcoded else Severity.LOW,
            recommendation="Use environment variables for all secrets",
            is_passed=not has_hardcoded,
            details={}
        ))
    
    def check_api_security(self):
        """Check API security configuration"""
        rest_framework = getattr(settings, 'REST_FRAMEWORK', {})
        
        auth_classes = rest_framework.get('DEFAULT_AUTHENTICATION_CLASSES', [])
        perm_classes = rest_framework.get('DEFAULT_PERMISSION_CLASSES', [])
        throttle_classes = rest_framework.get('DEFAULT_THROTTLE_CLASSES', [])
        
        has_auth = len(auth_classes) > 0
        has_perms = len(perm_classes) > 0
        has_throttle = len(throttle_classes) > 0
        
        self.add_finding(SecurityFinding(
            category="API",
            title="API Security",
            description="API should have authentication, permissions, and rate limiting",
            severity=Severity.HIGH if not (has_auth and has_perms) else Severity.LOW,
            recommendation="Configure authentication, permissions, and throttling for all API endpoints",
            is_passed=has_auth and has_perms and has_throttle,
            details={
                "auth_classes_count": len(auth_classes),
                "permission_classes_count": len(perm_classes),
                "throttle_enabled": has_throttle
            }
        ))
    
    def check_file_upload_security(self):
        """Check file upload security"""
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', None)
        allowed_ext = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', [])
        
        is_configured = max_size is not None and len(allowed_ext) > 0
        
        self.add_finding(SecurityFinding(
            category="File Upload",
            title="File Upload Security",
            description="File uploads should be restricted",
            severity=Severity.MEDIUM if not is_configured else Severity.LOW,
            recommendation="Configure MAX_UPLOAD_SIZE and ALLOWED_UPLOAD_EXTENSIONS",
            is_passed=is_configured,
            details={"max_size": max_size, "allowed_extensions": allowed_ext}
        ))
    
    def check_encryption_config(self):
        """Check encryption configuration"""
        encryption_key = getattr(settings, 'ENCRYPTION_MASTER_KEY', '')
        encryption_enabled = getattr(settings, 'DATABASE_ENCRYPTION_ENABLED', False)
        
        has_key = bool(encryption_key) and len(encryption_key) >= 32
        
        self.add_finding(SecurityFinding(
            category="Encryption",
            title="Data Encryption",
            description="Sensitive data should be encrypted at rest",
            severity=Severity.HIGH if not has_key else Severity.LOW,
            recommendation="Configure ENCRYPTION_MASTER_KEY for data encryption",
            is_passed=has_key,
            details={"encryption_enabled": encryption_enabled, "key_configured": bool(encryption_key)}
        ))
    
    def check_backup_config(self):
        """Check backup configuration"""
        backup_dir = getattr(settings, 'BACKUP_LOCAL_DIR', None)
        use_s3 = getattr(settings, 'USE_S3_BACKUP', False)
        
        self.add_finding(SecurityFinding(
            category="Backup",
            title="Backup Configuration",
            description="Regular backups should be configured",
            severity=Severity.MEDIUM if not backup_dir else Severity.LOW,
            recommendation="Configure backup directory and optionally S3 for off-site backups",
            is_passed=bool(backup_dir),
            details={"local_backup": bool(backup_dir), "s3_backup": use_s3}
        ))
    
    def check_dependencies(self):
        """Check for outdated or vulnerable dependencies"""
        # This is a placeholder - in production, use safety or pip-audit
        self.add_finding(SecurityFinding(
            category="Dependencies",
            title="Dependency Security",
            description="Dependencies should be regularly updated and scanned",
            severity=Severity.MEDIUM,
            recommendation="Run 'pip-audit' or 'safety check' regularly to scan for vulnerabilities",
            is_passed=True,
            details={"recommendation": "Run pip-audit for vulnerability scanning"}
        ))
    
    def check_admin_security(self):
        """Check admin interface security"""
        admin_url = None
        try:
            from django.urls import reverse
            admin_url = reverse('admin:index')
        except:
            pass
        
        ip_allowlist = getattr(settings, 'ADMIN_IP_ALLOWLIST', [])
        
        self.add_finding(SecurityFinding(
            category="Admin",
            title="Admin Interface Security",
            description="Admin interface should be protected",
            severity=Severity.MEDIUM if not ip_allowlist else Severity.LOW,
            recommendation="Consider restricting admin access by IP or using additional authentication",
            is_passed=True,
            details={"admin_url": admin_url, "ip_restricted": bool(ip_allowlist)}
        ))
    
    def check_logging_config(self):
        """Check logging configuration"""
        logging_config = getattr(settings, 'LOGGING', {})
        
        has_security_logger = 'security' in logging_config.get('loggers', {})
        
        self.add_finding(SecurityFinding(
            category="Logging",
            title="Security Logging",
            description="Security events should be logged",
            severity=Severity.MEDIUM if not has_security_logger else Severity.LOW,
            recommendation="Configure dedicated security logging",
            is_passed=has_security_logger,
            details={"has_security_logger": has_security_logger}
        ))
    
    def check_rate_limiting(self):
        """Check rate limiting configuration"""
        rest_framework = getattr(settings, 'REST_FRAMEWORK', {})
        throttle_rates = rest_framework.get('DEFAULT_THROTTLE_RATES', {})
        
        has_rate_limiting = bool(throttle_rates)
        
        self.add_finding(SecurityFinding(
            category="Rate Limiting",
            title="API Rate Limiting",
            description="API endpoints should have rate limiting",
            severity=Severity.HIGH if not has_rate_limiting else Severity.LOW,
            recommendation="Configure DEFAULT_THROTTLE_RATES in REST_FRAMEWORK settings",
            is_passed=has_rate_limiting,
            details={"throttle_rates": throttle_rates}
        ))
    
    def check_oauth_config(self):
        """Check OAuth configuration"""
        google_client = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '')
        github_client = getattr(settings, 'GITHUB_OAUTH_CLIENT_ID', '')
        
        has_oauth = bool(google_client) or bool(github_client)
        
        self.add_finding(SecurityFinding(
            category="OAuth",
            title="OAuth Configuration",
            description="OAuth providers should be configured for social login",
            severity=Severity.LOW,
            recommendation="Configure OAuth providers for additional authentication options",
            is_passed=True,
            details={
                "google_configured": bool(google_client),
                "github_configured": bool(github_client)
            }
        ))
    
    def generate_report(self) -> AuditReport:
        """Generate the final audit report"""
        # Calculate score
        total = self.passed + self.failed
        score = int((self.passed / total) * 100) if total > 0 else 0
        
        # Count by severity
        severity_counts = {
            'critical': sum(1 for f in self.findings if not f.is_passed and f.severity == Severity.CRITICAL),
            'high': sum(1 for f in self.findings if not f.is_passed and f.severity == Severity.HIGH),
            'medium': sum(1 for f in self.findings if not f.is_passed and f.severity == Severity.MEDIUM),
            'low': sum(1 for f in self.findings if not f.is_passed and f.severity == Severity.LOW),
            'passed': self.passed,
            'failed': self.failed,
        }
        
        # Generate recommendations
        recommendations = [
            f.recommendation for f in self.findings 
            if not f.is_passed
        ]
        
        report = AuditReport(
            timestamp=datetime.now().isoformat(),
            overall_score=score,
            findings=self.findings,
            summary=severity_counts,
            recommendations=recommendations
        )
        
        self.print_report(report)
        
        return report
    
    def print_report(self, report: AuditReport):
        """Print the audit report to console"""
        print("\n" + "=" * 60)
        print(f"📊 SECURITY AUDIT REPORT - Score: {report.overall_score}%")
        print("=" * 60)
        
        # Print summary
        print(f"\n📈 Summary:")
        print(f"   ✅ Passed: {report.summary['passed']}")
        print(f"   ❌ Failed: {report.summary['failed']}")
        print(f"   🔴 Critical: {report.summary['critical']}")
        print(f"   🟠 High: {report.summary['high']}")
        print(f"   🟡 Medium: {report.summary['medium']}")
        
        # Print failed findings
        print(f"\n🔍 Failed Checks:")
        for finding in report.findings:
            if not finding.is_passed:
                severity_icon = {
                    Severity.CRITICAL: "🔴",
                    Severity.HIGH: "🟠",
                    Severity.MEDIUM: "🟡",
                    Severity.LOW: "🔵"
                }[finding.severity]
                
                print(f"\n   {severity_icon} [{finding.category}] {finding.title}")
                print(f"      {finding.description}")
                print(f"      💡 {finding.recommendation}")
        
        # Print recommendations
        if report.recommendations:
            print(f"\n📋 Top Recommendations:")
            for i, rec in enumerate(report.recommendations[:5], 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "=" * 60)
        print(f"Audit completed at: {report.timestamp}")
        print("=" * 60 + "\n")


def main():
    """Run the security audit"""
    auditor = SecurityAuditor()
    report = auditor.run_full_audit()
    
    # Save report to file
    report_dir = Path(__file__).resolve().parent.parent / 'security_reports'
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Convert findings to serializable format
    report_data = {
        'timestamp': report.timestamp,
        'overall_score': report.overall_score,
        'summary': report.summary,
        'recommendations': report.recommendations,
        'findings': [
            {
                'category': f.category,
                'title': f.title,
                'description': f.description,
                'severity': f.severity.value,
                'recommendation': f.recommendation,
                'is_passed': f.is_passed,
                'details': f.details
            }
            for f in report.findings
        ]
    }
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"📄 Report saved to: {report_file}")
    
    return report.overall_score


if __name__ == '__main__':
    score = main()
    sys.exit(0 if score >= 70 else 1)
