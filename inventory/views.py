from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import BaseItem, LogEntry
from django.db.models import Q
from .forms import (
    PumpForm, ValveForm, FilterForm, MixTankForm, CommandCenterForm, MiscForm
)

FORM_MAP = {
    'pump': PumpForm,
    'valve': ValveForm,
    'filter': FilterForm,
    'mixtank': MixTankForm,
    'commandcenter': CommandCenterForm,
    'misc': MiscForm
}

def item_list(request):
    # Get the search query from the URL's 'q' parameter
    query = request.GET.get('q')

    # Start with all items
    items = BaseItem.objects.all()

    # If a query was provided, filter the items
    if query:
        items = items.filter(
            Q(item_id__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(vendor__icontains=query)
        ).order_by('category', 'item_id')
    else:
        # If no query, just order the full list
        items = items.order_by('category', 'item_id')

    context = {
        'items': items
    }
    return render(request, 'inventory/item_list.html', context)

def item_detail(request, pk):
    # Takes a single item by its primary key and sends it to a detail template
    item = get_object_or_404(BaseItem, pk=pk)
    context = {
        'item': item
    }
    return render(request, 'inventory/item_detail.html', context)

@login_required
def add_item_chooser(request):
    # We get the category choices directly from our BaseItem model
    category_choices = BaseItem.CATEGORY_CHOICES
    context = {
        'categories': category_choices
    }
    return render(request, 'inventory/add_item_chooser.html', context)

@login_required
def add_item(request, category):
    FormClass = FORM_MAP.get(category.lower().replace(' ', ''))

    if FormClass is None:
        return redirect('item_list')

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            # Create the object in memory
            new_item = form.save(commit=False)

            # Set the category from the URL
            new_item.category = category

            # Save the object to database
            new_item.save()

            return redirect('item_list')
    else:
        # Create a blank form
        form = FormClass()

    context = {
        'form': form,
        'category': category.title()
    }
    return render(request, 'inventory/add_item.html', context)

@login_required
def edit_item(request, pk):
    # Get the parent BaseItem object first
    base_item = get_object_or_404(BaseItem, pk=pk)

    # Determine the category and find the correct Form class
    category_slug = base_item.category.lower().replace(' ', '')
    FormClass = FORM_MAP.get(category_slug)

    if FormClass is None:
        return redirect('item_list')

    try:
        child_instance = getattr(base_item, category_slug)
    except AttributeError:
        child_instance = base_item

    if request.method == 'POST':
        # Pass the specific child_instance to the form
        form = FormClass(request.POST, instance=child_instance)
        if form.is_valid():
            form.save()
            return redirect('item_detail', pk=base_item.pk)
    else:
        # Pass the specific child_instance to the form
        form = FormClass(instance=child_instance)

    context = {
        'form': form,
        'category': base_item.category
    }
    return render(request, 'inventory/add_item.html', context)

@login_required
def delete_item(request, pk):
    item = get_object_or_404(BaseItem, pk=pk)

    # When user confirms deletion
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')

    context = {
        'item': item
    }
    return render(request, 'inventory/item_confirm_delete.html', context)

@login_required
def log_history(request):
    logs = LogEntry.objects.all()
    context = {
        'logs': logs
    }
    return render(request, 'inventory/log_history.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('item_list')