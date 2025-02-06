from drf_spectacular.utils import OpenApiParameter

flight_parameters = [
    OpenApiParameter(
        name="airplane",
        description="ID of an airplane assigned to the flight.",
        type=str,
    ),
    OpenApiParameter(
        name="route",
        description="ID of the flight route.",
        type=int,
    ),
    OpenApiParameter(
        name="crew",
        description="ID of the airplane crew.",
        type=int,
    ),
]
airplane_type_parameters = [
    OpenApiParameter(
        name="type",
        description="Airplane type id.",
        type=int,
    )
]
route_parameters = [
    OpenApiParameter(
        name="source",
        description="Route source ID.",
        type=int,
    ),
    OpenApiParameter(
        name="destination",
        description="Route destination ID.",
        type=int,
    ),
]
