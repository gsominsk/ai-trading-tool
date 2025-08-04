"""
Error Architecture Phase 3 - Comprehensive Test Runner

Executes all error architecture test suites to verify the complete implementation
of Phase 3 testing requirements. Provides detailed reporting on test coverage
and results across all components.

Test Suites:
1. Integration tests for MarketDataService error handling
2. Error recovery and fallback tests
3. Backward compatibility tests
4. Error context and logging preparation tests
5. Exception hierarchy compatibility tests (existing)

Usage:
    python tests/run_error_architecture_tests.py
    python tests/run_error_architecture_tests.py --verbose
    python tests/run_error_architecture_tests.py --coverage
"""

import sys
import subprocess
import argparse
from pathlib import Path
import time
from datetime import datetime

def run_test_suite(test_file, verbose=False):
    """Run a specific test suite and return results."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print(f"{'='*60}")
    
    cmd = ["python", "-m", "pytest", str(test_file)]
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    cmd.extend(["--tb=short", "--no-header"])
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
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

def run_coverage_analysis():
    """Run coverage analysis across all test files."""
    print(f"\n{'='*60}")
    print("Running Coverage Analysis")
    print(f"{'='*60}")
    
    test_files = [
        "tests/test_error_architecture_integration.py",
        "tests/test_error_recovery_fallbacks.py", 
        "tests/test_backward_compatibility.py",
        "tests/test_error_context_logging.py",
        "tests/test_exception_hierarchy_compatibility.py"
    ]
    
    cmd = ["python", "-m", "pytest"] + test_files + [
        "--cov=src/market_data",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--no-header"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
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

def print_summary(results):
    """Print a summary of all test results."""
    print(f"\n{'='*60}")
    print("ERROR ARCHITECTURE PHASE 3 - TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests
    total_duration = sum(r['duration'] for r in results)
    
    print(f"\nOverall Results:")
    print(f"  Total test suites: {total_tests}")
    print(f"  Successful: {successful_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Total duration: {total_duration:.2f}s")
    
    print(f"\nDetailed Results:")
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        duration = f"{result['duration']:.2f}s"
        print(f"  {status} {result['file']} ({duration})")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test suite(s) failed. Check output above for details.")
        return False
    else:
        print(f"\n🎉 All test suites passed successfully!")
        return True

def print_test_coverage_overview():
    """Print an overview of what each test suite covers."""
    print(f"\n{'='*60}")
    print("TEST COVERAGE OVERVIEW")
    print(f"{'='*60}")
    
    coverage_info = {
        "test_error_architecture_integration.py": [
            "SymbolValidationError integration with MarketDataService",
            "NetworkError handling with API timeouts and connection failures", 
            "ProcessingError graceful degradation scenarios",
            "ErrorContext and trace ID functionality across operations",
            "Logging integration points verification"
        ],
        "test_error_recovery_fallbacks.py": [
            "Fail-fast vs recovery strategy configuration and behavior",
            "Graceful degradation for non-critical operations",
            "Configurable error handling (enable_logging, fail_fast parameters)",
            "Recovery mechanisms for BTC correlation, volume profile, technical indicators",
            "Fallback chain integration testing"
        ],
        "test_backward_compatibility.py": [
            "ValidationError inheritance from ValueError (backward compatibility)",
            "Existing exception catching patterns still work",
            "MarketDataService constructor backward compatibility", 
            "No breaking changes to existing public API",
            "Legacy error handling patterns continue to function"
        ],
        "test_error_context_logging.py": [
            "Trace ID generation and propagation across operations",
            "Error context preservation across multiple operation calls",
            "Logging hooks functionality without actual logging implementation",
            "Operation metrics tracking for future logging integration",
            "ErrorContext serialization and system information collection"
        ],
        "test_exception_hierarchy_compatibility.py": [
            "Exception hierarchy structure and inheritance",
            "Multiple inheritance compatibility (MarketDataError + ValueError)",
            "Exception instantiation and string representation",
            "Context propagation through exception chain"
        ]
    }
    
    for test_file, features in coverage_info.items():
        print(f"\n📋 {test_file}:")
        for feature in features:
            print(f"   • {feature}")

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Error Architecture Phase 3 test suites")
    parser.add_argument("--verbose", "-v", action="store_true", help="Run tests in verbose mode")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run coverage analysis")
    parser.add_argument("--summary-only", "-s", action="store_true", help="Show only summary and coverage overview")
    
    args = parser.parse_args()
    
    print("🧪 ERROR ARCHITECTURE PHASE 3 - TESTING SUITE")
    print("="*60)
    print("Comprehensive testing of the integrated error architecture")
    print("with structured exception hierarchy, error recovery, and logging preparation.")
    
    if args.summary_only:
        print_test_coverage_overview()
        return
    
    # Define test suites in execution order
    test_suites = [
        "tests/test_exception_hierarchy_compatibility.py",  # Foundation tests first
        "tests/test_error_architecture_integration.py",     # Core integration tests
        "tests/test_backward_compatibility.py",             # Compatibility verification
        "tests/test_error_recovery_fallbacks.py",          # Recovery mechanisms
        "tests/test_error_context_logging.py"              # Context and logging preparation
    ]
    
    print_test_coverage_overview()
    
    # Run each test suite
    results = []
    for test_file in test_suites:
        result = run_test_suite(test_file, verbose=args.verbose)
        results.append(result)
    
    # Run coverage analysis if requested
    if args.coverage:
        coverage_success = run_coverage_analysis()
        if not coverage_success:
            print("\n⚠️  Coverage analysis encountered issues.")
    
    # Print final summary
    success = print_summary(results)
    
    if success:
        print(f"\n🎯 ERROR ARCHITECTURE PHASE 3 - TESTING COMPLETE")
        print("All test suites passed. The error architecture is ready for production use.")
        print("\nNext steps:")
        print("  • Integration with logging system (Tasks 24-36)")
        print("  • Performance testing under load")
        print("  • Production deployment preparation")
    else:
        print(f"\n❌ ERROR ARCHITECTURE PHASE 3 - TESTING FAILED")
        print("Some test suites failed. Please review and fix issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()