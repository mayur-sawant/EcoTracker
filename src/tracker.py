class EcoTracker:

    def __init__(
        self,
        detector,
        database,
        logger
    ):

        self.detector = detector

        self.database = database

        self.logger = logger


    def analyze(
        self,
        image_path,
        latitude=None,
        longitude=None
    ):

        self.logger.log(
            "Starting animal identification."
        )


        # ------------------------------------------
        # IDENTIFY SPECIES
        # ------------------------------------------

        species = self.detector.detect(
            image_path
        )


        common_name = species[
            "common_name"
        ]

        scientific_name = species[
            "scientific_name"
        ]

        confidence = species[
            "confidence"
        ]


        self.logger.log(
            f"Detected species: {common_name}"
        )


        # ------------------------------------------
        # IUCN LOOKUP
        # ------------------------------------------

        record = self.database.find_species(

            scientific_name=scientific_name,

            common_name=common_name

        )


        if record is not None:

            status = record[
                "Conservation_Status"
            ]

            population = record[
                "Global_Population"
            ]

        else:

            status = "Not Found"

            population = "Not Available"


        # ------------------------------------------
        # LOCATION
        # ------------------------------------------

        location = None

        if (
            latitude is not None
            and longitude is not None
        ):

            location = {
                "latitude": latitude,
                "longitude": longitude
            }


        # ------------------------------------------
        # LOG RESULT
        # ------------------------------------------

        self.logger.log(
            f"Conservation status: {status}"
        )

        self.logger.log(
            f"Global population: {population}"
        )


        self.logger.log(
            "Analysis completed."
        )


        return {

            "common_name": common_name,

            "scientific_name": scientific_name,

            "confidence": confidence,

            "status": status,

            "population": population,

            "location": location

        }