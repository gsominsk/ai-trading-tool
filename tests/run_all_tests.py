"""
AI Trading System - Universal Test Runner

Comprehensive test runner for the entire AI Trading System project.
Executes all test suites in logical order with detailed reporting,
coverage analysis, and categorized results.

Test Categories:
1. Unit Tests - Core MarketDataService functionality
2. Error Architecture Tests - Exception handling and recovery
3. Integration Tests - Component interaction testing
4. Edge Case Tests - Extreme scenarios and boundary conditions
5. Manual Tests - Human-verified functionality tests

Usage:
    python tests/run_all_tests.py                    # Run all tests
    python tests/run_all_tests.py --verbose          # Verbose output
    python tests/run_all_tests.py --coverage         # Include coverage
    python tests/run_all_tests.py --category unit    # Run specific category
    python tests/run_all_tests.py --fast             # Skip slow tests
    python tests/run_all_tests.py --list             # List all tests
"""

import sys
import subprocess
import argparse
from pathlib import Path
import time
from datetime import datetime
import glob
import os

class AITradingTestRunner:
    """Universal test runner for AI Trading System."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_categories = {
            'unit': {
                'description': 'Core unit tests across all components',
                'tests': [
                    'tests/unit/test_market_data_service.py',
                    'tests/unit/error_architecture/test_error_exceptions.py',
                    'tests/unit/logging/test_core_logging.py',
                    'tests/unit/logging/test_logging_components.py',
                    'tests/unit/logging/test_http_filter.py',
                    'tests/unit/logging/test_operation_context.py',
                    'tests/unit/logging/test_trace_id_integration.py',
                    'tests/unit/logging/test_trace_id_uniqueness.py',
                    'tests/unit/logging/test_raw_data_logging.py',
                    'tests/unit/logging/test_trace_id_demo.py',
                    'tests/unit/market_data/test_market_data_core.py',
                    'tests/unit/market_data/test_market_data_api.py',
                    'tests/unit/market_data/test_market_data_edge_cases.py',
                ]
            },
            'integration': {
                'description': 'Integration tests across system components',
                'tests': [
                    'tests/integration/error_architecture/test_error_integration.py',
                    'tests/integration/logging/test_logging_integration.py',
                    'tests/integration/logging/test_logging_production.py',
                    'tests/integration/logging/test_trace_architecture_integration.py',
                    'tests/integration/market_data/test_market_data_integration.py',
                    'tests/integration/system/test_backward_compatibility.py',
                    'tests/integration/system/test_comprehensive_integration.py',
                ]
            }
        }
    
    def discover_tests(self):
        """Discover all test files in the tests directory."""
        test_files = []
        
        # Discover Python test files
        for pattern in ['test_*.py', '*_test.py']:
            test_files.extend(glob.glob(f"tests/{pattern}"))
            test_files.extend(glob.glob(f"tests/**/{pattern}", recursive=True))
        
        # Filter out runner files
        test_files = [f for f in test_files if not f.endswith('run_all_tests.py') 
                     and not f.endswith('run_error_architecture_tests.py')]
        
        return sorted(test_files)
    
    def list_tests(self):
        """List all available tests by category."""
        print("🧪 AI Trading System - Available Tests")
        print("=" * 60)
        
        for category, info in self.test_categories.items():
            print(f"\n📋 {category.upper().replace('_', ' ')}:")
            print(f"   {info['description']}")
            
            available_tests = []
            for test_file in info['tests']:
                if os.path.exists(test_file):
                    available_tests.append(test_file)
            
            if available_tests:
                for test in available_tests:
                    print(f"   ✅ {test}")
            else:
                print(f"   ⚠️  No tests found in this category")
        
        # Show any tests not categorized
        all_categorized = set()
        for info in self.test_categories.values():
            all_categorized.update(info['tests'])
        
        discovered = set(self.discover_tests())
        uncategorized = discovered - all_categorized
        
        if uncategorized:
            print(f"\n📋 UNCATEGORIZED TESTS:")
            for test in sorted(uncategorized):
                print(f"   ❓ {test}")
    
    def run_test_file(self, test_file, verbose=False):
        """Run a specific test file and return results."""
        print(f"\n{'='*60}")
        print(f"Running: {test_file}")
        print(f"{'='*60}")
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            return {
                'file': test_file,
                'success': False,
                'duration': 0,
                'error': 'File not found'
            }
        
        cmd = ["python3", "-m", "pytest", str(test_file)]
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        cmd.extend(["--tb=short", "--no-header"])
        
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"Exit code: {result.returncode}")
            print(f"Duration: {duration:.2f}s")
            
            if result.stdout:
                print("\nSTDOUT:")
                print(result.stdout)
            
            if result.stderr:
                print("\nSTDERR:")
                print(result.stderr)
            
            return {
                'file': test_file,
                'success': result.returncode == 0,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            print(f"Error running test: {e}")
            return {
                'file': test_file,
                'success': False,
                'duration': 0,
                'error': str(e)
            }
    
    def run_category(self, category, verbose=False, fast=False):
        """Run all tests in a specific category."""
        if category not in self.test_categories:
            print(f"❌ Unknown category: {category}")
            print(f"Available categories: {', '.join(self.test_categories.keys())}")
            return []
        
        info = self.test_categories[category]
        print(f"\n🧪 Running {category.upper().replace('_', ' ')} Tests")
        print(f"📋 {info['description']}")
        
        # Skip comprehensive tests in fast mode
        if fast and category == 'comprehensive_validation':
            print("⏩ Skipping comprehensive validation tests in fast mode")
            return []
        
        results = []
        for test_file in info['tests']:
            if os.path.exists(test_file):
                result = self.run_test_file(test_file, verbose)
                results.append(result)
            else:
                print(f"⚠️  Skipping missing test: {test_file}")
        
        return results
    
    def run_coverage_analysis(self, test_files=None):
        """Run comprehensive coverage analysis."""
        print(f"\n{'='*60}")
        print("Running Comprehensive Coverage Analysis")
        print(f"{'='*60}")
        
        if test_files is None:
            # Use all existing test files
            test_files = [f for f in self.discover_tests() if os.path.exists(f)]
        
        cmd = ["python3", "-m", "pytest"] + test_files + [
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--no-header"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            print(f"Coverage exit code: {result.returncode}")
            
            if result.stdout:
                print("\nCoverage Report:")
                print(result.stdout)
            
            if result.stderr:
                print("\nCoverage Errors:")
                print(result.stderr)
                
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error running coverage: {e}")
            return False
    
    def print_summary(self, all_results):
        """Print comprehensive summary of all test results."""
        print(f"\n{'='*60}")
        print("🧪 AI TRADING SYSTEM - COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Overall statistics
        total_tests = sum(len(results) for results in all_results.values())
        successful_tests = sum(sum(1 for r in results if r['success']) for results in all_results.values())
        failed_tests = total_tests - successful_tests
        total_duration = sum(sum(r['duration'] for r in results) for results in all_results.values())
        
        print(f"\n📊 Overall Results:")
        print(f"  Total test files: {total_tests}")
        print(f"  Successful: {successful_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Total duration: {total_duration:.2f}s")
        
        # Category breakdown
        print(f"\n📋 Results by Category:")
        for category, results in all_results.items():
            if results:
                category_success = sum(1 for r in results if r['success'])
                category_total = len(results)
                status = "✅" if category_success == category_total else "❌"
                print(f"  {status} {category.replace('_', ' ').title()}: {category_success}/{category_total}")
        
        # Detailed results
        print(f"\n📄 Detailed Results:")
        for category, results in all_results.items():
            if results:
                print(f"\n  {category.replace('_', ' ').title()}:")
                for result in results:
                    status = "✅ PASS" if result['success'] else "❌ FAIL"
                    duration = f"{result['duration']:.2f}s"
                    test_name = os.path.basename(result['file'])
                    print(f"    {status} {test_name} ({duration})")
        
        # Final assessment
        if failed_tests > 0:
            print(f"\n⚠️  {failed_tests} test file(s) failed across {len([c for c, r in all_results.items() if any(not res['success'] for res in r)])} categories.")
            print("Check output above for details.")
            return False
        else:
            print(f"\n🎉 All test files passed successfully across all categories!")
            print("\n🚀 AI Trading System is ready for production deployment!")
            return True
    
    def run_all(self, verbose=False, coverage=False, fast=False, categories=None):
        """Run all tests or specific categories."""
        print("🧪 AI TRADING SYSTEM - UNIVERSAL TEST RUNNER")
        print("=" * 60)
        print("Comprehensive testing across all system components")
        
        all_results = {}
        
        # Determine which categories to run
        categories_to_run = categories if categories else list(self.test_categories.keys())
        
        # Run each category
        for category in categories_to_run:
            if category in self.test_categories:
                results = self.run_category(category, verbose, fast)
                if results:  # Only include categories that had tests
                    all_results[category] = results
            else:
                print(f"⚠️  Unknown category: {category}")
        
        # Run coverage analysis if requested
        if coverage and all_results:
            all_test_files = []
            for results in all_results.values():
                all_test_files.extend([r['file'] for r in results])
            
            coverage_success = self.run_coverage_analysis(all_test_files)
            if not coverage_success:
                print("\n⚠️  Coverage analysis encountered issues.")
        
        # Print final summary
        if all_results:
            success = self.print_summary(all_results)
            return success
        else:
            print("\n⚠️  No tests were executed.")
            return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="AI Trading System Universal Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Run tests in verbose mode")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run coverage analysis")
    parser.add_argument("--fast", "-f", action="store_true", help="Skip slow tests (manual tests)")
    parser.add_argument("--category", action="append", help="Run specific test category (can be used multiple times)")
    parser.add_argument("--list", "-l", action="store_true", help="List all available tests by category")
    
    args = parser.parse_args()
    
    runner = AITradingTestRunner()
    
    if args.list:
        runner.list_tests()
        return
    
    success = runner.run_all(
        verbose=args.verbose,
        coverage=args.coverage,
        fast=args.fast,
        categories=args.category
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()