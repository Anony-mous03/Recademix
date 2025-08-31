from django.shortcuts import render, redirect
from .models import ContactForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from videos.models import UserCourse
from .models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')
def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        ContactForm.objects.create(name = name, email = email, message = message)

        messages.info(request, "Your message has been successfully sent!")
        return redirect(home)
    
    return render(request, 'contact.html')
def signup(request):
    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']
        location = request.POST.get('location', '')
        avatar = request.FILES.get('avatar')
        
        # authenticate
        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')
        # unique user
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken")
            return redirect('signup')
        
        user = User.objects.create_user(
            first_name=firstname,
            last_name=lastname,
            username=username,
            email=email,
            password=pass1,
        )
        
        # FIXED: Use defaults parameter for non-lookup fields
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'location': location,
            }
        )
        
        if avatar:
            profile.avatar = avatar
            profile.save()

        login(request, user)
        messages.success(request, "Your account has been successfully created.")
        messages.info(request, "Register your courses to get started.")
        return redirect('course_registration')
        
    return render(request, 'register.html')
def signin(request):
    from django.contrib import messages
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful!")
            return redirect('home')
        else:
            messages.success(request, "Invalid Username or Password.")
            return redirect('signin')
    return render(request, 'login.html')
def signout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('signin')

@login_required
def profile(request):
    """Enhanced user profile view with comprehensive statistics"""
    user = request.user
    
    # Course Statistics
    enrolled_courses = UserCourse.objects.filter(user=user)
    enrolled_courses_count = enrolled_courses.count()
        
    # Profile Completion Percentage
    profile_fields = [
        user.first_name, user.last_name, user.email,
        user.profile.avatar, user.profile.location
    ]
    completed_fields = sum(1 for field in profile_fields if field)
    profile_completion = round((completed_fields / len(profile_fields)) * 100)
    
    context = {
        'enrolled_courses_count': enrolled_courses_count,
        'profile_completion': profile_completion,
        'member_since': user.date_joined,
        'last_login': user.last_login,
    }
    
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    user = request.user

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        location = request.POST.get('location', '').strip()
        avatar = request.FILES.get('avatar')

        # Validation
        if not username:
            messages.error(request, "Username is required.")
            return redirect('edit_profile')
        
        if not email:
            messages.error(request, "Email is required.")
            return redirect('edit_profile')

        # Check for duplicates
        if User.objects.exclude(pk=user.pk).filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('edit_profile.html')

        if User.objects.exclude(pk=user.pk).filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect('edit_profile')

        # Update user information
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Update profile information
        profile = user.profile
        profile.location = location
        if avatar:
            profile.avatar = avatar
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'edit-profile.html')