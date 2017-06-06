from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models

decimal = RegexValidator(r'^[0-9]+(\.[0-9]{1,5})?$', 'Enkel decimalen toegelaten bv. 0.1')
alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Enkel alphanumerische waarden toegtelaten bv. abc123  .')
alphaChar = RegexValidator(r'^[a-zA-Z_ ]*$', 'Enkel letters toegelaten bv a-z,A-Z')


class UserType(models.Model):
    class Meta:
        verbose_name_plural = "gebruikerstypen"

    name = models.CharField(max_length=50, validators=[alphaChar])

    @classmethod
    def create(cls, name):
        user_type = cls(name=name)
        user_type.save()
        return user_type

    def __str__(self):
        return 'type: ' + str(self.name)


# BEGIN USER PROFILE
class UserProfile(models.Model):
    SEX_CHOICES = (
        ('man', 'Man'),
        ('vrouw', 'Vrouw'),
        ('andere', 'Anders'),
    )
    STATUS_CHOICES = (
        ('student', 'Student'),
        ('bedrijf', 'Bedrijf'),
        ('algemene gebruiker', 'Algemeen gebruiker'),
    )

    HOOK_UP_CHOICES = (
        ('Social media', (
            ('facebook', 'Facebook'),
            ('twitter', 'Twitter'),
            ('linked', 'LinkedIn'),
            ('andere', 'Andere'),
        )
         ),
        ('evenement', 'Evenement'),
        ('andere', 'Andere'),
    )

    PAYMENT_CHOICES = (
        ('paypal', 'Paypal'),
        ('bank', 'Bankkaart'),
        ('bitcoint', 'Bitcoint'),
    )

    PREFERENCE_CHOICES = (
        ('eenmalig opdracht', 'Eenmalig opdracht'),
        ('langdurige opdracht', 'langdurige opdracht'),
    )
    user = models.OneToOneField(User)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    hook_up = models.CharField(max_length=10, choices=HOOK_UP_CHOICES, blank=True, null=True)
    payment = models.CharField(max_length=10, choices=PAYMENT_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    # deze link breken
    student_details = models.ForeignKey('StudentDetails', on_delete=models.SET_NULL, null=True, blank=True)
    company_details = models.ForeignKey('CompanyDetails', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "type: " + str(self.user_type.name) + ' naam: ' + str(self.user.first_name) + ' ' + str(
            self.user.last_name) \
               + ' sex: ' + str(self.sex) + ' status: ' + str(self.status)


class StudentDetails(models.Model):
    class Meta:
        verbose_name_plural = "Studentendetails"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.CharField(max_length=65, blank=True)
    education = models.CharField(max_length=65, blank=True)

    def __str__(self):
        return str(self.user.username) + ' ' + str(self.school)


class CompanyDetails(models.Model):
    PREFERENCE_CHOICES = (
        ('single', 'eenmalig opdracht'),
        ('long', 'langdurige opdracht'),
    )

    class Meta:
        verbose_name_plural = "Bedrijfsdetails"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_number = models.IntegerField(null=True, blank=True)
    sector = models.CharField(max_length=65, blank=True)
    preference = models.CharField(max_length=10, choices=PREFERENCE_CHOICES, blank=True, null=False)

    def __str__(self):
        return str(self.user.username) + ' preference ' + str(self.preference)


# END USER PROFILE

class UserFile(models.Model):
    owner = models.ForeignKey(User, related_name="user_texter", on_delete=models.CASCADE)
    name = models.CharField(max_length=65, blank=True)
    thema = models.CharField(max_length=65, blank=True)
    word_count = models.IntegerField(blank=True)
    upload_date = models.DateTimeField(blank=False)
    accept_date = models.DateTimeField(blank=True)
    end_date = models.DateTimeField(blank=False)
    checker = models.ForeignKey(User, related_name="user_checker", on_delete=models.SET_NULL, null=True, blank=True)
    price = models.FloatField(blank=True)

    def get_owner_full_name(self):
        return self.owner.first_name + " " + self.owner.last_name

    def get_checker_full_name(self):
        if self.checker is None:
            return "None"
        else:
            return self.checker.first_name + " " + self.checker.last_name

    def __str__(self):
        if self.checker is None:
            return "owner: " + str(self.owner.first_name) + ' name: ' + str(self.name) + ' checker: None '
        else:
            return "owner: " + str(self.owner.first_name) + ' name: ' + str(self.name) + ' checker: ' + str(
                self.checker.first_name)
