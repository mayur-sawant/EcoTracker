from pathlib import Path

import pandas as pd


class IUCNDatabase:

    def __init__(self, csv_path):

        self.csv_path = Path(csv_path)

        if not self.csv_path.exists():

            raise FileNotFoundError(
                f"IUCN database not found: {self.csv_path}"
            )

        self.data = pd.read_csv(
            self.csv_path
        )


    def find_species(
        self,
        scientific_name=None,
        common_name=None
    ):

        if scientific_name:

            result = self.data[
                self.data[
                    "Scientific_Name"
                ].str.lower()
                ==
                scientific_name.lower()
            ]

            if not result.empty:

                return result.iloc[0]


        if common_name:

            result = self.data[
                self.data[
                    "Common_Name"
                ].str.lower()
                ==
                common_name.lower()
            ]

            if not result.empty:

                return result.iloc[0]


        return None