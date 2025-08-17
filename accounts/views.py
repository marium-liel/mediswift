from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from .forms import CustomUserCreationForm, UserProfileForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('products:home')
            except IntegrityError:
                # Handle duplicate username/email
                if 'username' in form.errors:
                    messages.error(request, 'This username is already taken. Please choose a different one.')
                elif 'email' in form.errors:
                    messages.error(request, 'This email is already registered. Please use a different email or try logging in.')
                else:
                    messages.error(request, 'An error occurred while creating your account. Please try again.')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'username':
                        messages.error(request, f'Username: {error}')
                    elif field == 'email':
                        messages.error(request, f'Email: {error}')
                    elif field == 'password1':
                        messages.error(request, f'Password: {error}')
                    elif field == 'password2':
                        messages.error(request, f'Password confirmation: {error}')
                    else:
                        messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('products:home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form}) 