from django.contrib import admin

from airport.models import (Ticket,
                            Order,
                            Airplane,
                            AirplaneType,
                            Crew,
                            Airport,
                            Route,
                            Flight)


# Register your models here.
class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]

    class Meta:
        model = Order


admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Airplane)
admin.site.register(Flight)
