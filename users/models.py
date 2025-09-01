from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Extended User model for CineChainLanka platform
    """
    USER_TYPE_CHOICES = [
        ('creator', _('Content Creator')),
        ('investor', _('Investor/Backer')),
        ('admin', _('Platform Admin')),
    ]
    
    KYC_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('submitted', _('Submitted')),
        ('verified', _('Verified')),
        ('rejected', _('Rejected')),
    ]
    
    # Basic user information
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='investor',
        help_text=_('Type of user on the platform')
    )
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text=_('Phone number for contact and verification')
    )
    
    # Profile information
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text=_('User profile picture')
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text=_('User biography and description')
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text=_('User date of birth for age verification')
    )
    
    # Address information
    address_line1 = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Primary address line')
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Secondary address line')
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('City of residence')
    )
    state_province = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('State or province')
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('Postal/ZIP code')
    )
    country = models.CharField(
        max_length=100,
        default='Sri Lanka',
        help_text=_('Country of residence')
    )
    
    # KYC and verification
    kyc_status = models.CharField(
        max_length=20,
        choices=KYC_STATUS_CHOICES,
        default='pending',
        help_text=_('KYC verification status')
    )
    kyc_submitted_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When KYC was submitted')
    )
    kyc_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When KYC was verified')
    )
    
    # Platform preferences
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('si', 'Sinhala'),
            ('ta', 'Tamil'),
        ],
        default='en',
        help_text=_('Preferred language for platform interface')
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text=_('Receive email notifications')
    )
    sms_notifications = models.BooleanField(
        default=False,
        help_text=_('Receive SMS notifications')
    )
    
    # Creator-specific fields
    creator_verified = models.BooleanField(
        default=False,
        help_text=_('Whether the creator account is verified')
    )
    creator_category = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Primary category of content creation')
    )
    
    # Investor-specific fields
    investment_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text=_('Maximum investment limit for this user')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text=_('IP address of last login')
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users'
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['kyc_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_creator(self):
        return self.user_type == 'creator'
    
    @property
    def is_investor(self):
        return self.user_type == 'investor'
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_kyc_verified(self):
        return self.kyc_status == 'verified'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class UserProfile(models.Model):
    """
    Extended profile information for users
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='extended_profile'
    )
    
    # Social media links
    website = models.URLField(
        blank=True,
        help_text=_('Personal or business website')
    )
    facebook = models.URLField(
        blank=True,
        help_text=_('Facebook profile URL')
    )
    twitter = models.URLField(
        blank=True,
        help_text=_('Twitter profile URL')
    )
    instagram = models.URLField(
        blank=True,
        help_text=_('Instagram profile URL')
    )
    linkedin = models.URLField(
        blank=True,
        help_text=_('LinkedIn profile URL')
    )
    
    # Professional information
    occupation = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Current occupation or profession')
    )
    company = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Current company or organization')
    )
    experience_years = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Years of experience in the field')
    )
    
    # Creator portfolio
    portfolio_description = models.TextField(
        blank=True,
        help_text=_('Description of creator portfolio and achievements')
    )
    awards = models.TextField(
        blank=True,
        help_text=_('Awards and recognitions received')
    )
    
    # Financial information
    annual_income_range = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('under_500k', 'Under LKR 500,000'),
            ('500k_1m', 'LKR 500,000 - 1,000,000'),
            ('1m_2m', 'LKR 1,000,000 - 2,000,000'),
            ('2m_5m', 'LKR 2,000,000 - 5,000,000'),
            ('5m_10m', 'LKR 5,000,000 - 10,000,000'),
            ('over_10m', 'Over LKR 10,000,000'),
        ],
        help_text=_('Annual income range for investment purposes')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.username}"


class UserDocument(models.Model):
    """
    User documents for KYC and verification
    """
    DOCUMENT_TYPE_CHOICES = [
        ('national_id', _('National ID Card')),
        ('passport', _('Passport')),
        ('drivers_license', _('Driver\'s License')),
        ('utility_bill', _('Utility Bill')),
        ('bank_statement', _('Bank Statement')),
        ('proof_of_income', _('Proof of Income')),
        ('business_registration', _('Business Registration')),
        ('other', _('Other')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        help_text=_('Type of document')
    )
    
    document_file = models.FileField(
        upload_to='user_documents/',
        help_text=_('Uploaded document file')
    )
    
    document_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Document identification number')
    )
    
    expiry_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Document expiry date if applicable')
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether the document has been verified')
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='verified_documents',
        help_text=_('Admin who verified this document')
    )
    
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When the document was verified')
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_('Admin notes about the document')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Document')
        verbose_name_plural = _('User Documents')
        db_table = 'user_documents'
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_document_type_display()}"
