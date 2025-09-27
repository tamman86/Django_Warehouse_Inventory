from django.db import models
from django.contrib.auth.models import User

class BaseItem(models.Model):
    # List of category fields
    CATEGORY_CHOICES = [
        ("Pump", "Pump"),
        ("Filter", "Filter"),
        ("Mix Tank", "Mix Tank"),
        ("Valve", "Valve"),
        ("Command Center", "Command Center"),
        ("Misc", "Misc"),
    ]

    item_id = models.CharField(max_length=100, unique=True, verbose_name="Item ID")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    vendor = models.CharField(max_length=100, blank=True)
    rating = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item_id} ({self.get_category_display()})"

    class Meta:
        ordering = ['item_id']  # Orders items by the Item_ID


# The models inherit all fields from BaseItem and add their own specific attributes

class Pump(BaseItem):
    speed = models.CharField(max_length=50, blank=True)
    inlet = models.CharField(max_length=50, blank=True)
    outlet = models.CharField(max_length=50, blank=True)
    moc = models.CharField(max_length=100, blank=True, verbose_name="Material of Construction")
    power = models.CharField(max_length=50, blank=True)


class Valve(BaseItem):
    moc = models.CharField(max_length=100, blank=True, verbose_name="Material of Construction")
    size = models.CharField(max_length=50, blank=True)
    valve_type = models.CharField(max_length=100, blank=True, verbose_name="Valve Type")


class Filter(BaseItem):
    inlet = models.CharField(max_length=50, blank=True)
    outlet = models.CharField(max_length=50, blank=True)
    moc = models.CharField(max_length=100, blank=True, verbose_name="Material of Construction")
    filter_type = models.CharField(max_length=100, blank=True, verbose_name="Filter Type")


class MixTank(BaseItem):
    inlet = models.CharField(max_length=50, blank=True)
    outlet = models.CharField(max_length=50, blank=True)
    moc = models.CharField(max_length=100, blank=True, verbose_name="Material of Construction")
    power = models.CharField(max_length=50, blank=True)


class CommandCenter(BaseItem):
    # This item has no extra fields beyond the base ones
    pass


class Misc(BaseItem):
    speed = models.CharField(max_length=50, blank=True)
    inlet = models.CharField(max_length=50, blank=True)
    outlet = models.CharField(max_length=50, blank=True)
    moc = models.CharField(max_length=100, blank=True, verbose_name="Material of Construction")
    power = models.CharField(max_length=50, blank=True)
    quantity = models.CharField(max_length=50, blank=True)

class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_log_entries')
    action = models.CharField(max_length=50)
    item_id_str = models.CharField(max_length=100, verbose_name="Item ID")
    details = models.TextField(blank=True)



    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.action} - {self.item_id_str}"

    class Meta:
        ordering = ['-timestamp']  # Show the most recent logs first