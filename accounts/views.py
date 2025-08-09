from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.sites.shortcuts import get_current_site
# from django.utils.encoding import force_bytes, force_str
# from django.template.loader import render_to_string
# from myinventory.settings import EMAIL_HOST_USER
from django.shortcuts import render, redirect
from myinventory.utils import is_valid_email
from django.contrib.auth.models import User
# from django.core.mail import send_mail
# from django.urls import reverse


def login(request):

    context = {
        "page_title": "Sign In"
    }

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')

        else:
            context["error_message"] = "Invalid username or password."
            return render(request, "accounts/sign-in.html", context)

    return render(request, "accounts/sign-in.html", context)


def register(request):

    context = {
        "page_title": "Sign Up"
    }

    if request.method == 'POST':

        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not is_valid_email(email):
            context["error_message"] = "Invalid email address."
            return render(request, "accounts/sign-up.html", context)

        if User.objects.filter(email=email).exists():
            context["error_message"] = "User with this email already exists."
            return render(request, "accounts/sign-up.html", context)

        else:
            user = User.objects.create_user(username=username, email=email, password=password)

            # user.is_active = False
            user.is_active = True
            user.save()

            # current_site = get_current_site(request)
            # mail_subject = "Activate your account"

            # domain = current_site.domain
            # token = default_token_generator.make_token(user)
            # uid = urlsafe_base64_encode(force_bytes(user.pk))

            # verification_link = f"http://{domain}/accounts/activate/{uid}/{token}"

            # message = render_to_string('accounts/email-verification.html', {
            #     'user': user,
            #     'verification_link': verification_link
            # })

            # to_email = email

            # send_mail(
            #     mail_subject,
            #     message,
            #     EMAIL_HOST_USER,
            #     [to_email],
            #     fail_silently=False,
            #     html_message=message
            # )

            # login_url = reverse('login')
            # login_url += '?message=Email+Verification+Pending'

            return redirect('login')

    return render(request, "accounts/sign-up.html", context)


# def activate_account(request, uidb64, token):

#     context = {
#         "page_title": "Activation Status"
#     }

#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)

#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user is not None and default_token_generator.check_token(user, token):

#         user.is_active = True
#         user.save()

#         context["status"] = "Activation Success"
#         context["message"] = "Your account has been successfully activated. You can now log in to your account."

#         return render(request, "accounts/account-activation-status.html", context)

#     else:
#         context["status"] = "Activation Failed"
#         context["message"] = "Sorry, the activation link is invalid or expired. Please contact support for assistance."

#         return render(request, "accounts/account-activation-status.html", context)


def logout(request):
    auth_logout(request)
    return redirect('dashboard')
