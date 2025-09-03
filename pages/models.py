# pages/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None   # remove username
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)  # ✅ this is new

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()


class Admin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)  # store hashed password

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email
    
class PatientAnalysis(models.Model):
    """
    This model represents the patient_analysis table, which is populated
    by the machine learning pipeline. It is an UNMANAGED model.
    """
    # Unique patient identifier
    desynpuf_id = models.CharField(primary_key=True, max_length=255)
    
    # Demographics
    age = models.IntegerField()
    gender_male = models.BooleanField()
    race_white = models.BooleanField()
    race_black = models.BooleanField()
    
    # Health Metrics
    chronic_condition_count = models.IntegerField()
    high_impact_conditions = models.TextField(blank=True, null=True)
    inpatient_admissions = models.IntegerField()
    inpatient_days = models.IntegerField()
    outpatient_visits = models.IntegerField()
    total_medicare_costs = models.DecimalField(max_digits=10, decimal_places=2)
    prior_hospitalization = models.BooleanField()

    # Specific Chronic Conditions (Booleans)
    sp_chf = models.BooleanField()
    sp_diabetes = models.BooleanField()
    sp_chrnkidn = models.BooleanField()
    sp_cncr = models.BooleanField()
    sp_copd = models.BooleanField()
    sp_depressn = models.BooleanField()
    sp_ischmcht = models.BooleanField()
    sp_strketia = models.BooleanField()
    sp_alzhdmta = models.BooleanField()
    sp_osteoprs = models.BooleanField()
    sp_ra_oa = models.BooleanField()

    # Risk Scores and Tiers from ML Model
    RISK_TIER_CHOICES = [
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Medium'),
        (4, 'Low'),
        (5, 'Healthy'),
    ]
    risk_30d_hospitalization = models.FloatField()
    risk_60d_hospitalization = models.FloatField()
    risk_90d_hospitalization = models.FloatField()
    mortality_risk = models.FloatField()
    risk_tier = models.IntegerField(choices=RISK_TIER_CHOICES)
    
    # Interventions and Savings
    care_intervention = models.TextField(blank=True, null=True)
    annual_intervention_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cost_savings = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    prevented_hospitalizations = models.IntegerField(null=True)

    class Meta:
        managed = False  # <-- CRITICAL: Tells Django not to touch this table
        db_table = 'patient_analysis'  # The exact name of your PostgreSQL table
        ordering = ['-risk_90d_hospitalization'] # Default sort: highest risk first