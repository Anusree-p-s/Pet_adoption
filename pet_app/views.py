from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from .models import Pet, AdoptionRequest
from .forms import PetForm
from django.contrib.auth.models import User

# Home page
from django.shortcuts import render, redirect

def home(request):
    """
    Home page:
    - Redirect logged-in users to expanded_home
    - Show landing page to anonymous users
    """
    if request.user.is_authenticated:
        return redirect('expanded_home')
    return render(request, 'home.html')


# Explore / Expanded home (all pets)
@login_required
def expanded_home(request):
    query = request.GET.get('q', '')  # get the search term

    if query:
        pets = Pet.objects.filter(
            Q(name__icontains=query) |
            Q(breed__icontains=query) |
            Q(category__icontains=query)
        ).order_by('-id')
    else:
        pets = Pet.objects.all().order_by('-id')

    user_pets = Pet.objects.filter(owner=request.user)

    return render(request, "pets/expanded_home.html", {
        "pets": pets,
        "user_pets": user_pets,
        "query": query  # send query to template to retain input value
    })

# My Pets (user-specific)
@login_required
def my_pets(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, "pets/my_pets.html", {"pets": pets})

# Pet details
def pet_details(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return render(request, "pets/pet_details.html", {"pet": pet})

# Signup
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# Login
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.POST.get('next') or reverse('expanded_home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    next_url = request.GET.get('next', '')
    return render(request, "registration/login.html", {"form": form, "next": next_url})

# Adopt pet
@login_required
def adopt_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if not pet.available:
        messages.error(request, "Sorry, this pet has already been adopted.")
        return redirect('pet_details', pet_id=pet.id)

    if AdoptionRequest.objects.filter(user=request.user, pet=pet).exists():
        messages.warning(request, "You have already requested to adopt this pet.")
        return redirect('pet_details', pet_id=pet.id)

    AdoptionRequest.objects.create(user=request.user, pet=pet)
    messages.success(request, f"You have requested to adopt {pet.name}!")
    return redirect('home')

# User dashboard (adoption requests)
@login_required
def dashboard(request):
    total_pets = Pet.objects.count()
    available_pets = Pet.objects.filter(available=True).count()
    adopted_pets = Pet.objects.filter(available=False).count()

    context = {
        'total_pets': total_pets,
        'available_pets': available_pets,
        'adopted_pets': adopted_pets,
    }
    return render(request, 'pets/dashboard.html',context)

# Adoption info
def adoption_info(request):
    query = request.GET.get('q', '')

    if query:
        pets = Pet.objects.filter(
            Q(name__icontains=query) |
            Q(breed__icontains=query) |
            Q(category__icontains=query)
        )
    else:
        pets = Pet.objects.all()
    return render(request, "pets/adoption_info.html",{
        'pets':pets,
        'query':query
    })


# Add pet
@login_required
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.available=True 
            pet.save()
            messages.success(request, f"{pet.name} has been added successfully!")
            return redirect('expanded_home')
    else:
        form = PetForm()
    return render(request, 'pets/add_pet.html', {'form': form})

@login_required
def edit_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('expanded_home')
    else:
        form = PetForm(instance=pet)
    return render(request, 'pets/edit_pet.html', {'form': form, 'pet': pet})

@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    pet.delete()
    messages.success(request, f'{pet.name} has been deleted successfully.')
    return redirect('expanded_home')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

@login_required
def admin_requests(request):
    if not request.user.is_staff:
        return redirect('expanded_home')
    requests = AdoptionRequest.objects.all()
    return render(request, 'pets/admin_requests.html', {'requests': requests})

@login_required
def update_request(request, request_id, status):
    if not request.user.is_staff:
        return redirect('expanded_home')
    adoption_request = get_object_or_404(AdoptionRequest, id=request_id)
    adoption_request.status = status
    adoption_request.save()
    if status == 'Approved':
        adoption_request.pet.available = False
        adoption_request.pet.save()
    return redirect('admin_requests')

@login_required
def my_requests(request):
    """
    View all adoption requests submitted by the logged-in user.
    """
    requests = AdoptionRequest.objects.filter(user=request.user).order_by('-request_date')
    return render(request, 'pets/my_requests.html', {'requests': requests})

@login_required
def my_adopted_pets(request):
    # Filter only "Approved" adoption requests by the current user
    adopted_requests = AdoptionRequest.objects.filter(user=request.user, status="Approved")
    adopted_pets = [req.pet for req in adopted_requests]  # Extract pets
    return render(request, "pets/my_adopted_pets.html", {"adopted_pets": adopted_pets})

@login_required
def owner_requests(request):
    """
    Show all adoption requests for pets owned by the current user.
    Optionally filter by a specific pet via GET parameter 'pet_id'.
    """
    pets = Pet.objects.filter(owner=request.user)
    pet_id = request.GET.get('pet_id')

    if pet_id:
        requests = AdoptionRequest.objects.filter(pet__owner=request.user, pet_id=pet_id, status='Pending')
    else:
        requests = AdoptionRequest.objects.filter(pet__in=pets, status='Pending')

    return render(request, 'pets/owner_requests.html', {'requests': requests})


@login_required
def update_request(request, request_id, status):
    """
    Owner approves or rejects a pet adoption request
    """
    adoption_request = get_object_or_404(AdoptionRequest, id=request_id)

    
    if adoption_request.pet.owner != request.user:
        messages.error(request, "You are not authorized to update this request.")
        return redirect('owner_requests')

    adoption_request.status = status
    adoption_request.save()

    if status == 'Approved':
        adoption_request.pet.available = False
        adoption_request.pet.save()
        AdoptionRequest.objects.filter(pet=adoption_request.pet).exclude(id=request_id).update(status='Rejected')

    messages.success(request, f"Request has been {status}.")
    return redirect('owner_requests')


