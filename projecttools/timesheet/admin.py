from models import Customer
from models import Entry
from django.contrib import admin
from projecttools.me.helpers import isSubscriptionValid

class EntryAdmin(admin.ModelAdmin):
    """
    Shows only the timesheet entries that belong to the current user.
    Restricts access if the subscription is no longer valid.
    """
    def queryset(self, request):
        originalQuerySet = super(EntryAdmin, self).queryset(request)
        
        if request.user.is_superuser:
            return originalQuerySet
        else:
            filteredQuerySet = originalQuerySet.filter(owner = request.user)
            return filteredQuerySet
    
    def has_add_permission(self, request):
        return isSubscriptionValid(request.user) and super(EntryAdmin, self).has_add_permission(request)
    
    def has_change_permission(self, request, obj = None):
        return isSubscriptionValid(request.user) and super(EntryAdmin, self).has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj = None):
        return isSubscriptionValid(request.user) and super(EntryAdmin, self).has_delete_permission(request, obj)
admin.site.register(Entry, EntryAdmin)

class CustomerAdmin(admin.ModelAdmin):
    def has_add_permissions(self, request):
        return True
    
    def has_change_permissions(self, request, obj = None):
        return True
    
    def has_delete_permissions(self, request, obj = None):
        return True
admin.site.register(Customer, CustomerAdmin)
