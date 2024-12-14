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
    """
    Logs out the currently logged-in user and redirects them to the home page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponseRedirect: Redirect to the home page.
    """
    logout(request)
    return redirect('home')


def signup(request):
    """
    Handles user registration. Creates a new user if the form is valid.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Renders the signup page with the registration form.
        HttpResponseRedirect: Redirects to the board page after successful registration.
    """
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
    """
    Renders the home page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Renders the home.html template.
    """
    return render(request, 'home.html')


def advertisement_list(request):
    """
    Displays a paginated list of active advertisements.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Renders the adv_list.html template with paginated advertisements.
    """
    adv_list = Advertisement.objects.filter(completed=False, deleted=False)
    for ad in adv_list:
        ad.like_count = ad.likes.count()
        ad.dislike_count = ad.dislikes.count()
    page = request.GET.get('page', 1)
    paginator = Paginator(adv_list, 12)

    try:
        adv = paginator.page(page)
    except PageNotAnInteger:
        adv = paginator.page(1)
    except EmptyPage:
        adv = paginator.page(paginator.num_pages)
    return render(request, 'board/adv_list.html', {'adv': adv})


@login_required
def advertisement_detail(request, pk):
    """
    Displays the details of an advertisement or redirects to the edit page if the user is the author.

    Args:
        request (HttpRequest): The request object.
        pk (int): The primary key of the advertisement.

    Returns:
        HttpResponse: Renders the adv_detail.html template.
        HttpResponseRedirect: Redirects to the edit_adv page if the user is the author.
    """
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.user == adv.author:
        return redirect('AdvBoard:edit_adv', pk=pk)
    return render(request, 'board/adv_detail.html', {
        'adv': adv,
        'photos': [adv.photo1, adv.photo2, adv.photo3, adv.photo4],
    })


@login_required
def add_advertisement(request):
    """
    Handles the creation of a new advertisement. Validates form data and uploads photos.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Renders the add_adv.html template with the advertisement form.
        HttpResponseRedirect: Redirects to the my_ads page after successful creation.
    """
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
    """
    Handles editing an existing advertisement. Allows the user to update details and photos.

    Args:
        request (HttpRequest): The request object.
        pk (int): The primary key of the advertisement to edit.

    Returns:
        HttpResponse: Renders the edit_adv.html template with the advertisement form and photos.
        HttpResponseRedirect: Redirects to the adv_detail page after successful editing.
    """
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
                    print('We are here')
                    existing_photo = getattr(adv, photo_field)
                    if request.POST.get(f'clear_{photo_field}'):
                        setattr(adv, photo_field, None)
                    elif not existing_photo:
                        setattr(adv, photo_field, None)
            adv.save()
            return redirect('AdvBoard:adv_list')
    else:
        form = AdvertisementForm(instance=adv)
    photos = [adv.photo1, adv.photo2, adv.photo3, adv.photo4]
    return render(request, 'board/edit_adv.html', {'form': form, 'adv': adv, 'photos': photos})


@login_required
def activate_advertisement(request, pk):
    """
    Reactivates a previously completed or deleted advertisement.

    Args:
        request (HttpRequest): The request object.
        pk (int): The primary key of the advertisement to activate.

    Returns:
        HttpResponseRedirect: Redirects to the my_ads or adv_detail page.
    """
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
    """
    Marks an advertisement as deleted without actually removing it from the database.

    Args:
        request (HttpRequest): The request object.
        pk (int): The primary key of the advertisement to delete.

    Returns:
        HttpResponseRedirect: Redirects to the my_ads or adv_detail page.
    """
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
    """
    Permanently deletes an advertisement from the database.

    Args:
        request (HttpRequest): The request object.
        pk (int): The primary key of the advertisement to delete.

    Returns:
        HttpResponseRedirect: Redirects to the my_ads page.
    """
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.method == "POST":
        adv.delete()
        return redirect('AdvBoard:my_ads')
    return redirect('AdvBoard:adv_detail', pk=pk)


@login_required
def complete_advertisement(request, pk):
    """
    Marks an advertisement as completed.

    Args:
        request (HttpRequest): The request object.
        pk (int): The primary key of the advertisement to mark as completed.

    Returns:
        HttpResponseRedirect: Redirects to the my_ads or adv_detail page.
    """
    adv = get_object_or_404(Advertisement, pk=pk)
    if request.method == "POST":
        adv.completed = True
        adv.completed_at = now()
        adv.save()
        return redirect('AdvBoard:my_ads')
    return redirect('AdvBoard:adv_detail', pk=pk)


@login_required
def my_advertisements(request):
    """
    Displays a paginated list of advertisements created by the logged-in user.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Renders the my_ads.html template with paginated advertisements.
    """
    ads = Advertisement.objects.filter(author=request.user)
    paginator = Paginator(ads, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    active_tab = 'my_ads'
    sub_tab = request.GET.get('filter', 'active')
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
    """
    Handles voting (like/dislike) for an advertisement. Updates the like/dislike counters.

    Args:
        request (HttpRequest): The request object.
        pk (int): The primary key of the advertisement.
        action (str): The action to perform ('like' or 'dislike').

    Returns:
        JsonResponse: The updated like and dislike counts for the advertisement.
    """
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
