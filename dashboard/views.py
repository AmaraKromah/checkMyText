from __future__ import print_function

import math
import warnings

import moment
import textract
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q  # om OR te kunnnen gebruiken een andere complexere queries
from django.db.models.query import EmptyResultSet
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, redirect, resolve_url
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.deprecation import RemovedInDjango20Warning
from django.utils.http import urlsafe_base64_decode
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View

from .forms import (
    UserProfileForm,
    UserLoginForm,
    UserChangePassword,
    UserEditProfile,
    SetPasswordForm,
    CreateUserFileForm
)
from .models import User, StudentDetails, CompanyDetails, UserProfile, UserType, UserFile


# ---------------hierboven is niet van mij----------------------------


# _______________OVERWRITE VAN DJANGO_______________________________
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='password_reset/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           extra_context=None):
    """
    Check the hash in a password reset link and present a form for entering a
    new password.
    """
    warnings.warn("The password_reset_confirm() view is superseded by the "
                  "class-based PasswordResetConfirmView().",
                  RemovedInDjango20Warning, stacklevel=2)
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = 'Enter new password'
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = 'Password reset unsuccessful'
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


# ______________ EIGEN CODE __________________________

class IndexView(View):
    @staticmethod
    def get(request):

        if request.user.is_authenticated():
            return render(request, 'dashboard/index.html')
        else:
            return redirect('login')


class PreRegisterView(View):
    @staticmethod
    def get(request):

        return render(request, 'account/user_type_select.html')

    @staticmethod
    def post(request):
        if 'texter' in request.POST:
            request.session['type'] = "texter"
            if not UserType.objects.filter(name="texter").exists():
                UserType.create(name="texter")

            return redirect('register')

        elif 'checker' in request.POST:
            request.session['type'] = "checker"
            if not UserType.objects.filter(name="checker").exists():
                UserType.create(name="checker")

            return redirect('register')
        else:
            return render(request, 'account/user_type_select.html', {"error": "yeah no"})


class RegisterFormView(View):
    @staticmethod
    def post(request):
        user_form = UserProfileForm(data=request.POST)
        if user_form.is_valid():

            student_details = None
            company_details = None
            user_type = None  # check of je dit kan verwijderen
            session = request.session['type']
            first_name = user_form.cleaned_data['first_name'].capitalize()
            last_name = user_form.cleaned_data['last_name'].capitalize()
            username = user_form.cleaned_data.get('username')
            email = user_form.cleaned_data.get('email')
            password = user_form.cleaned_data.get('password')
            sex = user_form.cleaned_data.get('sex')
            birthday = user_form.cleaned_data.get('birth_date')
            hook_up = user_form.cleaned_data.get('hook_up')
            payment = user_form.cleaned_data.get('payment')
            status = user_form.cleaned_data.get('status')
            school = user_form.cleaned_data.get('school')
            education = user_form.cleaned_data.get('education')
            business_number = user_form.cleaned_data.get('business_number')
            sector = user_form.cleaned_data.get('sector')
            preference = user_form.cleaned_data.get('preference')
            if session == "texter":
                try:
                    user_type = UserType.objects.get(name="texter")
                except ObjectDoesNotExist:
                    UserType.create(name="texter")
                    print("oei", user_type)
                    user_type = UserType.objects.get(name="texter")

            elif session == "checker":
                try:
                    user_type = UserType.objects.get(name="checker")
                except ObjectDoesNotExist:
                    UserType.create(name="checker")
                    user_type = UserType.objects.get(name="checker")

            user = User.objects.create_user(username=username, email=email, password=password,
                                            first_name=first_name, last_name=last_name)

            if status == 'student':
                student_details = StudentDetails.objects.create(user=user, school=school, education=education)
            elif status == 'bedrijf':
                company_details = CompanyDetails.objects.create(user=user, business_number=business_number,

                                                                sector=sector, preference=preference)

            profile = UserProfile.objects.create(user=user, user_type=user_type, sex=sex, hook_up=hook_up,
                                                 status=status, birth_date=birthday, payment=payment,
                                                 student_details=student_details, company_details=company_details)
            profile.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            return redirect('master:base')
        return render(request, 'account/register.html', {'user_form': user_form})

    @staticmethod
    def get(request):

        user_form = UserProfileForm()
        return render(request, 'account/register.html', {'user_form': user_form})


class LoginFormView(View):
    @staticmethod
    def post(request):
        login_form = UserLoginForm(data=request.POST)
        if login_form.is_valid():

            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']

            try:
                user_object = User.objects.get(email=email)
                user = authenticate(username=user_object.username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('dashboard')
                else:
                    messages.error(request, 'Verkeerde email of wachtwoord ingegeven')
                    return render(request, 'account/login.html',
                                  {'login_form': login_form})

            except ObjectDoesNotExist:
                messages.error(request, 'Wij hebben helaas geen gebruiker met deze email')
                return render(request, 'account/login.html',
                              {'login_form': login_form, })

        return render(request, 'account/login.html', {'login_form': login_form})

    @staticmethod
    def get(request):
        login_form = UserLoginForm()

        if request.user.is_authenticated():
            return redirect('dashboard')
        else:
            return render(request, 'account/login.html', {'login_form': login_form})


class ProfileView(View):
    @staticmethod
    def get(request):

        if request.user.is_authenticated():
            user = User.objects.get(id=request.user.id)
            return render(request, 'account/profile.html', {'user': user})
        else:
            return redirect('login')


class ProfileEditView(View):
    @staticmethod
    def post(request):
        profile_edit_form = UserEditProfile(data=request.POST)

        if profile_edit_form.is_valid():
            first_name = profile_edit_form.cleaned_data['first_name'].capitalize()
            last_name = profile_edit_form.cleaned_data['last_name'].capitalize()
            username = profile_edit_form.cleaned_data.get('username')
            sex = profile_edit_form.cleaned_data.get('sex')
            birth_date = profile_edit_form.cleaned_data.get('birth_date')
            hook_up = profile_edit_form.cleaned_data.get('hook_up')
            payment = profile_edit_form.cleaned_data.get('payment')
            status = profile_edit_form.cleaned_data.get('status')
            school = profile_edit_form.cleaned_data.get('school')
            education = profile_edit_form.cleaned_data.get('education')
            business_number = profile_edit_form.cleaned_data.get('business_number')
            sector = profile_edit_form.cleaned_data.get('sector')
            preference = profile_edit_form.cleaned_data.get('preference')

            user = User.objects.get(id=request.user.id)
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            if status == 'student':
                try:
                    student_details = StudentDetails.objects.get(user=user)
                    student_details.school = school
                    student_details.education = education
                    student_details.save()

                except ObjectDoesNotExist:
                    student_details = StudentDetails.objects.create(user=user, school=school, education=education)
                    profile = UserProfile.objects.get(user=user)
                    profile.student_details = student_details
                    profile.save()

                try:
                    CompanyDetails.objects.get(user=user).delete()
                except ObjectDoesNotExist:
                    pass

            elif status == 'bedrijf':
                try:
                    company_details = CompanyDetails.objects.get(user=user)
                    company_details.business_number = business_number
                    company_details.sector = sector
                    company_details.preference = preference
                    company_details.save()

                except ObjectDoesNotExist:
                    company_details = CompanyDetails.objects.create(user=user, business_number=business_number,
                                                                    sector=sector, preference=preference)
                    profile = UserProfile.objects.get(user=user)
                    profile.company_details = company_details
                    profile.save()

                try:
                    StudentDetails.objects.get(user=user).delete()
                except ObjectDoesNotExist:
                    pass
            else:
                try:
                    CompanyDetails.objects.get(user=user).delete()
                except ObjectDoesNotExist:
                    pass

                try:
                    StudentDetails.objects.get(user=user).delete()

                except ObjectDoesNotExist:
                    pass

            profile = UserProfile.objects.get(user=user)
            profile.sex = sex
            profile.hook_up = hook_up
            profile.status = status
            profile.birth_date = birth_date
            profile.payment = payment
            profile.save()

            return redirect('profile')
        return render(request, 'account/edit_profile.html', {'profile_edit_form': profile_edit_form})

    @staticmethod
    def get(request):

        if request.user.userprofile.status == "student":
            profile_edit_form = UserEditProfile(initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'username': request.user.username,
                'sex': request.user.userprofile.sex,
                'birth_date': request.user.userprofile.birth_date,
                'hook_up': request.user.userprofile.hook_up,
                'payment': request.user.userprofile.payment,
                'status': request.user.userprofile.status,
                'school': request.user.studentdetails.school,
                'education': request.user.studentdetails.education,
            })

        elif request.user.userprofile.status == "bedrijf":
            profile_edit_form = UserEditProfile(initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'username': request.user.username,
                'sex': request.user.userprofile.sex,
                'birth_date': request.user.userprofile.birth_date,
                'hook_up': request.user.userprofile.hook_up,
                'payment': request.user.userprofile.payment,
                'status': request.user.userprofile.status,
                'business_number': request.user.companydetails.business_number,
                'sector': request.user.companydetails.sector,
                'preference': request.user.companydetails.preference,
            })
        else:
            profile_edit_form = UserEditProfile(initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'username': request.user.username,
                'sex': request.user.userprofile.sex,
                'birth_date': request.user.userprofile.birth_date,
                'hook_up': request.user.userprofile.hook_up,
                'payment': request.user.userprofile.payment,
                'status': request.user.userprofile.status,
            })

        if request.user.is_authenticated():

            return render(request, 'account/edit_profile.html', {'profile_edit_form': profile_edit_form})
        else:
            return redirect('login')


class ChangePasswordView(View):
    @staticmethod
    def post(request):
        change_pass = UserChangePassword(data=request.POST, user=request.user)

        if change_pass.is_valid():
            current_pass = change_pass.cleaned_data.get("current_password")
            new_password = change_pass.cleaned_data.get("new_password")
            user = authenticate(username=request.user.username, password=current_pass)
            if user is not None:
                user.set_password(new_password)
                user.save()
                login(request, user)
                return redirect('profile')

        return render(request, 'account/change_password.html', {'change_password': change_pass})

    @staticmethod
    def get(request):

        change_pass = UserChangePassword(user=request.user)
        if request.user.is_authenticated():

            return render(request, 'account/change_password.html', {'change_password': change_pass})
        else:
            return redirect('login')


class Logout(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated():
            logout(request)
        return redirect('master:base')


# ZORG ERVOOR DAT JE NIET ZOMAAR VIA URL OP DE PAGINA'S KAN KOMEN
class ProjectIndexView(generic.ListView):
    template_name = 'dashboard/project_index.html'
    context_object_name = "all_projects"

    def dispatch(self, request, *args, **kwargs):  # onze request parameter opvangen

        if request.user.is_authenticated():
            return super(ProjectIndexView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('login')

    def get_queryset(self):
        if self.request.user.userprofile.user_type.name == "checker":
            return UserFile.objects.filter(Q(checker_id=self.request.user.id) | Q(checker_id__isnull=True)).order_by(
                'end_date')  # de - teken wil zeggen van groot naar klein
        else:
            return UserFile.objects.filter(owner_id=self.request.user.id).order_by(
                'end_date')


class ProjectRunningView(generic.ListView):
    template_name = 'dashboard/project_running.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.userprofile.user_type.name == "checker":
                return super(ProjectRunningView, self).dispatch(request, *args, **kwargs)
            else:
                return redirect('dashboard')
        else:
            return redirect('login')

    def get_queryset(self):
        return UserFile.objects.all()


class ProjectExpiredView(generic.ListView):
    template_name = 'dashboard/project_expired.html'
    context_object_name = "expired_projects"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(ProjectExpiredView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('login')

    def get_queryset(self):
        today = timezone.now()
        if self.request.user.userprofile.user_type.name == "checker":
            return UserFile.objects.filter(Q(checker_id=self.request.user.id), Q(end_date__lt=today)).order_by(
                'end_date')
        else:
            return UserFile.objects.filter(owner_id=self.request.user.id).filter(end_date__lt=today)


class ProjectDetailView(generic.DetailView):
    model = UserFile
    template_name = 'dashboard/project_detail.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(ProjectDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('login')

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        project = UserFile.objects.get(id__iexact=self.kwargs['pk'])
        path = project.file.path
        helper = HelperFunctions(path)
        whole_word = ""
        sentence_count = helper.get_sentence_count()
        sentence_sample_count = int(math.ceil(sentence_count * 0.35))

        sample_data = str(textract.process(path)).split(".")
        sample_count = 0
        for word in sample_data:
            if sample_count >= sentence_sample_count:
                break
            else:
                if word == "":
                    whole_word += "\n"
                else:
                    whole_word += word + "."
            sample_count += 1
        context['sample'] = whole_word

        return context


class ProjectCreateView(View):
    @staticmethod
    def post(request):
        files_form = CreateUserFileForm(data=request.POST, files=request.FILES)

        if files_form.is_valid():
            name = files_form.cleaned_data.get('name')
            thema = files_form.cleaned_data.get('thema')
            end_date = files_form.cleaned_data.get('end_date')
            owner = request.user
            now = timezone.now()
            upload_date = moment.utcnow().timezone('Europe/Brussels')  # same as today but used for calculations
            checker_end_date = moment.date(end_date)
            delta_deadline = (checker_end_date - upload_date).days
            price_word = 0.3
            project_file = files_form.cleaned_data.get('file')

            if not UserFile.objects.filter(name=name).exists():
                project = UserFile.objects.create(owner=owner, name=name, thema=thema, upload_date=now,
                                                  end_date=end_date, file=project_file)
                path = project.file.path
                helper = HelperFunctions(path)
                word_count = helper.get_word_count()

                if delta_deadline < 3:
                    price = word_count * price_word * 1.50
                elif 3 <= delta_deadline <= 7:
                    price = word_count * price_word * 1.30
                else:
                    price = word_count * price_word

                project.word_count = word_count
                project.price = price
                project.save()
                return redirect('dashboard')
            # vervang dit later door ajax
            return render(request, 'dashboard/project_new.html', {'files_form': files_form,
                                                                  'bestaat': 'deze opdracht bestaat al reeds',
                                                                  })

        return render(request, 'dashboard/project_new.html', {'files_form': files_form})

    @staticmethod
    def get(request):
        if request.user.is_authenticated():
            # if request.user.userprofile.user_type.name == "texter":
            files_form = CreateUserFileForm()
            return render(request, 'dashboard/project_new.html', {'files_form': files_form})
            # else:
            #     return redirect('dashboard')
        else:
            return redirect('login')


# nog implementeren
class ProjectEditView(View):
    pass


class ProjectDeleteView(generic.DeleteView):
    model = UserFile
    success_url = reverse_lazy('all_projects')


# AJAX CALLS
class getFilesDatesView(View):
    @staticmethod
    def get(request):
        files = UserFile.objects.filter(checker_id=request.user.id). \
            values('id', 'checker_id', 'owner_id', 'name', 'end_date')

        users = User.objects.all().values('id', 'last_name', 'first_name')
        response_data = {}
        try:
            response_data['result'] = 'Succes'
            response_data['dates'] = list(files)
            response_data['users'] = list(users)

        except (ObjectDoesNotExist, EmptyResultSet):  # errors nog opvangen in ajax
            response_data['result'] = 'Error'
            response_data['dates'] = 'No files found '
            response_data['users'] = 'No users found '

        if request.method == 'GET':
            if request.is_ajax():
                return JsonResponse(response_data)
        else:
            raise Http404


class confirmProjectView(View):
    @staticmethod
    def post(request):
        project_id = request.POST.get('project_id', None)
        project = UserFile.objects.get(id__iexact=project_id)
        print(project.file.name, project.file.url)
        # try catch voorzien hier
        user_name = request.user.first_name + " " + request.user.last_name
        response_data = {}

        if project.checker is None:
            project.checker = request.user
            project.accept_date = timezone.now()
            project.save()
            response_data['result'] = "no checker"
            response_data['checker'] = user_name
            response_data['accept_date'] = project.accept_date

        if request.is_ajax():
            return JsonResponse(response_data)
        else:
            raise Http404


class HelperFunctions:
    def __init__(self, path):
        self.path = path

    def get_word_count(self):
        project_file = textract.process(self.path).split()
        num_words = len(project_file)
        return num_words

    def get_sentence_count(self):
        project_file = str(textract.process(self.path)).split(".")
        sentence_count = len(project_file)
        return sentence_count
