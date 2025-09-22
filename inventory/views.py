from django.shortcuts import render, get_object_or_404
from .models import BaseItem

def item_list(request):
    # Grab all items in database and prepare for display
    items = BaseItem.objects.all().order_by('category', 'item_id')
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