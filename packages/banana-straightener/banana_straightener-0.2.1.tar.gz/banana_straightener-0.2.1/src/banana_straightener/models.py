"""Model interfaces and implementations for image generation and evaluation."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai as new_genai
from google.genai import types
import logging
from io import BytesIO

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """Abstract base class for models."""
    
    @abstractmethod
    def generate_image(self, prompt: str, base_images: Optional[List[Image.Image]] = None) -> Image.Image:
        """Generate an image based on prompt. Optionally condition on one or more input images."""
        pass
    
    @abstractmethod
    def evaluate_image(self, image: Image.Image, target_prompt: str) -> Dict[str, Any]:
        """Evaluate if image matches the target prompt."""
        pass

class GeminiModel(BaseModel):
    """Gemini model implementation for generation and evaluation using google.genai."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-image-preview"):
        """Initialize Gemini model client and defaults."""
        self.api_key = api_key
        self.model_name = model_name
        self.client = new_genai.Client(api_key=self.api_key)
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_image(
        self,
        prompt: str,
        base_images: Optional[List[Image.Image]] = None,
        *,
        base_image: Optional[Image.Image] = None,  # backward-compat alias
    ) -> Image.Image:
        """Generate or edit an image using Gemini Image Preview.

        Accepts either a single `base_image` (legacy) or a list `base_images`.
        If both are provided, they will be combined.
        """

        all_images: List[Image.Image] = []
        if base_images:
            all_images.extend(base_images)
        if base_image:
            all_images.append(base_image)

        if all_images:
            logger.info("🖼️ Using %d input image(s)", len(all_images))

        try:
            return self._generate_with_gemini(prompt, all_images if all_images else None)
        except Exception as e:
            logger.error("Generation error: %s", e)
            return self._create_placeholder_image(prompt)
    
    def _generate_with_gemini(self, prompt: str, base_images: Optional[List[Image.Image]] = None) -> Image.Image:
        """Generate or edit image using google.genai."""
        try:
            return self._generate_with_new_api(prompt, base_images)
        except Exception as e:
            logger.error("Gemini generation error: %s", e)
            return self._create_placeholder_image(prompt)
    
    def _generate_with_new_api(self, prompt: str, base_images: Optional[List[Image.Image]] = None) -> Image.Image:
        """Generate or edit image using google.genai client."""
        # Prepare content parts
        parts = []

        # Add text prompt
        if base_images:
            edit_prompt = (
                f"Edit this image: {prompt}. Modify the existing image to match this description "
                f"while preserving its structure and context."
            )
            parts.append(types.Part.from_text(text=edit_prompt))
            logger.debug("Using image edit prompt")
        else:
            parts.append(types.Part.from_text(text=prompt))
            logger.debug("Generating new image from text")

        # Add image(s) if provided
        if base_images:
            for img in base_images:
                img_bytes = BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                parts.append(types.Part.from_bytes(data=img_bytes.read(), mime_type="image/png"))
            logger.info("🖼️ Sending %d input image(s) to API", len(base_images))

        contents = [
            types.Content(
                role="user",
                parts=parts,
            ),
        ]

        config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )

        # Generate and stream response
        for chunk in self.client.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=config,
        ):
            if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                part = chunk.candidates[0].content.parts[0]
                if getattr(part, "inline_data", None) and getattr(part.inline_data, "data", None):
                    image_data = BytesIO(part.inline_data.data)
                    result_image = Image.open(image_data).convert("RGB")
                    logger.info(
                        "✅ Generated image: %sx%s pixels",
                        result_image.size[0],
                        result_image.size[1],
                    )
                    return result_image

        raise RuntimeError("No image data received from Gemini API")
    
    def _generate_fallback(self, prompt: str) -> Image.Image:
        """Fallback method when generation fails."""
        return self._create_placeholder_image(f"Generation failed. Prompt: {prompt}")
    
    def _create_placeholder_image(self, prompt: str) -> Image.Image:
        """Create a placeholder image when generation fails."""
        from PIL import Image, ImageDraw, ImageFont
        
        width, height = 512, 512
        image = Image.new('RGB', (width, height), color='lightgray')
        draw = ImageDraw.Draw(image)
        
        text = f"Failed to generate:\n{prompt[:50]}..."
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        return image
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def evaluate_image(self, image: Image.Image, target_prompt: str, prompt_template: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate if the image matches the target prompt using google.genai."""

        template = prompt_template or (
            "Analyze this image and determine if it successfully shows: \"{target_prompt}\"\n\n"
            "Provide a structured evaluation with SPECIFIC, ACTIONABLE feedback:\n"
            "1. MATCH: Does it match the intent? (YES/NO)\n"
            "2. CONFIDENCE: Rate your confidence from 0.0 to 1.0\n"
            "3. CORRECT_ELEMENTS: List what elements are correctly represented\n"
            "4. MISSING_ELEMENTS: List what's missing or incorrect\n"
            "5. IMPROVEMENTS: Specific improvements needed (CRITICAL: be very detailed and actionable)\n\n"
            "Format your response as:\n"
            "MATCH: [YES/NO]\n"
            "CONFIDENCE: [0.0-1.0]\n"
            "CORRECT_ELEMENTS: [list]\n"
            "MISSING_ELEMENTS: [list]\n"
            "IMPROVEMENTS: [detailed, specific, actionable feedback - never generic]"
        )

        evaluation_prompt = template.format(target_prompt=target_prompt)

        try:
            # Convert image to bytes
            buf = BytesIO()
            image.save(buf, format="PNG")
            buf.seek(0)

            parts = [
                types.Part.from_text(text=evaluation_prompt),
                types.Part.from_bytes(data=buf.read(), mime_type="image/png"),
            ]
            contents = [types.Content(role="user", parts=parts)]

            config = types.GenerateContentConfig(response_modalities=["TEXT"],)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            text = getattr(response, "text", "") or ""
            return self._parse_evaluation(text, target_prompt)
        except Exception as e:
            logger.error("Evaluation error: %s", e)
            return {
                "matches_intent": False,
                "confidence": 0.0,
                "correct_elements": "Error during evaluation",
                "missing_elements": "Unable to analyze",
                "improvements": "Please try again",
                "raw_feedback": f"Evaluation failed: {e}",
            }
    
    @staticmethod
    def _parse_evaluation(response_text: str, target_prompt: str) -> Dict[str, Any]:
        """Parse the evaluation response into structured data."""
        lines = response_text.strip().split('\n')
        evaluation = {
            'matches_intent': False,
            'confidence': 0.0,
            'correct_elements': [],
            'missing_elements': [],
            'improvements': '',
            'raw_feedback': response_text
        }
        
        # Track if we're in multi-line improvements section
        improvements_lines = []
        in_improvements = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('MATCH:'):
                evaluation['matches_intent'] = 'YES' in line.upper()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence_str = line.split(':', 1)[1].strip()
                    confidence_str = confidence_str.replace('%', '')
                    evaluation['confidence'] = min(1.0, max(0.0, float(confidence_str)))
                except (ValueError, IndexError):
                    evaluation['confidence'] = 0.5
            elif line.startswith('CORRECT_ELEMENTS:'):
                evaluation['correct_elements'] = line.split(':', 1)[1].strip()
                in_improvements = False
            elif line.startswith('MISSING_ELEMENTS:'):
                evaluation['missing_elements'] = line.split(':', 1)[1].strip()
                in_improvements = False
            elif line.startswith('IMPROVEMENTS:'):
                improvements_content = line.split(':', 1)[1].strip()
                if improvements_content:
                    improvements_lines.append(improvements_content)
                in_improvements = True
            elif in_improvements and line.startswith('- '):
                # Handle bullet point improvements
                improvements_lines.append(line)
            elif in_improvements and line and not line.startswith(('MATCH:', 'CONFIDENCE:', 'CORRECT_ELEMENTS:', 'MISSING_ELEMENTS:')):
                # Handle continuation of improvements section
                improvements_lines.append(line)
            else:
                in_improvements = False
        
        # Join all improvements
        if improvements_lines:
            evaluation['improvements'] = ' '.join(improvements_lines).strip()
            logger.debug("Parsed improvements: %s...", evaluation['improvements'][:100])
        
        if not evaluation['improvements'] and not evaluation['matches_intent']:
            logger.warning("Evaluator did not provide specific improvements, using fallback")
            evaluation['improvements'] = f"Please regenerate the image to better match: {target_prompt}"
        
        return evaluation
