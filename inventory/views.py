from django.shortcuts import render, get_object_or_404, redirect
from .models import BaseItem
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

def add_item_chooser(request):
    # We get the category choices directly from our BaseItem model
    category_choices = BaseItem.CATEGORY_CHOICES
    context = {
        'categories': category_choices
    }
    return render(request, 'inventory/add_item_chooser.html', context)

def add_item(request, category):
    # Look up the correct form class from the FORM_MAP
    FormClass = FORM_MAP.get(category.lower().replace(' ', ''))

    # If the category is invalid we want to redirect
    if FormClass is None:
        return redirect('item_list')

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = FormClass(initial={'category': category.title()})

    context = {
        'form': form,
        'category': category.title()
    }
    return render(request, 'inventory/add_item.html', context)


def edit_item(request, pk):
    # Get item to edit
    item = get_object_or_404(BaseItem, pk=pk)

    # Determine the correct form based on the item's category
    category_slug = item.category.lower().replace(' ', '')
    FormClass = FORM_MAP.get(category_slug)

    if FormClass is None:
        # Handle cases where the category might not be in our map
        return redirect('item_list')

    if request.method == 'POST':
        # Pass the submitted data AND the specific item instance to the form
        form = FormClass(request.POST, instance=item)
        if form.is_valid():
            form.save()
            # Redirect to the detail page of the item that was just edited
            return redirect('item_detail', pk=item.pk)
    else:
        # On a GET request, create a form pre-populated with the item's data
        form = FormClass(instance=item)

    context = {
        'form': form,
        'category': item.category
    }
    # We can reuse the same template we use for adding an item!
    return render(request, 'inventory/add_item.html', context)


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