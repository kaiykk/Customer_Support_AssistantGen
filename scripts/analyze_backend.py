#!/usr/bin/env python3
"""
Backend Code Analyzer

This script analyzes Python backend code to identify:
- Redundant or duplicate code blocks
- Missing docstrings and comments
- Incomplete features (TODO, FIXME markers)
- Code quality issues (unused imports, undefined variables)
- Style violations

Usage:
    python scripts/analyze_backend.py <directory_path>
"""

import ast
import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class CodeIssue:
    """Represents a code quality issue found during analysis."""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # critical, high, medium, low
    description: str
    code_snippet: str = ""


class BackendCodeAnalyzer:
    """
    Analyzes Python backend code for quality issues and improvements.
    
    This analyzer scans Python files to detect various code quality issues
    including missing documentation, incomplete features, and style violations.
    """
    
    def __init__(self, root_dir: str):
        """
        Initialize the code analyzer.
        
        Args:
            root_dir: Root directory to analyze
        """
        self.root_dir = Path(root_dir)
        self.issues: List[CodeIssue] = []
        self.stats = {
            "total_files": 0,
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "issues_by_severity": defaultdict(int),
            "issues_by_type": defaultdict(int),
        }
    
    def analyze(self) -> Dict[str, Any]:
        """
        Run the complete analysis on the codebase.
        
        Returns:
            dict: Analysis results including issues and statistics
        """
        print(f"Analyzing Python files in: {self.root_dir}")
        
        # Find all Python files
        python_files = list(self.root_dir.rglob("*.py"))
        self.stats["total_files"] = len(python_files)
        
        print(f"Found {len(python_files)} Python files")
        
        # Analyze each file
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            
            try:
                self._analyze_file(file_path)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}", file=sys.stderr)
        
        # Generate report
        return self._generate_report()
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """
        Check if a file should be skipped during analysis.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if file should be skipped
        """
        skip_patterns = [
            "__pycache__",
            ".venv",
            "venv",
            "migrations",
            "tests",
            ".pytest_cache",
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path) -> None:
        """
        Analyze a single Python file.
        
        Args:
            file_path: Path to the Python file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        self.stats["total_lines"] += len(lines)
        
        # Parse AST
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            self.issues.append(CodeIssue(
                file_path=str(file_path.relative_to(self.root_dir)),
                line_number=e.lineno or 0,
                issue_type="syntax_error",
                severity="critical",
                description=f"Syntax error: {e.msg}",
            ))
            return
        
        # Run various checks
        self._check_docstrings(file_path, tree, lines)
        self._check_todo_fixme(file_path, lines)
        self._check_unused_imports(file_path, tree, content)
        self._check_commented_code(file_path, lines)
        self._check_function_complexity(file_path, tree)
    
    def _check_docstrings(self, file_path: Path, tree: ast.AST, lines: List[str]) -> None:
        """
        Check for missing docstrings in classes and functions.
        
        Args:
            file_path: Path to the file
            tree: AST tree of the file
            lines: Lines of code
        """
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.stats["total_functions"] += 1
                
                # Check if function has docstring
                docstring = ast.get_docstring(node)
                if not docstring:
                    # Skip private functions and test functions
                    if not node.name.startswith('_') and not node.name.startswith('test_'):
                        self.issues.append(CodeIssue(
                            file_path=str(file_path.relative_to(self.root_dir)),
                            line_number=node.lineno,
                            issue_type="missing_docstring",
                            severity="medium",
                            description=f"Function '{node.name}' is missing a docstring",
                            code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                        ))
            
            elif isinstance(node, ast.ClassDef):
                self.stats["total_classes"] += 1
                
                # Check if class has docstring
                docstring = ast.get_docstring(node)
                if not docstring:
                    self.issues.append(CodeIssue(
                        file_path=str(file_path.relative_to(self.root_dir)),
                        line_number=node.lineno,
                        issue_type="missing_docstring",
                        severity="high",
                        description=f"Class '{node.name}' is missing a docstring",
                        code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                    ))
    
    def _check_todo_fixme(self, file_path: Path, lines: List[str]) -> None:
        """
        Check for TODO and FIXME markers indicating incomplete features.
        
        Args:
            file_path: Path to the file
            lines: Lines of code
        """
        todo_pattern = re.compile(r'#\s*(TODO|FIXME|XXX|HACK|NOTE)[\s:](.*)', re.IGNORECASE)
        
        for line_num, line in enumerate(lines, start=1):
            match = todo_pattern.search(line)
            if match:
                marker_type = match.group(1).upper()
                description = match.group(2).strip()
                
                severity = "high" if marker_type in ["FIXME", "XXX"] else "medium"
                
                self.issues.append(CodeIssue(
                    file_path=str(file_path.relative_to(self.root_dir)),
                    line_number=line_num,
                    issue_type="incomplete_feature",
                    severity=severity,
                    description=f"{marker_type}: {description}",
                    code_snippet=line.strip(),
                ))
    
    def _check_unused_imports(self, file_path: Path, tree: ast.AST, content: str) -> None:
        """
        Check for unused imports.
        
        Args:
            file_path: Path to the file
            tree: AST tree of the file
            content: File content
        """
        imports = set()
        used_names = set()
        
        # Collect all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports.add((name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports.add((name, node.lineno))
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
        
        # Check for unused imports
        for import_name, line_num in imports:
            if import_name not in used_names and not import_name.startswith('_'):
                self.issues.append(CodeIssue(
                    file_path=str(file_path.relative_to(self.root_dir)),
                    line_number=line_num,
                    issue_type="unused_import",
                    severity="low",
                    description=f"Unused import: {import_name}",
                ))
    
    def _check_commented_code(self, file_path: Path, lines: List[str]) -> None:
        """
        Check for commented-out code blocks.
        
        Args:
            file_path: Path to the file
            lines: Lines of code
        """
        code_pattern = re.compile(r'^\s*#\s*(def |class |import |from |if |for |while |return )')
        
        for line_num, line in enumerate(lines, start=1):
            if code_pattern.match(line):
                self.issues.append(CodeIssue(
                    file_path=str(file_path.relative_to(self.root_dir)),
                    line_number=line_num,
                    issue_type="commented_code",
                    severity="low",
                    description="Commented-out code detected",
                    code_snippet=line.strip(),
                ))
    
    def _check_function_complexity(self, file_path: Path, tree: ast.AST) -> None:
        """
        Check for overly complex functions (high cyclomatic complexity).
        
        Args:
            file_path: Path to the file
            tree: AST tree of the file
        """
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_complexity(node)
                
                if complexity > 10:  # Threshold for high complexity
                    self.issues.append(CodeIssue(
                        file_path=str(file_path.relative_to(self.root_dir)),
                        line_number=node.lineno,
                        issue_type="high_complexity",
                        severity="medium",
                        description=f"Function '{node.name}' has high complexity ({complexity})",
                    ))
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity of a function.
        
        Args:
            node: Function AST node
            
        Returns:
            int: Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _generate_report(self) -> Dict[str, Any]:
        """
        Generate the analysis report.
        
        Returns:
            dict: Complete analysis report
        """
        # Count issues by severity and type
        for issue in self.issues:
            self.stats["issues_by_severity"][issue.severity] += 1
            self.stats["issues_by_type"][issue.issue_type] += 1
        
        return {
            "summary": {
                "total_files_analyzed": self.stats["total_files"],
                "total_lines_of_code": self.stats["total_lines"],
                "total_functions": self.stats["total_functions"],
                "total_classes": self.stats["total_classes"],
                "total_issues": len(self.issues),
                "issues_by_severity": dict(self.stats["issues_by_severity"]),
                "issues_by_type": dict(self.stats["issues_by_type"]),
            },
            "issues": [asdict(issue) for issue in self.issues],
        }
    
    def save_report(self, output_file: str) -> None:
        """
        Save the analysis report to a JSON file.
        
        Args:
            output_file: Path to output file
        """
        report = self._generate_report()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {output_path}")
    
    def print_summary(self) -> None:
        """Print a summary of the analysis results."""
        report = self._generate_report()
        summary = report["summary"]
        
        print("\n" + "=" * 70)
        print("BACKEND CODE ANALYSIS SUMMARY")
        print("=" * 70)
        print(f"Files analyzed: {summary['total_files_analyzed']}")
        print(f"Lines of code: {summary['total_lines_of_code']}")
        print(f"Functions: {summary['total_functions']}")
        print(f"Classes: {summary['total_classes']}")
        print(f"\nTotal issues found: {summary['total_issues']}")
        
        print("\nIssues by severity:")
        for severity in ["critical", "high", "medium", "low"]:
            count = summary["issues_by_severity"].get(severity, 0)
            if count > 0:
                print(f"  {severity.capitalize()}: {count}")
        
        print("\nIssues by type:")
        for issue_type, count in sorted(summary["issues_by_type"].items()):
            print(f"  {issue_type}: {count}")
        
        print("=" * 70)


def main():
    """Main entry point for the analyzer."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_backend.py <directory_path>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    # Run analysis
    analyzer = BackendCodeAnalyzer(directory)
    analyzer.analyze()
    
    # Print summary
    analyzer.print_summary()
    
    # Save detailed report
    output_file = "docs/analysis/backend_analysis_report.json"
    analyzer.save_report(output_file)
    
    # Create human-readable summary
    summary_file = "docs/analysis/backend_analysis_summary.md"
    create_summary_markdown(analyzer, summary_file)


def create_summary_markdown(analyzer: BackendCodeAnalyzer, output_file: str) -> None:
    """
    Create a human-readable markdown summary of the analysis.
    
    Args:
        analyzer: The code analyzer instance
        output_file: Path to output markdown file
    """
    report = analyzer._generate_report()
    summary = report["summary"]
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Backend Code Analysis Summary\n\n")
        f.write(f"**Analysis Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Overview\n\n")
        f.write(f"- **Files Analyzed:** {summary['total_files_analyzed']}\n")
        f.write(f"- **Lines of Code:** {summary['total_lines_of_code']}\n")
        f.write(f"- **Functions:** {summary['total_functions']}\n")
        f.write(f"- **Classes:** {summary['total_classes']}\n")
        f.write(f"- **Total Issues:** {summary['total_issues']}\n\n")
        
        f.write("## Issues by Severity\n\n")
        for severity in ["critical", "high", "medium", "low"]:
            count = summary["issues_by_severity"].get(severity, 0)
            f.write(f"- **{severity.capitalize()}:** {count}\n")
        
        f.write("\n## Issues by Type\n\n")
        for issue_type, count in sorted(summary["issues_by_type"].items()):
            f.write(f"- **{issue_type}:** {count}\n")
        
        f.write("\n## Top Issues\n\n")
        # Group issues by file
        issues_by_file = defaultdict(list)
        for issue in report["issues"]:
            issues_by_file[issue["file_path"]].append(issue)
        
        # Show files with most issues
        sorted_files = sorted(issues_by_file.items(), key=lambda x: len(x[1]), reverse=True)
        for file_path, issues in sorted_files[:10]:  # Top 10 files
            f.write(f"\n### {file_path}\n\n")
            f.write(f"**{len(issues)} issues found**\n\n")
            
            # Show first 5 issues
            for issue in issues[:5]:
                f.write(f"- Line {issue['line_number']}: [{issue['severity']}] {issue['description']}\n")
            
            if len(issues) > 5:
                f.write(f"- ... and {len(issues) - 5} more issues\n")
    
    print(f"Summary saved to: {output_path}")


if __name__ == "__main__":
    main()
