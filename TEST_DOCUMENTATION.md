# CineChainLanka Phase 1 Test Documentation

## Overview

This document provides comprehensive information about the test suite for CineChainLanka Phase 1. The test suite covers all core functionality including user management, KYC integration, campaign management, and payment processing.

## Test Structure

### 1. Users App Tests (`users/tests.py`)

#### Test Classes:
- **UserModelTest**: Tests for User model functionality
- **UserViewsTest**: Tests for user API endpoints
- **UserAuthenticationTest**: Tests for JWT authentication
- **UserPermissionsTest**: Tests for user role permissions
- **UserIntegrationTest**: End-to-end user workflow tests
- **UserValidationTest**: Data validation tests

#### Test Coverage:
- ✅ User registration and authentication
- ✅ Profile management and updates
- ✅ Password change and reset
- ✅ JWT token creation and validation
- ✅ User type permissions (creator, investor, admin)
- ✅ Data validation and error handling

#### Key Test Cases:
```python
# User registration
def test_user_registration(self):
    # Tests complete user registration flow

# JWT authentication
def test_jwt_token_creation(self):
    # Tests JWT token generation and validation

# Profile management
def test_user_profile_update(self):
    # Tests profile update functionality
```

### 2. KYC App Tests (`kyc/tests.py`)

#### Test Classes:
- **KYCRequestModelTest**: Tests for KYC request models
- **KYCDocumentModelTest**: Tests for document upload models
- **KYCVerificationModelTest**: Tests for verification workflow
- **KYCViewsTest**: Tests for KYC API endpoints
- **KYCDocumentUploadTest**: Tests for document upload functionality
- **KYCVerificationWorkflowTest**: Tests for verification process
- **KYCIntegrationTest**: End-to-end KYC workflow tests
- **KYCValidationTest**: Data validation tests

#### Test Coverage:
- ✅ KYC request creation and management
- ✅ Document upload and storage
- ✅ Verification workflow (pending → submitted → approved/rejected)
- ✅ Multi-level verification (basic, enhanced, corporate)
- ✅ Document type validation
- ✅ Address and identity verification

#### Key Test Cases:
```python
# KYC request creation
def test_create_kyc_request(self):
    # Tests KYC request creation with all required fields

# Document upload
def test_document_upload(self):
    # Tests document upload functionality

# Verification workflow
def test_kyc_verification_approval(self):
    # Tests complete KYC approval process
```

### 3. Campaigns App Tests (`campaigns/tests.py`)

#### Test Classes:
- **CampaignCategoryModelTest**: Tests for campaign categories
- **CampaignModelTest**: Tests for campaign models
- **CampaignRewardModelTest**: Tests for campaign rewards
- **CampaignViewsTest**: Tests for campaign API endpoints
- **CampaignSearchAndFilterTest**: Tests for search and filtering
- **CampaignRewardViewsTest**: Tests for reward management
- **CampaignIntegrationTest**: End-to-end campaign workflow tests
- **CampaignValidationTest**: Data validation tests

#### Test Coverage:
- ✅ Campaign creation and management
- ✅ Campaign categories and organization
- ✅ Campaign rewards and incentives
- ✅ Search and filtering functionality
- ✅ Campaign status management (draft → active → funded)
- ✅ Funding goal tracking and progress

#### Key Test Cases:
```python
# Campaign creation
def test_create_campaign(self):
    # Tests campaign creation with all required fields

# Campaign workflow
def test_complete_campaign_workflow(self):
    # Tests complete campaign lifecycle

# Search and filtering
def test_campaign_search_by_title(self):
    # Tests campaign search functionality
```

### 4. Payments App Tests (`payments/tests.py`)

#### Test Classes:
- **PaymentMethodModelTest**: Tests for payment methods
- **TransactionModelTest**: Tests for transaction models
- **PaymentGatewayModelTest**: Tests for payment gateways
- **RefundModelTest**: Tests for refund functionality
- **PaymentViewsTest**: Tests for payment API endpoints
- **LocalPaymentIntegrationTest**: Tests for local payment methods
- **PaymentProcessingTest**: Tests for payment workflows
- **PaymentValidationTest**: Data validation tests
- **PaymentIntegrationTest**: End-to-end payment tests

#### Test Coverage:
- ✅ Payment method configuration (LankaQR, eZ Cash, FriMi)
- ✅ Transaction processing and management
- ✅ Payment gateway integration
- ✅ Refund processing workflow
- ✅ Local payment method integration
- ✅ Transaction status management
- ✅ Fee calculation and processing

#### Key Test Cases:
```python
# Payment initiation
def test_initiate_payment(self):
    # Tests payment initiation process

# Local payment integration
def test_lanka_qr_payment_integration(self):
    # Tests LankaQR payment method

# Payment workflow
def test_payment_processing_workflow(self):
    # Tests complete payment processing
```

## Running Tests

### 1. Using Django Test Runner

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test kyc
python manage.py test campaigns
python manage.py test payments

# Run specific test class
python manage.py test users.tests.UserModelTest

# Run specific test method
python manage.py test users.tests.UserModelTest.test_create_user
```

### 2. Using Custom Test Runner

```bash
# Run all Phase 1 tests
python run_tests.py

# Run specific test suite
python run_tests.py users.tests
```

### 3. Using Pytest (Recommended)

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run specific app tests
pytest users/
pytest kyc/
pytest campaigns/
pytest payments/

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test markers
pytest -m "user"
pytest -m "kyc"
pytest -m "campaign"
pytest -m "payment"
```

## Test Configuration

### 1. Test Settings (`cinechain_backend/test_settings.py`)

- Uses SQLite in-memory database for fast execution
- Disables password hashing for faster tests
- Uses console email backend
- Disables logging during tests
- Configures test-specific media and static directories

### 2. Pytest Configuration (`pytest.ini`)

- Configures Django settings
- Sets up test discovery patterns
- Configures coverage reporting
- Defines test markers for organization
- Sets up test paths and filtering

## Test Data and Fixtures

### 1. Sample Data Creation

The test suite includes sample data creation for testing:

```python
# Users
self.user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123',
    user_type='investor'
)

# Campaigns
self.campaign = Campaign.objects.create(
    creator=self.creator,
    title='Test Film Campaign',
    description='Test description',
    # ... other fields
)

# Payment Methods
self.payment_method = PaymentMethod.objects.create(
    name='LankaQR',
    payment_type='lanka_qr',
    # ... other fields
)
```

### 2. Test Utilities

- **APIClient**: For testing API endpoints
- **SimpleUploadedFile**: For testing file uploads
- **RefreshToken**: For JWT authentication testing
- **Client**: For testing Django views

## Test Coverage Goals

### 1. Code Coverage Targets

- **Models**: 100% coverage
- **Views**: 95% coverage
- **Serializers**: 95% coverage
- **Business Logic**: 90% coverage
- **Overall**: 85% minimum coverage

### 2. Test Types Distribution

- **Unit Tests**: 60% (model validation, business logic)
- **Integration Tests**: 30% (API workflows, database operations)
- **End-to-End Tests**: 10% (complete user journeys)

## Phase 1 Feature Verification

### 1. User Management & KYC ✅

- [x] User registration and authentication
- [x] Profile management
- [x] KYC request creation and submission
- [x] Document upload and verification
- [x] Multi-level verification workflow
- [x] Admin verification process

### 2. Campaign Management ✅

- [x] Campaign creation and editing
- [x] Campaign categorization and organization
- [x] Campaign rewards and incentives
- [x] Campaign status management
- [x] Search and filtering functionality
- [x] Campaign dashboard features

### 3. Payment Integration ✅

- [x] Local payment methods (LankaQR, eZ Cash, FriMi)
- [x] Transaction processing and management
- [x] Payment gateway integration
- [x] Refund processing workflow
- [x] Fee calculation and processing
- [x] Payment status tracking

### 4. Frontend & UI ✅

- [x] Responsive design implementation
- [x] Multi-language support (Sinhala, Tamil, English)
- [x] User dashboard interfaces
- [x] Campaign discovery and browsing
- [x] Admin panel functionality

## Test Results Interpretation

### 1. All Tests Pass ✅

If all tests pass, Phase 1 is working correctly and ready for:
- Production deployment
- Phase 2 development (Blockchain Integration)
- User acceptance testing

### 2. Some Tests Fail ⚠️

If some tests fail:
- Review failing test cases
- Identify root causes
- Fix implementation issues
- Re-run tests until all pass

### 3. Test Errors 💥

If tests encounter errors:
- Check test configuration
- Verify dependencies are installed
- Review test setup and teardown
- Ensure database connectivity

## Continuous Integration

### 1. Automated Testing

The test suite is designed for CI/CD integration:
- Fast execution (under 5 minutes)
- Comprehensive coverage reporting
- Clear pass/fail indicators
- Detailed error reporting

### 2. Test Automation

```yaml
# Example GitHub Actions workflow
- name: Run Phase 1 Tests
  run: |
    pip install -r requirements-test.txt
    python run_tests.py
```

## Troubleshooting

### 1. Common Issues

**Database Connection Errors**
- Ensure test database is configured
- Check database permissions
- Verify test settings are loaded

**Import Errors**
- Check Python path configuration
- Verify app is in INSTALLED_APPS
- Ensure all dependencies are installed

**Test Data Issues**
- Clear test database between runs
- Use unique test data identifiers
- Avoid hardcoded test data

### 2. Debug Mode

Enable debug mode for detailed test output:

```bash
# Django test runner with verbosity
python manage.py test -v 2

# Pytest with verbose output
pytest -v -s
```

## Next Steps

### 1. After Successful Testing

- Deploy Phase 1 to production
- Begin Phase 2 development (Blockchain Integration)
- Implement smart contracts
- Add wallet integration

### 2. Test Maintenance

- Update tests when features change
- Add tests for new functionality
- Maintain test coverage above 85%
- Regular test suite execution

## Support and Resources

### 1. Documentation

- Django Testing Documentation
- Pytest Documentation
- REST Framework Testing Guide

### 2. Community

- Django Community Forum
- Python Testing Community
- Blockchain Development Community

---

*This test documentation ensures comprehensive coverage of all Phase 1 features and provides clear guidance for testing, maintenance, and future development.*

