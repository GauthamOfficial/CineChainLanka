from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User


class KYCRequest(models.Model):
    """
    KYC verification requests submitted by users
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('under_review', _('Under Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('requires_additional_info', _('Requires Additional Information')),
    ]
    
    VERIFICATION_LEVEL_CHOICES = [
        ('basic', _('Basic Verification')),
        ('enhanced', _('Enhanced Verification')),
        ('corporate', _('Corporate Verification')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='kyc_request'
    )
    
    verification_level = models.CharField(
        max_length=20,
        choices=VERIFICATION_LEVEL_CHOICES,
        default='basic',
        help_text=_('Level of KYC verification required')
    )
    
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Current status of KYC request')
    )
    
    # Personal information verification
    legal_name = models.CharField(
        max_length=255,
        help_text=_('Legal name as per official documents')
    )
    
    date_of_birth = models.DateField(
        help_text=_('Date of birth for verification')
    )
    
    nationality = models.CharField(
        max_length=100,
        help_text=_('Nationality of the user')
    )
    
    residential_address = models.TextField(
        help_text=_('Current residential address')
    )
    
    # Identity verification
    identity_document_type = models.CharField(
        max_length=50,
        choices=[
            ('national_id', _('National ID Card')),
            ('passport', _('Passport')),
            ('drivers_license', _('Driver\'s License')),
            ('birth_certificate', _('Birth Certificate')),
        ],
        help_text=_('Type of identity document provided')
    )
    
    identity_document_number = models.CharField(
        max_length=100,
        help_text=_('Identity document number')
    )
    
    identity_document_expiry = models.DateField(
        blank=True,
        null=True,
        help_text=_('Expiry date of identity document')
    )
    
    # Address verification
    address_proof_type = models.CharField(
        max_length=50,
        choices=[
            ('utility_bill', _('Utility Bill')),
            ('bank_statement', _('Bank Statement')),
            ('rental_agreement', _('Rental Agreement')),
            ('property_deed', _('Property Deed')),
            ('government_letter', _('Government Letter')),
        ],
        help_text=_('Type of address proof document')
    )
    
    address_proof_date = models.DateField(
        help_text=_('Date of address proof document')
    )
    
    # Financial information
    source_of_funds = models.CharField(
        max_length=100,
        choices=[
            ('employment', _('Employment Income')),
            ('business', _('Business Income')),
            ('investment', _('Investment Income')),
            ('inheritance', _('Inheritance')),
            ('gift', _('Gift')),
            ('other', _('Other')),
        ],
        help_text=_('Primary source of funds')
    )
    
    annual_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Annual income amount')
    )
    
    employment_status = models.CharField(
        max_length=50,
        choices=[
            ('employed', _('Employed')),
            ('self_employed', _('Self-Employed')),
            ('unemployed', _('Unemployed')),
            ('student', _('Student')),
            ('retired', _('Retired')),
        ],
        blank=True,
        help_text=_('Current employment status')
    )
    
    employer_name = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Name of employer or company')
    )
    
    # Additional information
    political_exposure = models.BooleanField(
        default=False,
        help_text=_('Whether user has political exposure')
    )
    
    politically_exposed_person = models.BooleanField(
        default=False,
        help_text=_('Whether user is a politically exposed person')
    )
    
    sanctions_check = models.BooleanField(
        default=False,
        help_text=_('Whether user passed sanctions screening')
    )
    
    # Review information
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When KYC was submitted')
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reviewed_kyc_requests',
        help_text=_('Admin who reviewed the KYC request')
    )
    
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When KYC was reviewed')
    )
    
    review_notes = models.TextField(
        blank=True,
        help_text=_('Notes from the review process')
    )
    
    rejection_reason = models.TextField(
        blank=True,
        help_text=_('Reason for rejection if applicable')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('KYC Request')
        verbose_name_plural = _('KYC Requests')
        db_table = 'kyc_requests'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['verification_level']),
            models.Index(fields=['submitted_at']),
        ]
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"KYC Request for {self.user.username} - {self.get_status_display()}"
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        return self.status == 'rejected'
    
    @property
    def is_pending(self):
        return self.status in ['pending', 'under_review']


class KYCVerification(models.Model):
    """
    Individual verification checks within a KYC request
    """
    VERIFICATION_TYPE_CHOICES = [
        ('identity', _('Identity Verification')),
        ('address', _('Address Verification')),
        ('financial', _('Financial Verification')),
        ('document', _('Document Verification')),
        ('sanctions', _('Sanctions Screening')),
        ('pep', _('PEP Screening')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('requires_review', _('Requires Review')),
    ]
    
    kyc_request = models.ForeignKey(
        KYCRequest,
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    
    verification_type = models.CharField(
        max_length=20,
        choices=VERIFICATION_TYPE_CHOICES,
        help_text=_('Type of verification')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Status of this verification')
    )
    
    # Verification details
    verification_method = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Method used for verification')
    )
    
    verification_provider = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('External provider used for verification')
    )
    
    verification_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Reference ID from verification provider')
    )
    
    # Results
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether verification was successful')
    )
    
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Confidence score from verification (0-100)')
    )
    
    verification_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Raw data from verification process')
    )
    
    # Timing
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When verification started')
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When verification was completed')
    )
    
    # Notes and errors
    notes = models.TextField(
        blank=True,
        help_text=_('Notes about the verification process')
    )
    
    error_message = models.TextField(
        blank=True,
        help_text=_('Error message if verification failed')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('KYC Verification')
        verbose_name_plural = _('KYC Verifications')
        db_table = 'kyc_verifications'
        indexes = [
            models.Index(fields=['verification_type']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]
        ordering = ['started_at']
    
    def __str__(self):
        return f"{self.get_verification_type_display()} for {self.kyc_request.user.username}"


class KYCDocument(models.Model):
    """
    Documents submitted for KYC verification
    """
    DOCUMENT_TYPE_CHOICES = [
        ('identity', _('Identity Document')),
        ('address_proof', _('Address Proof')),
        ('financial_proof', _('Financial Proof')),
        ('employment_proof', _('Employment Proof')),
        ('business_registration', _('Business Registration')),
        ('bank_statement', _('Bank Statement')),
        ('tax_document', _('Tax Document')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('verified', _('Verified')),
        ('rejected', _('Rejected')),
        ('requires_review', _('Requires Review')),
    ]
    
    kyc_request = models.ForeignKey(
        KYCRequest,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        help_text=_('Type of document')
    )
    
    document_file = models.FileField(
        upload_to='kyc_documents/',
        help_text=_('Uploaded document file')
    )
    
    document_name = models.CharField(
        max_length=200,
        help_text=_('Name/description of the document')
    )
    
    document_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Document identification number')
    )
    
    issue_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Document issue date')
    )
    
    expiry_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Document expiry date')
    )
    
    issuing_authority = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Authority that issued the document')
    )
    
    # Verification status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Verification status of this document')
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='verified_kyc_documents',
        help_text=_('Admin who verified this document')
    )
    
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When document was verified')
    )
    
    verification_notes = models.TextField(
        blank=True,
        help_text=_('Notes from document verification')
    )
    
    rejection_reason = models.TextField(
        blank=True,
        help_text=_('Reason for rejection if applicable')
    )
    
    # Document metadata
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('File size in bytes')
    )
    
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text=_('SHA-256 hash of the document file')
    )
    
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('MIME type of the document file')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('KYC Document')
        verbose_name_plural = _('KYC Documents')
        db_table = 'kyc_documents'
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.document_name} - {self.kyc_request.user.username}"
    
    def save(self, *args, **kwargs):
        if self.document_file and not self.file_size:
            self.file_size = self.document_file.size
        super().save(*args, **kwargs)


class KYCComplianceCheck(models.Model):
    """
    Compliance checks performed during KYC process
    """
    CHECK_TYPE_CHOICES = [
        ('aml', _('Anti-Money Laundering')),
        ('ctf', _('Counter-Terrorism Financing')),
        ('sanctions', _('Sanctions Screening')),
        ('pep', _('Politically Exposed Person')),
        ('adverse_media', _('Adverse Media Screening')),
        ('risk_assessment', _('Risk Assessment')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('passed', _('Passed')),
        ('failed', _('Failed')),
        ('requires_review', _('Requires Review')),
    ]
    
    kyc_request = models.ForeignKey(
        KYCRequest,
        on_delete=models.CASCADE,
        related_name='compliance_checks'
    )
    
    check_type = models.CharField(
        max_length=20,
        choices=CHECK_TYPE_CHOICES,
        help_text=_('Type of compliance check')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Status of the compliance check')
    )
    
    # Check details
    check_provider = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Provider used for the compliance check')
    )
    
    check_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Reference ID from the compliance check')
    )
    
    # Results
    risk_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Risk score from the check (0-100)')
    )
    
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', _('Low Risk')),
            ('medium', _('Medium Risk')),
            ('high', _('High Risk')),
            ('critical', _('Critical Risk')),
        ],
        blank=True,
        help_text=_('Risk level determined by the check')
    )
    
    check_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Raw data from the compliance check')
    )
    
    # Timing
    initiated_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When the check was initiated')
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When the check was completed')
    )
    
    # Notes and findings
    notes = models.TextField(
        blank=True,
        help_text=_('Notes about the compliance check')
    )
    
    findings = models.TextField(
        blank=True,
        help_text=_('Key findings from the compliance check')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('KYC Compliance Check')
        verbose_name_plural = _('KYC Compliance Checks')
        db_table = 'kyc_compliance_checks'
        indexes = [
            models.Index(fields=['check_type']),
            models.Index(fields=['status']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['initiated_at']),
        ]
        ordering = ['initiated_at']
    
    def __str__(self):
        return f"{self.get_check_type_display()} for {self.kyc_request.user.username}"
    
    @property
    def is_passed(self):
        return self.status == 'passed'
    
    @property
    def is_failed(self):
        return self.status == 'failed'
