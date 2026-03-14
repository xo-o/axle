"""Image generation using Gemini."""
import os
from enum import Enum
from google import genai
from google.genai import types
from PIL import Image
import io


class AspectRatioType(str, Enum):
    ONE = '1:1'
    NINE_SIXTEEN = '9:16'
    SIXTEEN_NINE = '16:9'


class ImageGenerator:
    def __init__(self, api_key: str, model: str = "gemini-3.1-flash-image-preview"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_to_file(self, prompt: str, output_path: str, aspect_ratio: AspectRatioType = AspectRatioType.NINE_SIXTEEN):
        """Generate an image from a prompt and save it to a file using PIL."""
        # Append aspect ratio hint to prompt
        full_prompt = f"{prompt}. Aspect ratio: {aspect_ratio.value}."

        response = self.client.models.generate_content(
            model=self.model,
            contents=[full_prompt],
        )

        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                image.save(output_path)
                return True
        
        return False
