"""
Frontend Code Analyzer

This script analyzes Vue 3 frontend code to identify areas for improvement
including UI/UX enhancements, accessibility issues, styling inconsistencies,
and missing responsive design implementations.

Usage:
    python analyze_frontend.py <frontend_directory>
    
Example:
    python analyze_frontend.py ../code/code/frontend/DsAgentChat_web/src
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


class FrontendAnalyzer:
    """Analyzer for Vue 3 frontend code."""
    
    def __init__(self, directory: str):
        """
        Initialize the analyzer.
        
        Args:
            directory: Path to the frontend source directory
        """
        self.directory = Path(directory)
        self.issues = {
            "accessibility": [],
            "styling": [],
            "responsive": [],
            "ui_ux": [],
            "performance": [],
            "best_practices": []
        }
        self.stats = {
            "total_files": 0,
            "vue_components": 0,
            "typescript_files": 0,
            "style_blocks": 0,
            "total_lines": 0
        }
    
    def analyze(self) -> Dict:
        """
        Run complete analysis on frontend code.
        
        Returns:
            Dictionary containing analysis results
        """
        print(f"Analyzing frontend code in: {self.directory}")
        
        # Analyze all files
        for file_path in self.directory.rglob("*"):
            if file_path.is_file():
                self._analyze_file(file_path)
        
        # Generate summary
        summary = self._generate_summary()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "directory": str(self.directory),
            "stats": self.stats,
            "issues": self.issues,
            "summary": summary
        }
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single file."""
        self.stats["total_files"] += 1
        
        # Determine file type
        if file_path.suffix == ".vue":
            self.stats["vue_components"] += 1
            self._analyze_vue_component(file_path)
        elif file_path.suffix in [".ts", ".tsx"]:
            self.stats["typescript_files"] += 1
            self._analyze_typescript_file(file_path)
    
    def _analyze_vue_component(self, file_path: Path):
        """Analyze a Vue component file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            self.stats["total_lines"] += len(content.splitlines())
            
            # Check for accessibility issues
            self._check_accessibility(file_path, content)
            
            # Check for styling issues
            self._check_styling(file_path, content)
            
            # Check for responsive design
            self._check_responsive_design(file_path, content)
            
            # Check UI/UX patterns
            self._check_ui_ux(file_path, content)
            
            # Check performance issues
            self._check_performance(file_path, content)
            
            # Check best practices
            self._check_best_practices(file_path, content)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _analyze_typescript_file(self, file_path: Path):
        """Analyze a TypeScript file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            self.stats["total_lines"] += len(content.splitlines())
            
            # Check for best practices
            self._check_typescript_best_practices(file_path, content)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _check_accessibility(self, file_path: Path, content: str):
        """Check for accessibility issues."""
        issues = []
        
        # Check for missing ARIA labels
        if re.search(r'<button[^>]*>', content) and not re.search(r'aria-label', content):
            issues.append("Missing aria-label on buttons")
        
        if re.search(r'<input[^>]*>', content) and not re.search(r'aria-label|<label', content):
            issues.append("Missing labels or aria-label on inputs")
        
        # Check for missing alt text on images
        if re.search(r'<img[^>]*>', content) and not re.search(r'alt=', content):
            issues.append("Missing alt text on images")
        
        # Check for keyboard navigation
        if re.search(r'@click', content) and not re.search(r'@keydown|@keyup|@keypress', content):
            issues.append("Click handlers without keyboard event handlers")
        
        # Check for focus management
        if not re.search(r':focus|focus\(', content):
            issues.append("No focus management detected")
        
        for issue in issues:
            self.issues["accessibility"].append({
                "file": str(file_path.relative_to(self.directory)),
                "issue": issue,
                "severity": "medium"
            })
    
    def _check_styling(self, file_path: Path, content: str):
        """Check for styling inconsistencies."""
        issues = []
        
        # Check for inline styles
        if re.search(r'style="[^"]*"', content):
            issues.append("Inline styles detected (prefer CSS classes)")
        
        # Check for hardcoded colors
        color_pattern = r'#[0-9a-fA-F]{3,6}|rgb\(|rgba\('
        if re.search(color_pattern, content):
            issues.append("Hardcoded colors (consider using CSS variables)")
        
        # Check for scoped styles
        if '<style' in content and 'scoped' not in content:
            issues.append("Style block not scoped (may cause global style conflicts)")
        
        # Check for CSS preprocessor
        if '<style' in content and not re.search(r'lang="(scss|sass|less)"', content):
            issues.append("Not using CSS preprocessor (consider SCSS for better maintainability)")
        
        for issue in issues:
            self.issues["styling"].append({
                "file": str(file_path.relative_to(self.directory)),
                "issue": issue,
                "severity": "low"
            })
    
    def _check_responsive_design(self, file_path: Path, content: str):
        """Check for responsive design implementation."""
        issues = []
        
        # Check for media queries
        if '<style' in content and not re.search(r'@media', content):
            issues.append("No media queries detected (may not be responsive)")
        
        # Check for fixed widths
        if re.search(r'width:\s*\d+px', content):
            issues.append("Fixed pixel widths detected (consider using relative units)")
        
        # Check for viewport meta tag (in HTML files)
        if file_path.name == "index.html" and 'viewport' not in content:
            issues.append("Missing viewport meta tag")
        
        # Check for responsive units
        if not re.search(r'(rem|em|%|vw|vh)', content):
            issues.append("Not using responsive units (rem, em, %, vw, vh)")
        
        for issue in issues:
            self.issues["responsive"].append({
                "file": str(file_path.relative_to(self.directory)),
                "issue": issue,
                "severity": "high"
            })
    
    def _check_ui_ux(self, file_path: Path, content: str):
        """Check for UI/UX improvements."""
        issues = []
        
        # Check for loading states
        if re.search(r'async|await|fetch|axios', content) and not re.search(r'loading|isLoading', content):
            issues.append("Async operations without loading state")
        
        # Check for error handling
        if re.search(r'async|await|fetch|axios', content) and not re.search(r'error|catch', content):
            issues.append("Async operations without error handling")
        
        # Check for empty states
        if re.search(r'v-for', content) and not re.search(r'v-if.*length|empty', content):
            issues.append("Lists without empty state handling")
        
        # Check for transitions
        if not re.search(r'<transition|<Transition', content):
            issues.append("No transitions detected (consider adding for better UX)")
        
        for issue in issues:
            self.issues["ui_ux"].append({
                "file": str(file_path.relative_to(self.directory)),
                "issue": issue,
                "severity": "medium"
            })
    
    def _check_performance(self, file_path: Path, content: str):
        """Check for performance issues."""
        issues = []
        
        # Check for v-for without key
        if re.search(r'v-for', content) and not re.search(r':key', content):
            issues.append("v-for without :key (performance issue)")
        
        # Check for computed vs methods
        if re.search(r'methods:', content) and not re.search(r'computed:', content):
            issues.append("Using methods instead of computed properties (consider computed for derived state)")
        
        # Check for large inline data
        if re.search(r'data\(\).*\{[\s\S]{500,}', content):
            issues.append("Large inline data (consider lazy loading or splitting)")
        
        for issue in issues:
            self.issues["performance"].append({
                "file": str(file_path.relative_to(self.directory)),
                "issue": issue,
                "severity": "medium"
            })
    
    def _check_best_practices(self, file_path: Path, content: str):
        """Check for Vue best practices."""
        issues = []
        
        # Check for component naming
        if file_path.suffix == ".vue" and not re.match(r'^[A-Z]', file_path.stem):
            issues.append("Component name should be PascalCase")
        
        # Check for prop validation
        if re.search(r'props:', content) and not re.search(r'type:|validator:', content):
            issues.append("Props without type validation")
        
        # Check for emit declarations
        if re.search(r'\$emit', content) and not re.search(r'emits:', content):
            issues.append("Using $emit without emits declaration")
        
        # Check for script setup
        if '<script' in content and 'setup' not in content:
            issues.append("Not using <script setup> (consider for better DX)")
        
        for issue in issues:
            self.issues["best_practices"].append({
                "file": str(file_path.relative_to(self.directory)),
                "issue": issue,
                "severity": "low"
            })
    
    def _check_typescript_best_practices(self, file_path: Path, content: str):
        """Check TypeScript best practices."""
        issues = []
        
        # Check for any types
        if re.search(r':\s*any', content):
            issues.append("Using 'any' type (reduces type safety)")
        
        # Check for type assertions
        if re.search(r'as\s+\w+', content):
            issues.append("Type assertions detected (may hide type errors)")
        
        # Check for interfaces vs types
        if not re.search(r'interface|type\s+\w+\s*=', content):
            issues.append("No type definitions (consider adding interfaces/types)")
        
        for issue in issues:
            self.issues["best_practices"].append({
                "file": str(file_path.relative_to(self.directory)),
                "issue": issue,
                "severity": "low"
            })
    
    def _generate_summary(self) -> Dict:
        """Generate analysis summary."""
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        return {
            "total_issues": total_issues,
            "issues_by_category": {
                category: len(issues)
                for category, issues in self.issues.items()
            },
            "issues_by_severity": self._count_by_severity(),
            "recommendations": self._generate_recommendations()
        }
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Count issues by severity."""
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        
        for issues in self.issues.values():
            for issue in issues:
                severity = issue.get("severity", "low")
                severity_counts[severity] += 1
        
        return severity_counts
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if len(self.issues["accessibility"]) > 0:
            recommendations.append(
                "Add ARIA labels and keyboard navigation for better accessibility"
            )
        
        if len(self.issues["responsive"]) > 0:
            recommendations.append(
                "Implement responsive design with media queries and relative units"
            )
        
        if len(self.issues["styling"]) > 0:
            recommendations.append(
                "Use CSS variables and scoped styles for consistent styling"
            )
        
        if len(self.issues["ui_ux"]) > 0:
            recommendations.append(
                "Add loading states, error handling, and transitions for better UX"
            )
        
        if len(self.issues["performance"]) > 0:
            recommendations.append(
                "Optimize performance with proper key usage and computed properties"
            )
        
        return recommendations
    
    def save_report(self, output_path: str):
        """Save analysis report to file."""
        results = self.analyze()
        
        # Save JSON report
        json_path = Path(output_path).with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save markdown summary
        md_path = Path(output_path).with_suffix('.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(results))
        
        print(f"\nReports saved:")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")
    
    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate markdown report."""
        md = "# Frontend Code Analysis Report\n\n"
        md += f"**Generated**: {results['timestamp']}\n\n"
        md += f"**Directory**: {results['directory']}\n\n"
        
        # Statistics
        md += "## Statistics\n\n"
        for key, value in results['stats'].items():
            md += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        md += "\n"
        
        # Summary
        md += "## Summary\n\n"
        summary = results['summary']
        md += f"- **Total Issues**: {summary['total_issues']}\n"
        md += f"- **High Severity**: {summary['issues_by_severity']['high']}\n"
        md += f"- **Medium Severity**: {summary['issues_by_severity']['medium']}\n"
        md += f"- **Low Severity**: {summary['issues_by_severity']['low']}\n\n"
        
        # Issues by category
        md += "## Issues by Category\n\n"
        for category, count in summary['issues_by_category'].items():
            md += f"- **{category.replace('_', ' ').title()}**: {count}\n"
        md += "\n"
        
        # Recommendations
        md += "## Recommendations\n\n"
        for i, rec in enumerate(summary['recommendations'], 1):
            md += f"{i}. {rec}\n"
        md += "\n"
        
        # Detailed issues
        md += "## Detailed Issues\n\n"
        for category, issues in results['issues'].items():
            if issues:
                md += f"### {category.replace('_', ' ').title()}\n\n"
                for issue in issues[:10]:  # Limit to first 10 per category
                    md += f"- **{issue['file']}**: {issue['issue']} "
                    md += f"(Severity: {issue['severity']})\n"
                if len(issues) > 10:
                    md += f"\n*...and {len(issues) - 10} more issues*\n"
                md += "\n"
        
        return md


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_frontend.py <frontend_directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.exists(directory):
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)
    
    analyzer = FrontendAnalyzer(directory)
    
    # Create output directory
    output_dir = Path("docs/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save report
    output_path = output_dir / "frontend_analysis_report"
    analyzer.save_report(str(output_path))
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
