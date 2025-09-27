from django.contrib import admin
from .models import Status, Pump, Valve, Filter, MixTank, CommandCenter, Misc

# Tell the Django admin to create an interface for each of our models
admin.site.register(Status)
admin.site.register(Pump)
admin.site.register(Valve)
admin.site.register(Filter)
admin.site.register(MixTank)
admin.site.register(CommandCenter)
admin.site.register(Misc)