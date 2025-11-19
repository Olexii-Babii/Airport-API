from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=63)
    closest_big_city = models.CharField(max_length=63)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="sources")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="destinations")
    distance = models.IntegerField()

    class Meta:
        ordering = ["source", "destination"]

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"Name: {self.name}, type: {self.airplane_type}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return (f"{self.route} -> {self.airplane}"
                f"departure time: {self.departure_time}"
                f"arrival time: {self.arrival_time}")


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    flights = models.ManyToManyField(Flight, related_name="crews")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in[
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise (
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {airplane_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            row=self.row,
            seat=self.seat,
            airplane=self.flight.airplane,
            error_to_raise=ValidationError
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{self.flight.route}, {self.row} -> {self.seat}"

    class Meta:
        unique_together = ("row", "seat", "flight")
        ordering = ["row", "seat"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Created at: {self.created_at}"