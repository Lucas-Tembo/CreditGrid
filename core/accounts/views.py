from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile
# Create your views here.
def signup(request):
    if request.method == 'POST':
         form = UserCreationForm(request.POST)
         if form.is_valid():
             user = form.save()
             login(request,user)
             return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request,'accounts/signup.html',{'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
             return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request,'accounts/login.html', {'form':form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('homepage')

@login_required
@login_required
def profile_view(request):
    user = request.user

    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated profile
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')  # or wherever you want
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})