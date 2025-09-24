from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LogEntry, Pump, Valve, Filter, MixTank, CommandCenter, Misc

ITEM_MODELS = [Pump, Valve, Filter, MixTank, CommandCenter, Misc]

@receiver(post_save, sender=ITEM_MODELS)
def log_item_change(sender, instance, created, **kwargs):
    if created:
        action = "Created"
        details = f"New item '{instance.item_id}' was added to category '{instance.get_category_display()}'."
    else:
        action = "Updated"
        details = f"Item '{instance.item_id}' was updated."

    LogEntry.objects.create(
        action=action,
        item_id_str=instance.item_id,
        details=details
    )

@receiver(post_delete, sender=ITEM_MODELS)
def log_item_deletion(sender, instance, **kwargs):
    LogEntry.objects.create(
        action="Deleted",
        item_id_str=instance.item_id,
        details=f"Item '{instance.item_id}' ({instance.get_category_display()}) was deleted."
    )