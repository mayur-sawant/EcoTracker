from pathlib import Path

import google.generativeai as genai
from PIL import Image


class SpeciesDetector:

    def __init__(self, api_key):

        if not api_key:
            raise ValueError(
                "Gemini API key is missing."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")


    def detect(self, image_path):

        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )


        image = Image.open(image_path)


        prompt = """
You are an expert wildlife identification assistant.

Identify the animal or bird in this image.

Return ONLY the following format:

Common Name: <common name>
Scientific Name: <scientific name>
Confidence: <confidence percentage>

Do not provide explanations.

If the image does not contain an identifiable animal,
return:

Common Name: Unknown
Scientific Name: Unknown
Confidence: 0%
"""


        response = self.model.generate_content(
            contents=[
                prompt,
                image
            ]
        )


        result = response.text.strip()


        return self._parse_result(result)


    def _parse_result(self, result):

        common_name = "Unknown"

        scientific_name = "Unknown"

        confidence = "0%"


        for line in result.splitlines():

            line = line.strip()


            if line.lower().startswith(
                "common name:"
            ):

                common_name = line.split(
                    ":",
                    1
                )[1].strip()


            elif line.lower().startswith(
                "scientific name:"
            ):

                scientific_name = line.split(
                    ":",
                    1
                )[1].strip()


            elif line.lower().startswith(
                "confidence:"
            ):

                confidence = line.split(
                    ":",
                    1
                )[1].strip()


        return {
            "common_name": common_name,
            "scientific_name": scientific_name,
            "confidence": confidence
        }