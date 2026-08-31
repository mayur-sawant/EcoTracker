def validate_location(
    latitude,
    longitude
):

    if latitude is None or longitude is None:

        return False, "Location not provided."


    if not -90 <= latitude <= 90:

        return False, (
            "Latitude must be between -90 and 90."
        )


    if not -180 <= longitude <= 180:

        return False, (
            "Longitude must be between -180 and 180."
        )


    return True, "Valid location."