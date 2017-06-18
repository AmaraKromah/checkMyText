# coding=utf-8
from __future__ import print_function

# import datetime
import re

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

from dashboard.models import UserFile


def regex_validation(pattern, to_check):
    if pattern == 1:
        match_len = re.compile('^.{3,}$')
        if not match_len.match(to_check):
            return False
        else:
            return True

    if pattern == 2:
        has_upper = re.compile("^(.*[A-Z].*)$")
        if not has_upper.match(to_check):
            return False
        else:
            return True

    if pattern == 3:
        has_digit = re.compile("^(.*[0-9].*)$")
        if not has_digit.match(to_check):
            return False
        else:
            return True

    if pattern == 4:
        has_special = re.compile("^(.*\W.*)$")
        if not has_special.match(to_check):
            return False
        else:
            return True

    if pattern == 5:
        has_space = re.compile("^(.*\s.*)$")
        if has_space.match(to_check):
            return True
        else:
            return False

    if pattern == 6:
        valid_email = re.compile('([\w\-.]+@(\w[\w\-]+\.)+[\w\-]+)')
        if not valid_email.match(to_check):
            return False
        else:
            return True

    if pattern == 7:
        alphanum_w_space = re.compile('^[0-9a-zA-Z\s]*$')
        if not alphanum_w_space.match(to_check):
            return False
        else:
            return True

    if pattern == 8:
        alphachar = re.compile('^[a-zA-Z]*$')
        if not alphachar.match(to_check):
            return False
        else:
            return True

    if pattern == 9:
        alphachar_w_space = re.compile('^[a-zA-Z\s]*$')
        if not alphachar_w_space.match(to_check):
            return False
        else:
            return True

    if pattern == 10:
        alphanum_w_limited_special = re.compile('^[0-9a-zA-Z-_,]*$')
        if not alphanum_w_limited_special.match(to_check):
            return False
        else:
            return True


# USERINTERFACE

class UserProfileForm(forms.Form):
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

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 15, 'maxlength': 15}))
    email = forms.CharField(required=False)
    sex = forms.CharField(widget=forms.Select(choices=SEX_CHOICES), required=False)
    birth_date = forms.DateField(required=False)
    hook_up = forms.CharField(widget=forms.Select(choices=HOOK_UP_CHOICES), required=False)
    payment = forms.CharField(widget=forms.Select(choices=PAYMENT_CHOICES), required=False)
    status = forms.CharField(widget=forms.Select(choices=STATUS_CHOICES), required=False)
    school = forms.CharField(required=False)
    education = forms.CharField(required=False)
    business_number = forms.IntegerField(required=False)
    sector = forms.CharField(required=False)
    preference = forms.CharField(widget=forms.Select(choices=PREFERENCE_CHOICES), required=False)
    password = forms.CharField(required=False, )
    confirm_password = forms.CharField(required=False)

    # Validation
    def clean(self):
        cleaned_data = super(UserProfileForm, self).clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        email_exist = User.objects.filter(email=email).exists()
        username_exist = User.objects.filter(username=username).exists()

        if username_exist:
            raise forms.ValidationError('Een gebruiker met dit gebruikersnaam bestaat al reeds')
        if email_exist:
            raise forms.ValidationError('Een gebruiker met dit email bestaat al reeds')

        return super(UserProfileForm, self).clean()

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if first_name:
            if not regex_validation(8, first_name):
                raise forms.ValidationError("voornaam mag geen speciale tekens, getallen  of spaties bevatten")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if last_name:
            if not regex_validation(9, last_name):
                raise forms.ValidationError("Achternaam mag geen speciale tekens of getallen bevatten")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get("username")
        max_len = 15
        min_len = 3
        if username:
            if not regex_validation(10, username):
                raise forms.ValidationError("enkel letters,-,_, en cijfers toegestaan")

            if len(username) > max_len or len(username) < min_len:
                raise forms.ValidationError(
                    "Dit veld moet meer dan " + str(min_len) + " maar niet meer dan " + str(max_len) +
                    " karakter lang zijn " + str(len(username)) + ' karakter(s) ingegeven')
        else:
            raise forms.ValidationError("Dit veld is verplicht")

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if not regex_validation(1, password):
                raise forms.ValidationError("Wachtwoord is te kort")
                # if not regex_validation(2, password):
                #     raise forms.ValidationError("Wachtwoord moet een hoofdletter bevatten")
                #
                # if not regex_validation(3, password):
                #     raise forms.ValidationError("Wachtwoord moet een getal bevatten")
                #
                # if not regex_validation(4, password):
                #     raise forms.ValidationError("Wachtwoord moet een speciale karakter bevatten")
                #
                # if regex_validation(5, password):
                #     raise forms.ValidationError("Wachtwoord mag geen spaties bevatten")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return password

    def clean_confirm_password(self):
        cleaned_data = super(UserProfileForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password is not None:
            if confirm_password != password:
                raise forms.ValidationError("wachtwoorden komen niet overeen")
        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:

            if not regex_validation(6, email):
                raise forms.ValidationError("Ongeldige email adres")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return email

    def clean_school(self):
        school = self.cleaned_data.get("school")
        if not regex_validation(7, school):
            raise forms.ValidationError("school mag geen speciale tekens bevatten")
        return school

    def clean_education(self):
        education = self.cleaned_data.get("education")
        if not regex_validation(9, education):
            raise forms.ValidationError("opleiding mag geen speciale tekens of getallen bevatten")
        return education

    def clean_sector(self):
        sector = self.cleaned_data.get("sector")
        if not regex_validation(9, sector):
            raise forms.ValidationError("opleiding mag geen speciale tekens of getallen bevatten")
        return sector

    def clean_birthday(self):
        b_day = str(self.cleaned_data.get("birthday"))

        # try:
        #     print(datetime.datetime.strptime(b_day, '%Y-%m-%d'))
        # except ValueError:
        #     print("Incorrect data format, should be YYYY-MM-DD")
        #
        # print(b_day)

        if b_day is not None:
            return b_day


class UserLoginForm(forms.Form):
    email = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            if not regex_validation(6, email):
                raise forms.ValidationError("Ongeldige email adres")
        else:
            raise forms.ValidationError("Deze veld is vereist")

        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            raise forms.ValidationError("Deze veld is vereist")

        return password


class UserChangePassword(forms.Form):
    current_password = forms.CharField(required=False)
    new_password = forms.CharField(required=False)
    confirm_password = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):  # overweeg user hier te implementeren en haar de kwargs shit eruit
        self.user = kwargs.pop('user', None)
        super(UserChangePassword, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        cleaned_data = super(UserChangePassword, self).clean()
        password = cleaned_data.get("current_password")

        if password:
            user = authenticate(username=self.user.username, password=password)
            if user is not None:
                print("huidig ingevoerde wachtwoord komt overeen met de huidige wachtwoord")
                return password
            else:
                raise forms.ValidationError("Huidige wachtwoord komen niet overeen")

        else:
            raise forms.ValidationError("Dit veld is verplicht")

    def clean_new_password(self):
        cleaned_data = super(UserChangePassword, self).clean()
        password = cleaned_data.get("current_password")  # pas dit indien nodig aan
        new_password = self.cleaned_data.get("new_password")

        if new_password:
            if password is not None:
                if not regex_validation(1, new_password):
                    raise forms.ValidationError("Wachtwoord is te kort")

                    # if not regex_validation(2, new_password):
                    #     raise forms.ValidationError("Wachtwoord moet een hoofdletter bevatten")
                    #
                    # if not regex_validation(3, new_password):
                    #     raise forms.ValidationError("Wachtwoord moet een getal bevatten")
                    #
                    # if not regex_validation(4, new_password):
                    #     raise forms.ValidationError("Wachtwoord moet een speciale karakter bevatten")
                    #
                    # if regex_validation(5, new_password):
                    #     raise forms.ValidationError("Wachtwoord mag geen spaties bevatten")
        else:
            raise forms.ValidationError("Dit veld is verplicht")

        return new_password

    def clean_confirm_password(self):
        cleaned_data = super(UserChangePassword, self).clean()
        password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if confirm_password:
            if password is not None and new_password is not None:
                if confirm_password != new_password:
                    raise forms.ValidationError("wachtwoorden komen niet overeen")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return confirm_password


class UserEditProfile(forms.Form):
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

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 15, 'maxlength': 15}))
    sex = forms.CharField(widget=forms.Select(choices=SEX_CHOICES), required=False)
    birth_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, required=False)
    hook_up = forms.CharField(widget=forms.Select(choices=HOOK_UP_CHOICES), required=False)
    payment = forms.CharField(widget=forms.Select(choices=PAYMENT_CHOICES), required=False)
    status = forms.CharField(widget=forms.Select(choices=STATUS_CHOICES), required=False)
    school = forms.CharField(required=False)
    education = forms.CharField(required=False)
    business_number = forms.IntegerField(required=False)
    sector = forms.CharField(required=False)
    preference = forms.CharField(widget=forms.Select(choices=PREFERENCE_CHOICES), required=False)

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if first_name:
            if not regex_validation(8, first_name):
                raise forms.ValidationError("voornaam mag geen speciale tekens, getallen  of spaties bevatten")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if last_name:
            if not regex_validation(9, last_name):
                raise forms.ValidationError("Achternaam mag geen speciale tekens of getallen bevatten")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get("username")
        max_len = 15
        min_len = 3
        if username:
            if not regex_validation(10, username):
                raise forms.ValidationError("enkel letters,-,_, en cijfers toegestaan")

            if len(username) > max_len or len(username) < min_len:
                raise forms.ValidationError(
                    "Dit veld moet meer dan " + str(min_len) + " maar niet meer dan " + str(max_len) +
                    " karakter lang zijn " + str(len(username)) + ' karakter(s) ingegeven')
        else:
            raise forms.ValidationError("Dit veld is verplicht")

        return username

    def clean_school(self):
        school = self.cleaned_data.get("school")
        if not regex_validation(7, school):
            raise forms.ValidationError("school mag geen speciale tekens bevatten")
        return school

    def clean_education(self):
        education = self.cleaned_data.get("education")
        if not regex_validation(9, education):
            raise forms.ValidationError("opleiding mag geen speciale tekens of getallen bevatten")
        return education

    def clean_sector(self):
        sector = self.cleaned_data.get("sector")
        if not regex_validation(9, sector):
            raise forms.ValidationError("opleiding mag geen speciale tekens of getallen bevatten")
        return sector


class SetPasswordForm(forms.Form):
    new_password = forms.CharField(label="nieuwe", widget=forms.PasswordInput, strip=False, )
    confirm_password = forms.CharField(label="nieuwe wachtwoord bevestiging", strip=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    # doe nog u eigen password controle implementeren
    def clean_confirm_password(self):
        password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if confirm_password:
            if password is not None:
                if confirm_password != password:
                    raise forms.ValidationError("wachtwoorden komen niet overeen")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return confirm_password

    def save(self, commit=True):
        password = self.cleaned_data["new_password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


# USER FILES

class CreateUserFileForm(forms.ModelForm):
    class Meta:
        model = UserFile
        fields = ('name', 'thema', 'file', 'end_date')

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name:
            if not regex_validation(9, name):
                raise forms.ValidationError("Naam mag geen speciale tekens of getallen bevatten")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return name

    def clean_thema(self):
        thema = self.cleaned_data.get("thema")
        if thema:
            if not regex_validation(9, thema):
                raise forms.ValidationError("thema mag geen speciale tekens of getallen bevatten")
        else:
            raise forms.ValidationError("Dit veld is verplicht")
        return thema

    def clean_file(self):
        project_file = self.cleaned_data.get("file")

        if project_file is not None:
            file_name = project_file.name
            if not str(file_name).endswith('.docx'):
                raise forms.ValidationError("Gelieve Word document (.docx) up te loaden")
        else:
            raise forms.ValidationError("Gelieve een bestand up te loaden")
        return project_file

    def clean_end_date(self):
        end_date = self.cleaned_data.get("end_date")
        now = timezone.now() + timezone.timedelta(hours=2)
        min_date = now + timezone.timedelta(days=4)

        if end_date < min_date:
            raise forms.ValidationError("Dag mag niet voor 4 dagen (" + str(min_date.date()) + " " +
                                        str(min_date.time()).split(".")[0] + str(") van nu vallen"))
        return end_date


class EditUserFileForm(forms.ModelForm):
    # nog validatieprocess starten
    class Meta:
        model = UserFile
        fields = ('name', 'thema', 'file', 'end_date')
