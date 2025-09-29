from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import BaseItem, LogEntry, Status, RepairLog
from django.db.models import Q
from django.utils import timezone
from .forms import (
    RepairLogForm, PumpForm, ValveForm, FilterForm, MixTankForm, CommandCenterForm, MiscForm
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
    repair_logs = item.repairs.all()

    context = {
        'item': item,
        'repair_logs': repair_logs,
    }
    return render(request, 'inventory/item_detail.html', context)

@login_required
@permission_required('inventory.add_baseitem', raise_exception=True)
def add_item_chooser(request):
    # We get the category choices directly from our BaseItem model
    category_choices = BaseItem.CATEGORY_CHOICES
    context = {
        'categories': category_choices
    }
    return render(request, 'inventory/add_item_chooser.html', context)

@login_required
@permission_required('inventory.add_baseitem', raise_exception=True)
def add_item(request, category):
    category_slug = category.lower().replace(' ', '')
    FormClass = FORM_MAP.get(category_slug)

    if FormClass is None:
        return redirect('item_list')

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
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
@permission_required('inventory.change_baseitem', raise_exception=True)
def edit_item(request, pk):
    base_item = get_object_or_404(BaseItem, pk=pk)
    category_slug = base_item.category.lower().replace(' ', '')
    ItemFormClass = FORM_MAP.get(category_slug)

    try:
        child_instance = getattr(base_item, category_slug)
    except AttributeError:
        child_instance = base_item

    active_repair = child_instance.repairs.filter(is_active=True).first()

    if request.method == 'POST':
        item_form = ItemFormClass(request.POST, request.FILES, instance=child_instance)
        repair_form = RepairLogForm(request.POST, request.FILES, prefix='repair', instance=active_repair)

        if item_form.is_valid():
            new_status = item_form.cleaned_data.get('status')

            if new_status and new_status.name == 'Repair':
                if repair_form.is_valid():
                    item_form.instance.updated_by = request.user
                    updated_item = item_form.save()

                    repair_log = repair_form.save(commit=False)
                    repair_log.item = updated_item
                    repair_log.is_active = True
                    repair_log.save()

                    log_action = "Repair Updated"
                    if not active_repair:  # If there was no active repair before, this is a new one
                        log_action = "Repair Started"

                    LogEntry.objects.create(
                        user=request.user,
                        action=log_action,
                        item_id_str=updated_item.item_id,
                        details=f"Company: {repair_log.repair_company}, Cost: ${repair_log.cost or 'N/A'}"
                    )

                    messages.success(request, f"Item '{updated_item.item_id}' updated and repair log saved.")
                    return redirect('item_detail', pk=base_item.pk)

            else:
                item_form.instance.updated_by = request.user
                item_form.save()
                messages.success(request, f"Item '{item_form.instance.item_id}' was updated successfully.")
                return redirect('item_detail', pk=base_item.pk)

    else:
        item_form = ItemFormClass(instance=child_instance)
        repair_form = RepairLogForm(prefix='repair', instance=active_repair)

    context = {
        'form': item_form,
        'repair_form': repair_form,
        'item': base_item,
    }
    return render(request, 'inventory/edit_item.html', context)

@login_required
@permission_required('inventory.delete_baseitem', raise_exception=True)
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
@permission_required('inventory.add_status', raise_exception=True)
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


@login_required
@permission_required('inventory.change_repairlog', raise_exception=True)
def complete_repair(request, pk):
    repair_log = get_object_or_404(RepairLog, pk=pk)
    item = repair_log.item

    if request.method == 'POST':
        repair_log.is_active = False
        repair_log.end_date = timezone.now().date()
        repair_log.save()

        LogEntry.objects.create(
            user=request.user,
            action="Repair Completed",
            item_id_str=item.item_id,
            details=f"Repair by {repair_log.repair_company} marked as complete."
        )

        try:
            warehouse_status = Status.objects.get(name="Warehouse")
            item.status = warehouse_status
            item.updated_by = request.user
            item.save()
            messages.success(request, f"Repair for {item.item_id} has been marked as complete.")
        except Status.DoesNotExist:
            messages.error(request, "CRITICAL: The 'Warehouse' status does not exist. Please create it.")

        return redirect('item_detail', pk=item.pk)

    return redirect('item_detail', pk=item.pk)