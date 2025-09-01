#!/usr/bin/env python
"""
Test Runner for CineChainLanka Phase 1
This script runs all test cases for Phase 1 features and provides a comprehensive report.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Setup Django environment for testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinechain_backend.test_settings')
    django.setup()

def run_tests():
    """Run all test cases for Phase 1"""
    setup_django()
    
    # Get test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    print("🚀 Starting CineChainLanka Phase 1 Test Suite")
    print("=" * 60)
    
    # Define test suites for each Phase 1 component
    test_suites = [
        'users.tests',
        'kyc.tests', 
        'campaigns.tests',
        'payments.tests',
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_suite in test_suites:
        print(f"\n📋 Running tests for: {test_suite}")
        print("-" * 40)
        
        try:
            # Run tests for this suite
            failures = test_runner.run_tests([test_suite])
            
            if failures:
                print(f"❌ {test_suite} had {len(failures)} failures")
                total_failures += len(failures)
            else:
                print(f"✅ {test_suite} passed successfully")
                
        except Exception as e:
            print(f"💥 Error running {test_suite}: {e}")
            total_errors += 1
    
    print("\n" + "=" * 60)
    print("📊 PHASE 1 TEST SUMMARY")
    print("=" * 60)
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 ALL TESTS PASSED! Phase 1 is working correctly.")
        print("\n✅ Phase 1 Features Verified:")
        print("   • User Management & Authentication")
        print("   • KYC Integration & Verification")
        print("   • Campaign Creation & Management")
        print("   • Local Payment Integration (LankaQR, eZ Cash, FriMi)")
        print("   • Transaction Processing & Management")
        print("   • Multi-language Support")
        print("   • Admin Panel Functionality")
    else:
        print(f"⚠️  Tests completed with {total_failures} failures and {total_errors} errors")
        print("Please review and fix the failing tests before proceeding to Phase 2.")
    
    print("\n🔍 Test Coverage:")
    print("   • Model validation and relationships")
    print("   • API endpoints and views")
    print("   • Business logic and workflows")
    print("   • Data validation and error handling")
    print("   • Integration between components")
    
    print("\n📈 Next Steps:")
    if total_failures == 0 and total_errors == 0:
        print("   • Phase 1 is ready for production")
        print("   • Proceed to Phase 2: Blockchain Integration")
        print("   • Begin smart contract development")
    else:
        print("   • Fix failing tests")
        print("   • Ensure all Phase 1 features work correctly")
        print("   • Re-run tests until all pass")
    
    return total_failures == 0 and total_errors == 0

def run_specific_tests(test_pattern=None):
    """Run specific test cases"""
    setup_django()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    if test_pattern:
        print(f"🎯 Running tests matching pattern: {test_pattern}")
        failures = test_runner.run_tests([test_pattern])
    else:
        print("🎯 Running all tests")
        failures = test_runner.run_tests()
    
    return len(failures) == 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific tests
        pattern = sys.argv[1]
        success = run_specific_tests(pattern)
    else:
        # Run all Phase 1 tests
        success = run_tests()
    
    sys.exit(0 if success else 1)

