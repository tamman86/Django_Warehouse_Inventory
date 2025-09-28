from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import BaseItem, LogEntry, Status
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
    status_filter = request.GET.get('status')

    # Start with all items
    items = BaseItem.objects.all()
    statuses = Status.objects.all().order_by('name')

    # Filter by status if selected
    if status_filter:
        items = items.filter(status__in=status_filter)

    # If a query was provided, filter the items
    if query:
        items = items.filter(
            Q(item_id__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(vendor__icontains=query)
        )

    items = items.order_by('category', 'item_id')

    context = {
        'items': items,
        'statuses': statuses,
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

            # Save user
            new_item.updated_by = request.user

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
            form.instance.updated_by = request.user
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
        LogEntry.objects.create(
            user=request.user,
            action="Deleted",
            item_id_str=item.item_id,
            details=f"Item from category '{item.get_category_display()}' was deleted."
        )
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

@login_required
def manage_statuses(request):
    if request.method == 'POST':
        if 'delete_status' in request.POST:
            status_id = request.POST.get('delete_status')
            status_to_delete = get_object_or_404(Status, id=status_id)
            try:
                status_to_delete.delete()
                messages.success(request, f"Status '{status_to_delete.name}' deleted.")
            except Exception as e:
                messages.error(request, f"Cannot delete status '{status_to_delete.name}' because it is in use.")
        else:
            new_status_name = request.POST.get('name')
            if new_status_name:
                status, created = Status.objects.get_or_create(name=new_status_name)
                if created:
                    messages.success(request, f"Status '{status.name}' added.")
                else:
                    messages.warning(request, f"Status '{status.name}' already exists.")
        return redirect('manage_statuses')

    statuses = Status.objects.all().order_by('name')
    context = {'statuses': statuses}
    return render(request, 'inventory/manage_statuses.html', context)