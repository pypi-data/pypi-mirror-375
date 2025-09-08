import os
from dataclasses import dataclass, field
from typing import List, Optional, Union

import httpx
from dotenv import load_dotenv
from PIL import Image

from .utils import b64_to_img, img_b64_part, img_to_b64

load_dotenv()


@dataclass
class GemImg:
    api_key: str = field(default=os.getenv("GEMINI_API_KEY"), repr=False)
    client: httpx.Client = field(default_factory=httpx.Client, repr=False)
    model: str = "gemini-2.5-flash-image-preview"

    def __post_init__(self):
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. Pass it as `api_key`, set it as an environment variable or in .env file."
            )

    def generate(
        self,
        prompt: Optional[str] = None,
        imgs: Optional[Union[str, Image.Image, List[str], List[Image.Image]]] = None,
        resize_inputs: bool = True,
        save: bool = True,
        save_dir: str = "",
        temperature: float = 1.0,
        webp: bool = False,
        n: int = 1,
    ) -> Optional["ImageGen"]:
        if not prompt and not imgs:
            raise ValueError("Either 'prompt' or 'imgs' must be provided")

        if n > 1:
            if temperature == 0:
                raise ValueError(
                    "Generating multiple images at temperature = 0.0 is redundant."
                )
            # Exclude 'self' from locals to avoid conflicts when passing as kwargs
            kwargs = {k: v for k, v in locals().items() if k != "self"}
            return self._generate_multiple(**kwargs)

        parts = []

        if imgs:
            # Ensure imgs is a list
            if isinstance(imgs, (str, Image.Image)):
                imgs = [imgs]

            img_b64_strings = [img_to_b64(img, resize_inputs) for img in imgs]
            parts.extend([img_b64_part(b64_str) for b64_str in img_b64_strings])

        if prompt:
            parts.append({"text": prompt.strip()})

        query_params = {
            "generationConfig": {"temperature": temperature},
            "contents": [{"parts": parts}],
        }

        headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

        try:
            response = self.client.post(
                api_url, json=query_params, headers=headers, timeout=120
            )
        except httpx.exceptions.Timeout:
            print("Request Timeout")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return None

        response_data = response.json()
        usage_metadata = response_data["usageMetadata"]

        # Check for prohibited content
        candidates = response_data["candidates"][0]
        finish_reason = candidates.get("finishReason")
        if finish_reason == "PROHIBITED_CONTENT":
            print(f"Image was not generated due to {finish_reason}.")
            return None

        response_parts = candidates["content"]["parts"]

        output_texts = []
        output_images = []

        # Parse response parts for text and images
        for part in response_parts:
            if "text" in part:
                output_texts.append(part["text"])
            elif "inlineData" in part:
                output_images.append(b64_to_img(part["inlineData"]["data"]))

        output_image_paths = []
        if save:
            response_id = response_data["responseId"]
            file_extension = "webp" if webp else "png"
            if len(output_images) == 1:
                image_path = f"{response_id}.{file_extension}"
                output_images[0].save(os.path.join(save_dir, image_path))
                output_image_paths.append(image_path)
            elif len(output_images) > 1:
                for idx, img in enumerate(output_images):
                    image_path = f"{response_id}-{idx}.{file_extension}"
                    img.save(os.path.join(save_dir, image_path))
                    output_image_paths.append(image_path)

        return ImageGen(
            texts=output_texts,
            images=output_images,
            image_paths=output_image_paths,
            usages=[
                Usage(
                    prompt_tokens=usage_metadata.get("promptTokenCount", -1),
                    completion_tokens=usage_metadata.get("candidatesTokenCount", -1),
                )
            ],
        )

    def _generate_multiple(self, n: int, **kwargs) -> "ImageGen":
        """Helper to generate multiple images by accumulating results."""
        n = kwargs.pop("n")
        result = None
        for _ in range(n):
            gen_result = self.generate(n=1, **kwargs)
            if result is None:
                result = gen_result
            else:
                result += gen_result
        return result


@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class ImageGen:
    texts: List[str] = field(default_factory=list)
    images: List[Image.Image] = field(default_factory=list)
    image_paths: List[str] = field(default_factory=list)
    usages: List[Usage] = field(default_factory=list)

    @property
    def image(self) -> Optional[Image.Image]:
        return self.images[0] if self.images else None

    @property
    def image_path(self) -> Optional[str]:
        return self.image_paths[0] if self.image_paths else None

    @property
    def text(self) -> Optional[str]:
        return self.texts[0] if self.texts else None

    @property
    def usage(self) -> Optional[Usage]:
        return self.usages[0] if self.usages else None

    def __add__(self, other: "ImageGen") -> "ImageGen":
        if isinstance(other, ImageGen):
            return ImageGen(
                images=self.images + other.images,
                image_paths=self.image_paths + other.image_paths,
                usages=self.usages + other.usages,
            )
        raise TypeError("Can only add ImageGen instances.")
