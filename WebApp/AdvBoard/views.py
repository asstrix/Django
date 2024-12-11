from AdvBoard.models import Advertisement
from AdvBoard.forms import AdvertisementForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm
from django.contrib.auth import login
from django.utils.timezone import now
from django.http import JsonResponse


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
    adv = Advertisement.objects.filter(completed=False, deleted=False)
    for ad in adv:
        ad.like_count = ad.likes.count()
        ad.dislike_count = ad.dislikes.count()
    return render(request, 'board/adv_list.html', {'adv': adv})


@login_required
def advertisement_detail(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.user == adv.author:
        return redirect('AdvBoard:my_ads')
    return render(request, 'board/adv_detail.html', {
        'adv': adv,
        'photos': [adv.photo1, adv.photo2, adv.photo3, adv.photo4],
    })


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


# def edit_advertisement(request, pk):
#     adv = get_object_or_404(Advertisement, pk=pk)
#     if request.method == 'POST':
#         form = AdvertisementForm(request.POST, request.FILES, instance=adv)
#         if form.is_valid():
#             for i in range(1, 5):
#                 photo = request.FILES.get(f'photo{i}')
#                 if photo:
#                     if not photo.content_type.startswith('image/'):
#                         form.add_error(None, f"Photo {i} must be an image file.")
#                         return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})
#                     if photo.size > 5 * 1024 * 1024:  # 5 MB
#                         form.add_error(None, f"Photo {i} exceeds 5MB size limit.")
#                         return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})
#                     setattr(adv, f'photo{i}', photo.read())
#             adv.save()
#             return redirect('AdvBoard:adv_detail', pk=pk)
#     else:
#         form = AdvertisementForm(instance=adv)
#     return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})


def edit_advertisement(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=adv)
        if form.is_valid():
            # Обработка новых фотографий и удаления
            for i in range(1, 5):
                photo = request.FILES.get(f'photo{i}')

                if photo:
                    # Проверить тип и размер фото
                    if not photo.content_type.startswith('image/'):
                        form.add_error(None, f"Photo {i} must be an image file.")
                        return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})
                    if photo.size > 5 * 1024 * 1024:  # 5 MB
                        form.add_error(None, f"Photo {i} exceeds 5MB size limit.")
                        return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})

                    # Сохранить фото как FileField-compatible объект
                    setattr(adv, f'photo{i}', photo.read())
                else:
                    # Если поле пустое, удалить фото
                    setattr(adv, f'photo{i}', None)

            # Сохранить изменения в объявлении
            adv.save()
            return redirect('AdvBoard:adv_detail', pk=pk)
    else:
        form = AdvertisementForm(instance=adv)

    # Собрать список фотографий для отображения в шаблоне
    photos = [adv.photo1, adv.photo2, adv.photo3, adv.photo4]
    return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv, 'photos': photos})





@login_required
def activate_advertisement(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.method == "POST":
        adv.completed = False
        adv.deleted = False
        adv.completed_at, adv.deleted_at = None, None
        adv.save()
        return redirect('AdvBoard:my_ads')
    return redirect('AdvBoard:adv_detail', pk=pk)


@login_required
def delete_advertisement(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.method == "POST":
        adv.completed = False
        adv.completed_at = None
        adv.deleted = True
        adv.deleted_at = now()
        adv.save()
        return redirect('AdvBoard:my_ads')
    return redirect('AdvBoard:adv_detail', pk=pk)


@login_required
def delete_completely(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.method == "POST":
        adv.delete()
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


def vote(request, pk, action):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in to like or dislike'}, status=403)
    ad = get_object_or_404(Advertisement, pk=pk)
    if action == 'like':
        if request.user in ad.dislikes.all():
            ad.dislikes.remove(request.user)
        if request.user in ad.likes.all():
            ad.likes.remove(request.user)
        else:
            ad.likes.add(request.user)
    elif action == 'dislike':
        if request.user in ad.likes.all():
            ad.likes.remove(request.user)
        if request.user in ad.dislikes.all():
            ad.dislikes.remove(request.user)
        else:
            ad.dislikes.add(request.user)
    return JsonResponse({
        'likes': ad.likes.count(),
        'dislikes': ad.dislikes.count()
    })
