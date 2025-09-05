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
    
class Patient(models.Model):
    """
    Represents the simple 'patients' table to store names.
    This is also an unmanaged model.
    """
    desynpuf_id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'patients'

class PatientAnalysis(models.Model):
    desynpuf_id = models.CharField(primary_key=True, max_length=255)
    age = models.IntegerField()
    gender_male = models.IntegerField()
    race_white = models.IntegerField()
    race_black = models.IntegerField()
    chronic_condition_count = models.IntegerField()
    high_impact_conditions = models.TextField(blank=True, null=True)
    sp_chf = models.IntegerField()
    sp_diabetes = models.IntegerField()
    sp_chrnkidn = models.IntegerField()
    sp_cncr = models.IntegerField()
    sp_copd = models.IntegerField()
    sp_depressn = models.IntegerField()
    sp_ischmcht = models.IntegerField()
    sp_strketia = models.IntegerField()
    sp_alzhdmta = models.IntegerField()
    sp_osteoprs = models.IntegerField()
    sp_ra_oa = models.IntegerField()
    inpatient_admissions = models.IntegerField()
    inpatient_days = models.IntegerField()
    outpatient_visits = models.IntegerField()
    total_medicare_costs = models.DecimalField(max_digits=10, decimal_places=2)
    prior_hospitalization = models.IntegerField()

    # --- CORRECTED FIELDS ---
    # These now match the fields your template and original schema expect.
    risk_30d_hospitalization = models.FloatField()
    risk_60d_hospitalization = models.FloatField()
    risk_90d_hospitalization = models.FloatField()
    mortality_risk = models.FloatField()

    RISK_TIER_CHOICES = [('1', 'Critical'), ('2', 'High'), ('3', 'Medium'), ('4', 'Low'), ('5', 'Healthy')]
    risk_tier = models.CharField(max_length=10, choices=RISK_TIER_CHOICES)
    risk_tier_label = models.CharField(max_length=50) 
    
    care_intervention = models.TextField(blank=True, null=True)
    annual_intervention_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_savings = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prevented_hospitalizations = models.IntegerField(null=True, blank=True)
    
    @property
    def patient_name(self):
        try:
            patient = Patient.objects.get(desynpuf_id=self.desynpuf_id)
            return patient.name
        except Patient.DoesNotExist:
            return f"Patient {self.desynpuf_id[:8]}"

    def get_conditions_display(self):
        """
        Creates a readable, comma-separated string of the patient's chronic conditions.
        This is the complete and corrected version.
        """
        conditions = []
        if self.sp_chf: conditions.append("CHF")
        if self.sp_diabetes: conditions.append("Diabetes")
        if self.sp_chrnkidn: conditions.append("Chronic Kidney")
        if self.sp_cncr: conditions.append("Cancer")
        if self.sp_copd: conditions.append("COPD")
        if self.sp_depressn: conditions.append("Depression")
        if self.sp_ischmcht: conditions.append("Ischemic Heart")
        if self.sp_strketia: conditions.append("Stroke/TIA")
        if self.sp_alzhdmta: conditions.append("Alzheimer's/Dementia")
        if self.sp_osteoprs: conditions.append("Osteoporosis")
        if self.sp_ra_oa: conditions.append("RA/OA")
        
        return ", ".join(conditions) if conditions else "None"

    class Meta:
        managed = False
        db_table = 'patient_analysis'
        ordering = ['-risk_tier', '-risk_90d_hospitalization']
