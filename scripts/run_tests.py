#!/usr/bin/env python3
"""
Test runner script for i18n-backend with various reporting options.

Usage:
    python scripts/run_tests.py                    # Run all tests
    python scripts/run_tests.py --unit             # Run unit tests only
    python scripts/run_tests.py --coverage         # Run with coverage report
    python scripts/run_tests.py --watch            # Run in watch mode
    python scripts/run_tests.py --rbac             # Run RBAC tests only
    python scripts/run_tests.py --atomic           # Run atomic workflow tests
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Execute a shell command and handle errors."""
    if description:
        print(f"\n{'=' * 70}")
        print(f"  {description}")
        print(f"{'=' * 70}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Test runner for i18n-backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py                  # Run all tests with basic output
  python scripts/run_tests.py --coverage       # Run all tests with coverage report
  python scripts/run_tests.py --unit           # Run unit tests only
  python scripts/run_tests.py --integration    # Run integration tests only
  python scripts/run_tests.py --rbac -v        # Run RBAC tests with verbose output
  python scripts/run_tests.py --specific test_message_workflow  # Run specific test file
        """
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report (requires pytest-cov)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only",
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only",
    )
    parser.add_argument(
        "--rbac",
        action="store_true",
        help="Run RBAC tests only",
    )
    parser.add_argument(
        "--atomic",
        action="store_true",
        help="Run atomic workflow tests only",
    )
    parser.add_argument(
        "--specific",
        type=str,
        help="Run specific test file (e.g., test_message_workflow)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run in watch mode (requires pytest-watch)",
    )
    parser.add_argument(
        "--failed-first",
        action="store_true",
        help="Run failed tests first",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report (requires pytest-html)",
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = "pytest"
    
    # Add verbosity
    if args.verbose:
        cmd += " -vv"
    else:
        cmd += " -v"
    
    # Add specific markers
    markers = []
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")
    if args.rbac:
        markers.append("rbac")
    if args.atomic:
        markers.append("atomic")
    
    if markers:
        marker_expr = " or ".join(markers)
        cmd += f" -m '{marker_expr}'"
    
    # Add specific test file
    if args.specific:
        cmd += f" tests/{args.specific}.py"
    else:
        cmd += " tests/"
    
    # Add coverage
    if args.coverage:
        cmd += " --cov=src --cov-report=html --cov-report=term-missing"
    
    # Add failed first
    if args.failed_first:
        cmd += " --ff"
    
    # Add HTML report
    if args.html:
        cmd += " --html=reports/report.html --self-contained-html"
    
    # Run in watch mode
    if args.watch:
        cmd = f"ptw {' '.join(sys.argv[1:])}".replace("--watch", "")
    
    # Add colors and show output
    cmd += " --tb=short --color=yes"
    
    description = "Running i18n-backend Tests"
    if args.specific:
        description += f" - {args.specific}"
    if args.rbac:
        description += " - RBAC Tests"
    if args.atomic:
        description += " - Atomic Workflow Tests"
    if args.coverage:
        description += " (with Coverage)"
    
    exit_code = run_command(cmd, description)
    
    # Summary
    print(f"\n{'=' * 70}")
    if exit_code == 0:
        print("  ✓ All tests passed!")
    else:
        print("  ✗ Some tests failed. See details above.")
    print(f"{'=' * 70}\n")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
