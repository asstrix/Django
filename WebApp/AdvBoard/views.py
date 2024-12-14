from AdvBoard.models import Advertisement
from AdvBoard.forms import AdvertisementForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm
from django.contrib.auth import login
from django.utils.timezone import now
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
    adv_list = Advertisement.objects.filter(completed=False, deleted=False)

    # Добавляем подсчет лайков и дизлайков
    for ad in adv_list:
        ad.like_count = ad.likes.count()
        ad.dislike_count = ad.dislikes.count()

    # Пагинация
    page = request.GET.get('page', 1)
    paginator = Paginator(adv_list, 12)  # Показываем 10 объявлений на страницу

    try:
        adv = paginator.page(page)
    except PageNotAnInteger:
        adv = paginator.page(1)
    except EmptyPage:
        adv = paginator.page(paginator.num_pages)

    return render(request, 'board/adv_list.html', {'adv': adv})


@login_required
def advertisement_detail(request, pk):
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.user == adv.author:
        return redirect('AdvBoard:edit_adv', pk=pk)
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
            request.user.advertisements_count += 1
            request.user.save()

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
                photo_field = f'photo{i}'
                photo = request.FILES.get(photo_field)
                if photo:
                    if not photo.content_type.startswith('image/'):
                        form.add_error(None, f"Photo {i} must be an image file.")
                        return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})
                    if photo.size > 5 * 1024 * 1024:  # 5 MB
                        form.add_error(None, f"Photo {i} exceeds 5MB size limit.")
                        return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv})
                    setattr(adv, photo_field, photo.read())
                else:
                    existing_photo = getattr(adv, photo_field)
                    if request.POST.get(f'clear_{photo_field}'):
                        setattr(adv, photo_field, None)
                    elif not existing_photo:
                        setattr(adv, photo_field, None)
            adv.save()
            return redirect('AdvBoard:adv_detail', pk=pk)
    else:
        form = AdvertisementForm(instance=adv)
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
    ads = Advertisement.objects.filter(author=request.user)  # Фильтруем объявления автора

    # Пагинация: 5 объявлений на странице
    paginator = Paginator(ads, 5)  # Показываем 5 объявлений на странице
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    active_tab = 'my_ads'  # Устанавливаем текущую вкладку
    sub_tab = request.GET.get('filter', 'active')

    # Подсчёт активных, завершённых и удалённых объявлений
    active_count = ads.filter(completed=False, deleted=False).count()
    completed_count = ads.filter(completed=True).count()
    deleted_count = ads.filter(deleted=True).count()

    return render(request, 'my_ads.html', {
        'ads': page_obj,
        'active_tab': active_tab,
        'sub_tab': sub_tab,
        'active_count': active_count,
        'completed_count': completed_count,
        'deleted_count': deleted_count,
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
