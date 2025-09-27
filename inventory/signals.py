from .models import LogEntry


def store_old_instance_on_save(sender, instance, **kwargs):
    """
    Before a model is saved, this function runs.
    """
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass


def log_item_change(sender, instance, created, **kwargs):
    """
    After a model is saved, this function runs.
    """
    user = getattr(instance, 'updated_by', None)

    if created:
        action = "Created"
        details = f"New item added to category '{instance.get_category_display()}'."
    else:
        action = "Updated"
        details = "Item was updated, but no specific changes were tracked."

        if hasattr(instance, '_old_instance'):
            old_instance = instance._old_instance
            changed_fields = []

            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name)
                new_value = getattr(instance, field_name)

                if old_value != new_value and field_name != 'last_updated':
                    verbose_name = field.verbose_name.capitalize()
                    changed_fields.append(f"{verbose_name} from '{old_value}' to '{new_value}'")

            if changed_fields:
                details = "; ".join(changed_fields)
            else:
                return

    LogEntry.objects.create(
        user=user,
        action=action,
        item_id_str=instance.item_id,
        details=details
    )