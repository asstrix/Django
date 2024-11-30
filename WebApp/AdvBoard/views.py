from django.shortcuts import render, redirect
from AdvBoard.models import Advertisement
from AdvBoard.forms import AdvertisementForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .forms import SignUpForm
from django.contrib.auth import login, authenticate


def logout_view(request):
    logout(request)
    return redirect('home')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/board')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def home(request):
    return render(request, 'home.html')


def advertisement_list(request):
    advertisements = Advertisement.objects.all()
    return render(request, 'board/advertisement_list.html', {'advertisements': advertisements})


def advertisement_detail(request, pk):
    advertisement = get_object_or_404(Advertisement, pk=pk)
    return render(request, 'board/advertisement_detail.html', {'advertisement': advertisement})


@login_required
def add_advertisement(request):
    if request.method == "POST":
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.author = request.user
            for i in range(1, 5):
                photo = request.FILES.get(f'photo{i}')
                if photo:
                    if not photo.content_type.startswith('image/'):
                        form.add_error(None, f"Photo {i} must be an image file.")
                        return render(request, 'board/add_advertisement.html', {'form': form})
                    if photo.size > 5 * 1024 * 1024:  # 5 MB
                        form.add_error(None, f"Photo {i} exceeds 5MB size limit.")
                        return render(request, 'board/add_advertisement.html', {'form': form})
                    setattr(advertisement, f'photo{i}', photo.read())
            advertisement.save()
            return redirect('board:advertisement_list')
    else:
        form = AdvertisementForm()
    return render(request, 'board/add_advertisement.html', {'form': form})


def edit_advertisement(request, pk):
    advertisement = get_object_or_404(Advertisement, pk=pk)
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=advertisement)
        if form.is_valid():
            for i in range(1, 5):
                photo = request.FILES.get(f'photo{i}')
                if photo:
                    if not photo.content_type.startswith('image/'):
                        form.add_error(None, f"Photo {i} must be an image file.")
                        return render(request, 'board/edit_adv.html', {'form': form, 'advertisement': advertisement})
                    if photo.size > 5 * 1024 * 1024:  # 5 MB
                        form.add_error(None, f"Photo {i} exceeds 5MB size limit.")
                        return render(request, 'board/edit_adv.html', {'form': form, 'advertisement': advertisement})
                    setattr(advertisement, f'photo{i}', photo.read())
            advertisement.save()
            return redirect('AdvBoard:advertisement_detail', pk=pk)
    else:
        form = AdvertisementForm(instance=advertisement)
    return render(request, 'board/edit_adv.html', {'form': form, 'advertisement': advertisement})


def delete_advertisement(request, pk):
    if request.method == "POST":
        advertisement = get_object_or_404(Advertisement, pk=pk)
        advertisement.delete()
        return redirect('board:advertisement_list')
    return redirect('board:advertisement_detail', pk=pk)