from django.contrib import admin

from airport.models import (
    AirplaneType,
    Airport,
    Route,
    Airplane,
    Crew,
    Flight,
    Ticket,
    Order,
)

admin.site.register(AirplaneType)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Airplane)
admin.site.register(Crew)
admin.site.register(Flight)
admin.site.register(Ticket)
admin.site.register(Order)
