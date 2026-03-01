from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Q
from .models import Photo
from .forms import PhotoUploadForm, RegisterForm


def photo_list(request):
    """Main page: list all photos, sortable by name or date."""
    sort = request.GET.get('sort', 'name')
    search = request.GET.get('search', '').strip()

    photos = Photo.objects.select_related('owner').all()

    if search:
        photos = photos.filter(name__icontains=search)

    if sort == 'date_asc':
        photos = photos.order_by('upload_date')
    elif sort == 'date_desc':
        photos = photos.order_by('-upload_date')
    elif sort == 'name_desc':
        photos = photos.order_by('-name')
    else:  # default: name ascending
        photos = photos.order_by('name')

    return render(request, 'photos/list.html', {
        'photos': photos,
        'sort': sort,
        'search': search,
    })


def photo_detail(request, pk):
    """Show a single photo with its details."""
    photo = get_object_or_404(Photo, pk=pk)
    return render(request, 'photos/detail.html', {'photo': photo})


@login_required
def photo_upload(request):
    """Upload a new photo. Only for logged-in users."""
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.owner = request.user
            photo.save()
            messages.success(request, f'Photo "{photo.name}" uploaded successfully!')
            return redirect('photo_detail', pk=photo.pk)
    else:
        form = PhotoUploadForm()

    return render(request, 'photos/upload.html', {'form': form})


@login_required
def photo_delete(request, pk):
    """Delete a photo. Only the owner or staff can delete."""
    photo = get_object_or_404(Photo, pk=pk)

    # Only owner or staff can delete
    if photo.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this photo.')
        return redirect('photo_detail', pk=pk)

    if request.method == 'POST':
        photo_name = photo.name
        # Delete the actual image file
        try:
            photo.image.delete(save=False)
        except Exception:
            pass
        photo.delete()
        messages.success(request, f'Photo "{photo_name}" deleted successfully.')
        return redirect('photo_list')

    return render(request, 'photos/delete_confirm.html', {'photo': photo})


def register(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('photo_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('photo_list')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})
