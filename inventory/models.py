from django.db import models
from django.contrib.auth.models import User

class Status(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Statuses"

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
    status = models.ForeignKey(Status, on_delete=models.PROTECT, null=True, blank=True)
    datasheet = models.FileField(upload_to='item_documents/', blank=True, null=True, verbose_name="Datasheet")
    manual = models.FileField(upload_to='item_documents/', blank=True, null=True, verbose_name="Manual")
    document1 = models.FileField(upload_to='item_documents/', blank=True, null=True, verbose_name="Document 1")
    document2 = models.FileField(upload_to='item_documents/', blank=True, null=True, verbose_name="Document 2")
    document3 = models.FileField(upload_to='item_documents/', blank=True, null=True, verbose_name="Document 3")
    document4 = models.FileField(upload_to='item_documents/', blank=True, null=True, verbose_name="Document 4")
    document5 = models.FileField(upload_to='item_documents/', blank=True, null=True, verbose_name="Document 5")
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


class RepairLog(models.Model):
    item = models.ForeignKey(BaseItem, on_delete=models.CASCADE, related_name='repairs')

    # Repair Detail Fields
    repair_company = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField(max_length=254, blank=True)
    start_date = models.DateField()
    expected_return_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True, verbose_name="Repair End Date")
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                               verbose_name="Estimated/Final Cost")
    document1 = models.FileField(upload_to='repair_documents/', blank=True, null=True, verbose_name="Document 1")
    document2 = models.FileField(upload_to='repair_documents/', blank=True, null=True, verbose_name="Document 2")
    document3 = models.FileField(upload_to='repair_documents/', blank=True, null=True, verbose_name="Document 3")
    document4 = models.FileField(upload_to='repair_documents/', blank=True, null=True, verbose_name="Document 4")
    document5 = models.FileField(upload_to='repair_documents/', blank=True, null=True, verbose_name="Document 5")

    # Status of the repair itself
    is_active = models.BooleanField(default=True, help_text="Is the repair currently ongoing?")

    def __str__(self):
        status = "Active" if self.is_active else "Complete"
        return f"Repair for {self.item.item_id} ({status})"

    class Meta:
        ordering = ['-start_date']