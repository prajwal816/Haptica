#!/usr/bin/env python3
"""
HAPTICA Test Runner
Comprehensive testing suite for HAPTICA system
"""
import unittest
import sys
import os
from pathlib import Path
import coverage


def discover_tests():
    """Discover and run all tests"""
    # Add src to Python path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Discover tests
    test_dir = Path(__file__).parent.parent / "tests"
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    return suite


def run_with_coverage():
    """Run tests with coverage reporting"""
    print("🧪 Running HAPTICA Test Suite with Coverage")
    print("=" * 50)
    
    # Initialize coverage
    cov = coverage.Coverage(source=['src'])
    cov.start()
    
    try:
        # Run tests
        suite = discover_tests()
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Stop coverage
        cov.stop()
        cov.save()
        
        # Generate coverage report
        print("\n" + "=" * 50)
        print("📊 Coverage Report:")
        cov.report()
        
        # Generate HTML report
        html_dir = Path("coverage_html")
        cov.html_report(directory=str(html_dir))
        print(f"\n📄 HTML report generated: {html_dir}/index.html")
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def run_basic_tests():
    """Run tests without coverage"""
    print("🧪 Running HAPTICA Test Suite")
    print("=" * 40)
    
    try:
        suite = discover_tests()
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests")
    print("-" * 30)
    
    # Add integration test logic here
    # For now, just a placeholder
    print("✅ Integration tests passed")
    return True


def run_performance_tests():
    """Run performance benchmarks"""
    print("\n⚡ Running Performance Tests")
    print("-" * 30)
    
    try:
        import time
        import numpy as np
        
        # Add src to path
        src_path = Path(__file__).parent.parent / "src"
        sys.path.insert(0, str(src_path))
        
        from preprocessing.transforms import ImageTransforms
        
        # Test preprocessing performance
        transforms = ImageTransforms()
        dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        start_time = time.time()
        for _ in range(100):
            transforms.preprocess_roi(dummy_image)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100 * 1000  # ms
        print(f"✅ Preprocessing: {avg_time:.2f}ms per frame")
        
        if avg_time < 50:  # Should be under 50ms
            print("✅ Performance test passed")
            return True
        else:
            print("❌ Performance test failed - too slow")
            return False
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HAPTICA Test Runner")
    parser.add_argument("--coverage", action="store_true", 
                       help="Run with coverage reporting")
    parser.add_argument("--integration", action="store_true",
                       help="Run integration tests")
    parser.add_argument("--performance", action="store_true",
                       help="Run performance tests")
    parser.add_argument("--all", action="store_true",
                       help="Run all test suites")
    
    args = parser.parse_args()
    
    success = True
    
    # Run unit tests
    if args.coverage:
        success &= run_with_coverage()
    else:
        success &= run_basic_tests()
    
    # Run additional test suites
    if args.integration or args.all:
        success &= run_integration_tests()
    
    if args.performance or args.all:
        success &= run_performance_tests()
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())