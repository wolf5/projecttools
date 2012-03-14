from models import Customer
from models import Entry
from django.contrib import admin

class OwnEntryAdmin(admin.ModelAdmin):
    def queryset(self, request):
        originalQuerySet = super(OwnEntryAdmin, self).queryset(request)
        
        if request.user.is_superuser:
            return originalQuerySet
        else:
            filteredQuerySet = originalQuerySet.filter(owner = request.user)
            return filteredQuerySet

admin.site.register(Customer)
admin.site.register(Entry, OwnEntryAdmin)
