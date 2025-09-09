import os
import requests

from PIL import Image
from io import BytesIO
from together import Together

class VisionManager:

    async def generate_and_save_image(self, prompt: str, output_path: str) -> str:
        """Generate an image using Together AI/Flux Model and save it to the specified path."""

        api_key = os.environ.get('TOGETHER_API_KEY')
        if not api_key:
            raise ValueError("TOGETHER_API_KEY environment variable not set.")

        client = Together(api_key=api_key)

        try:
            # Generate the image
            response = client.images.generate(
                prompt=prompt,
                width=1024,
                height=1024,
                steps=4,
                model="black-forest-labs/FLUX.1-schnell-Free",
                n=1,
            )
        except Exception as e:
            raise ValueError(f"Failed to generate image: {str(e)}")

        image_url = response.data[0].url

        # Download the image
        try:
            response = requests.get(image_url)
            if response.status_code != 200:
                raise ValueError(f"Failed to download generated image: HTTP {response.status_code}")
        except requests.RequestException as e:
            raise ValueError(f"Network error downloading image: {str(e)}")

        # Save the image
        try:
            image = Image.open(BytesIO(response.content))
            # Ensure the save directory exists
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            except OSError as e:
                raise ValueError(f"Failed to create a directory for image: str({e})")
            # Save the image
            image.save(output_path)
        except (IOError, OSError) as e:
            raise ValueError(f"Failed to save image to {output_path}: {str(e)}")

        return output_path