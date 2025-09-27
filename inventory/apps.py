from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        from django.db.models.signals import post_save, pre_save
        from . import signals
        from .models import Pump, Valve, Filter, MixTank, CommandCenter, Misc

        ITEM_MODELS = [Pump, Valve, Filter, MixTank, CommandCenter, Misc]

        # Loop through all our specific item models and connect the signals
        for model in ITEM_MODELS:
            pre_save.connect(signals.store_old_instance_on_save, sender=model)
            post_save.connect(signals.log_item_change, sender=model)
