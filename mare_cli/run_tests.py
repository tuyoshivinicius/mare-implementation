#!/usr/bin/env python3
"""
MARE CLI - Test Runner
Comprehensive test suite for MARE CLI
"""

import unittest
import sys
import os
from pathlib import Path
import argparse
import coverage

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_unit_tests(verbose=False):
    """Run unit tests."""
    print("🧪 Running Unit Tests...")
    
    # Discover and run unit tests
    loader = unittest.TestLoader()
    start_dir = project_root / "tests" / "unit"
    suite = loader.discover(str(start_dir), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stdout
    )
    
    result = runner.run(suite)
    return result.wasSuccessful()


def run_integration_tests(verbose=False):
    """Run integration tests."""
    print("🔗 Running Integration Tests...")
    
    # Discover and run integration tests
    loader = unittest.TestLoader()
    start_dir = project_root / "tests" / "integration"
    suite = loader.discover(str(start_dir), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stdout
    )
    
    result = runner.run(suite)
    return result.wasSuccessful()


def run_cli_tests(verbose=False):
    """Run CLI command tests."""
    print("💻 Running CLI Tests...")
    
    import subprocess
    import tempfile
    from pathlib import Path
    
    success = True
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Test CLI help
        result = subprocess.run(
            ["mare", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ CLI help test failed: {result.stderr}")
            success = False
        else:
            print("✅ CLI help test passed")
        
        # Test CLI version
        result = subprocess.run(
            ["mare", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ CLI version test failed: {result.stderr}")
            success = False
        else:
            print("✅ CLI version test passed")
        
        # Test init command
        project_name = "test_cli_project"
        result = subprocess.run(
            ["mare", "init", project_name, "--template", "basic", "--llm-provider", "openai"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ CLI init test failed: {result.stderr}")
            success = False
        else:
            project_path = temp_dir / project_name
            if project_path.exists():
                print("✅ CLI init test passed")
            else:
                print("❌ CLI init test failed: project not created")
                success = False
        
        # Test status command
        if success:
            result = subprocess.run(
                ["mare", "status"],
                cwd=str(temp_dir / project_name),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"❌ CLI status test failed: {result.stderr}")
                success = False
            else:
                print("✅ CLI status test passed")
    
    except subprocess.TimeoutExpired:
        print("❌ CLI tests timed out")
        success = False
    except Exception as e:
        print(f"❌ CLI tests failed with exception: {e}")
        success = False
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return success


def run_performance_tests(verbose=False):
    """Run performance tests."""
    print("⚡ Running Performance Tests...")
    
    import time
    from mare.workspace import SharedWorkspace
    import tempfile
    
    success = True
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Test workspace performance
        workspace = SharedWorkspace(temp_dir / "perf_workspace", "perf-test")
        
        # Measure artifact storage performance
        start_time = time.time()
        
        for i in range(100):
            workspace.store_user_stories(
                f"User story {i}: Test performance",
                "stakeholder"
            )
        
        storage_time = time.time() - start_time
        
        if storage_time > 5.0:  # Should store 100 artifacts in under 5 seconds
            print(f"❌ Workspace storage performance test failed: {storage_time:.2f}s")
            success = False
        else:
            print(f"✅ Workspace storage performance test passed: {storage_time:.2f}s")
        
        # Measure retrieval performance
        start_time = time.time()
        
        for i in range(100):
            workspace.get_user_stories()
        
        retrieval_time = time.time() - start_time
        
        if retrieval_time > 2.0:  # Should retrieve 100 times in under 2 seconds
            print(f"❌ Workspace retrieval performance test failed: {retrieval_time:.2f}s")
            success = False
        else:
            print(f"✅ Workspace retrieval performance test passed: {retrieval_time:.2f}s")
        
        # Test workspace stats
        start_time = time.time()
        stats = workspace.get_workspace_stats()
        stats_time = time.time() - start_time
        
        if stats_time > 1.0:  # Should get stats in under 1 second
            print(f"❌ Workspace stats performance test failed: {stats_time:.2f}s")
            success = False
        else:
            print(f"✅ Workspace stats performance test passed: {stats_time:.2f}s")
        
        print(f"📊 Performance Summary:")
        print(f"   - Storage: {storage_time:.2f}s for 100 artifacts")
        print(f"   - Retrieval: {retrieval_time:.2f}s for 100 queries")
        print(f"   - Stats: {stats_time:.2f}s")
        print(f"   - Total artifacts: {stats['total_artifacts']}")
    
    except Exception as e:
        print(f"❌ Performance tests failed with exception: {e}")
        success = False
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return success


def generate_coverage_report():
    """Generate test coverage report."""
    print("📊 Generating Coverage Report...")
    
    try:
        # Initialize coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Run tests with coverage
        success = True
        success &= run_unit_tests(verbose=False)
        success &= run_integration_tests(verbose=False)
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\n📈 Coverage Report:")
        cov.report(show_missing=True)
        
        # Generate HTML report
        html_dir = project_root / "coverage_html"
        cov.html_report(directory=str(html_dir))
        print(f"📄 HTML coverage report generated: {html_dir}/index.html")
        
        return success
    
    except ImportError:
        print("⚠️  Coverage package not available. Install with: pip install coverage")
        return True
    except Exception as e:
        print(f"❌ Coverage report generation failed: {e}")
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="MARE CLI Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--cli", action="store_true", help="Run CLI tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if not any([args.unit, args.integration, args.cli, args.performance, args.coverage, args.all]):
        args.all = True
    
    print("🚀 MARE CLI Test Suite")
    print("=" * 50)
    
    success = True
    
    if args.coverage:
        success &= generate_coverage_report()
    elif args.all:
        success &= run_unit_tests(args.verbose)
        success &= run_integration_tests(args.verbose)
        success &= run_cli_tests(args.verbose)
        success &= run_performance_tests(args.verbose)
    else:
        if args.unit:
            success &= run_unit_tests(args.verbose)
        
        if args.integration:
            success &= run_integration_tests(args.verbose)
        
        if args.cli:
            success &= run_cli_tests(args.verbose)
        
        if args.performance:
            success &= run_performance_tests(args.verbose)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

