from django.shortcuts import render, redirect
from AdvBoard.models import Advertisement
from AdvBoard.forms import AdvertisementForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.utils.timezone import now


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
    adv = Advertisement.objects.all()
    return render(request, 'board/adv_list.html', {'adv': adv})


def advertisement_detail(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    photos = [adv.photo1, adv.photo2, adv.photo3, adv.photo4]
    return render(request, 'board/adv_detail.html', {'adv': adv, 'photos': photos})


@login_required
def add_advertisement(request):
    if request.method == "POST":
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            adv = form.save(commit=False)
            adv.author = request.user
            for i in range(1, 5):
                photo = request.FILES.get(f'photo{i}')
                if photo:
                    if not photo.content_type.startswith('image/'):
                        form.add_error(None, f"Photo {i} must be an image file.")
                        return render(request, 'board/add_adv.html', {'form': form})
                    if photo.size > 5 * 1024 * 1024:  # 5 MB
                        form.add_error(None, f"Photo {i} exceeds 5MB size limit.")
                        return render(request, 'board/add_adv.html', {'form': form})
                    setattr(adv, f'photo{i}', photo.read())
            adv.save()
            return redirect('AdvBoard:my_ads')
    else:
        form = AdvertisementForm()
    return render(request, 'board/add_adv.html', {'form': form})


def edit_advertisement(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=adv)
        if form.is_valid():
            for i in range(1, 5):
                photo = request.FILES.get(f'photo{i}')
                if photo:
                    if not photo.content_type.startswith('image/'):
                        form.add_error(None, f"Photo {i} must be an image file.")
                        return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})
                    if photo.size > 5 * 1024 * 1024:  # 5 MB
                        form.add_error(None, f"Photo {i} exceeds 5MB size limit.")
                        return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})
                    setattr(adv, f'photo{i}', photo.read())
            adv.save()
            return redirect('AdvBoard:adv_detail', pk=pk)
    else:
        form = AdvertisementForm(instance=adv)
    return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})


# def delete_advertisement(request, pk):
#     if request.method == "POST":
#         adv = get_object_or_404(Advertisement, pk=pk)
#         adv.delete()
#         return redirect('AdvBoard:adv_list')
#     return redirect('AdvBoard:adv_detail', pk=pk)

@login_required
def delete_advertisement(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.method == "POST":
        adv.deleted = True
        adv.deleted_at = now()
        adv.save()
        return redirect('AdvBoard:my_ads')
    return redirect('AdvBoard:adv_detail', pk=pk)


@login_required
def complete_advertisement(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.method == "POST":
        adv.completed = True
        adv.completed_at = now()
        adv.save()
        return redirect('AdvBoard:my_ads')
    return redirect('AdvBoard:adv_detail', pk=pk)


@login_required
def my_advertisements(request):
    all_ads = Advertisement.objects.filter(author=request.user)
    active_ads = all_ads.filter(completed=False, deleted=False)
    completed_ads = all_ads.filter(completed=True, deleted=False)
    deleted_ads = all_ads.filter(completed=False, deleted=True)
    active_tab = 'my_ads'
    sub_tab = request.GET.get('filter', 'active')
    if sub_tab == 'active':
        ads = active_ads
    elif sub_tab == 'completed':
        ads = completed_ads
    elif sub_tab == 'deleted':
        ads = deleted_ads
    else:
        ads = all_ads
    return render(request, 'my_ads.html', {
        'active_tab': active_tab,
        'sub_tab': sub_tab,
        'ads': ads,
        'active_count': active_ads.count(),
        'completed_count': completed_ads.count(),
        'deleted_count': deleted_ads.count(),
    })