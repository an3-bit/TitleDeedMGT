from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

MOBILE_SASA_API_URL = "https://api.mobilesasa.com/v1/send-message"
MOBILE_SASA_API_KEY = "api_key_here"

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="gil_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="gil_user_permissions",
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def save(self, *args, **kwargs):
        """Automatically split name into first_name and last_name."""
        if self.name:
            name_parts = self.name.split(" ", 1)
            self.first_name = name_parts[0]
            self.last_name = name_parts[1] if len(name_parts) > 1 else ""
        super().save(*args, **kwargs)


    def __str__(self):
        return self.email

class TitleTransferTypes(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Title Transfer Type"
        verbose_name_plural = "Title Transfer Types"

    def __str__(self):
        return self.name

class TitleProcess(models.Model):
    type = models.ForeignKey(
        TitleTransferTypes,
        on_delete=models.SET_NULL,
        null=True,
        related_name="processes",
    )
    process = models.CharField(max_length=100)
    message = models.TextField(default="Your process is now in this stage. Thank you!")

    class Meta:
        ordering = ["id"]
        verbose_name = "Title Process"
        verbose_name_plural = "Title Processes"

    def __str__(self):
        return f"{self.type.name if self.type else 'No Type'} - {self.process}"

class Client(models.Model):
    SERVICE_CHOICES = [
        ("land_survey", "Land Survey"),
        ("title_search", "Title Search"),
        ("land_transfer", "Land Transfer"),
        ("subdivision", "Subdivision"),
    ]

    PROCESS_CHOICES = [
        ("initial_submission", "Initial Submission"),
        ("registry_processing", "Registry Processing"),
        ("approval_verification", "Approval & Verification"),
        ("ready_for_collection", "Title Ready for Collection"),
    ]

    username = models.CharField(max_length=100, unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    join_date = models.DateTimeField(default=timezone.now)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, default="land_survey")
    process = models.CharField(max_length=50, choices=PROCESS_CHOICES, default="initial_submission")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ["username"]
        db_table = "clients"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

class Surveyor(models.Model):
    username = models.CharField(max_length=100, unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=200, default="inactive")
    join_date = models.DateTimeField(default=timezone.now)
    is_registered = models.BooleanField(default=False)
    is_serving = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Surveyor"
        verbose_name_plural = "Surveyors"
        ordering = ["username"]
        db_table = "surveyors"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

class Payment(models.Model):
    client_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    amount = models.IntegerField()
    transaction_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=200, default="waiting for approval")

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["client_name"]
        db_table = "payments"

    def __str__(self):
        return self.client_name

class TitleDocument(models.Model):
    STATUS_CHOICES = [
        ("registry_processing", "Registry Processing"),
        ("approval_verification", "Approval and Verification"),
        ("ready_for_collection", "Title Deed Ready for Collection"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="documents")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="registry_processing")
    pdf_file = models.FileField(upload_to="title_documents/")
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Title Document"
        verbose_name_plural = "Title Documents"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.client.firstname} {self.client.lastname} - {self.status}"
