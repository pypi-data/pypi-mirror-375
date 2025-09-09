"""Core agent for iterative image improvement."""

from typing import Optional, Dict, Any, Generator, Callable, List
from pathlib import Path
from datetime import datetime
import json
import logging
from PIL import Image

from .models import GeminiModel
from .config import Config
from .utils import (
    save_image, 
    create_iteration_report, 
    enhance_prompt_with_feedback,
    create_session_summary,
    sanitize_filename,
    validate_image,
    resize_image_if_needed
)

logger = logging.getLogger(__name__)


class BananaStraightener:
    """Self-correcting image generation agent."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the Banana Straightener agent."""
        self.config = config or Config.from_env()
        
        if not self.config.api_key:
            raise ValueError(
                "API key not found. Please set GEMINI_API_KEY environment variable "
                "or pass it in the configuration."
            )
        
        self.generator = GeminiModel(
            api_key=self.config.api_key,
            model_name=self.config.generator_model
        )
        
        if self.config.evaluator_model == self.config.generator_model:
            self.evaluator = self.generator
        else:
            self.evaluator = GeminiModel(
                api_key=self.config.api_key,
                model_name=self.config.evaluator_model
            )
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.config.output_dir / self.session_id
        self.session_start_time = datetime.now()
        self.session_input_image = None  # Store input image for comparison
        
        if self.config.save_intermediates:
            self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def straighten(
        self,
        prompt: str,
        input_image: Optional[Image.Image] = None,
        input_images: Optional[List[Image.Image]] = None,
        max_iterations: Optional[int] = None,
        success_threshold: Optional[float] = None,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Iteratively improve image generation until it matches the prompt.
        
        Args:
            prompt: Target description of what the image should show
            input_image: Optional starting image to modify (legacy, single image)
            input_images: Optional list of starting images to condition on
            max_iterations: Maximum number of iterations (default from config)
            success_threshold: Confidence threshold for success (default from config)
            callback: Optional callback function called after each iteration
        
        Returns:
            Dictionary containing results and metadata
        """
        max_iterations = max_iterations or self.config.default_max_iterations
        success_threshold = success_threshold or self.config.success_threshold
        
        # Store input image for comparison in UI
        # Normalize input images
        imgs: List[Image.Image] = []
        if input_images:
            imgs.extend([img for img in input_images if img is not None])
        if input_image is not None:
            imgs.append(input_image)

        self.session_input_images = imgs or None

        history = []
        current_image = imgs[0] if imgs else None
        current_prompt = prompt

        # Validate and resize input image if provided
        if current_image and not validate_image(current_image):
            logger.warning("Invalid input image provided, starting from scratch")
            current_image = None
        elif current_image:
            current_image = resize_image_if_needed(current_image)
        # Resize all provided images
        input_images_resized: List[Image.Image] = []
        if imgs:
            for im in imgs:
                if validate_image(im):
                    input_images_resized.append(resize_image_if_needed(im))

        for iteration in range(1, max_iterations + 1):
            logger.info("🍌 Iteration %s/%s", iteration, max_iterations)
            
            try:
                # Generate or improve image
                if iteration == 1 and not imgs:
                    logger.info("📝 Generating initial image...")
                    current_image = self.generator.generate_image(prompt)
                else:
                    if history:
                        feedback = history[-1]['evaluation']['improvements']
                        if feedback and feedback.lower() not in ['none', 'n/a', 'none needed!']:
                            current_prompt = enhance_prompt_with_feedback(
                                original_prompt=prompt,
                                feedback=feedback,
                                iteration=iteration,
                                previous_history=history
                            )
                            logger.info("📝 Enhanced prompt based on feedback")
                    
                    logger.info("🎨 Generating improved image...")
                    if iteration == 1 and input_images_resized:
                        current_image = self.generator.generate_image(
                            current_prompt,
                            base_images=input_images_resized,
                        )
                    else:
                        current_image = self.generator.generate_image(
                            current_prompt,
                            base_images=[current_image] if current_image else None,
                        )
                
                if not validate_image(current_image):
                    logger.error("Failed to generate valid image for iteration %s", iteration)
                    continue
                
                # Save intermediate image if configured
                image_path = None
                if self.config.save_intermediates:
                    image_filename = f"iteration_{iteration:02d}.png"
                    image_path = self.session_dir / image_filename
                    save_image(current_image, image_path)
                    logger.info("💾 Saved to %s", image_path.name)
                
                # Evaluate the generated image
                logger.info("🔍 Evaluating image...")
                evaluation = self.evaluator.evaluate_image(
                    current_image,
                    prompt,
                    prompt_template=self.config.evaluation_prompt_template,
                )
                
                # Create iteration record
                iteration_data = {
                    'iteration': iteration,
                    'prompt_used': current_prompt,
                    'evaluation': evaluation,
                    'image_path': str(image_path) if image_path else None,
                    'timestamp': datetime.now().isoformat()
                }
                history.append(iteration_data)
                
                # Call callback if provided
                if callback:
                    try:
                        callback(iteration, current_image, evaluation)
                    except Exception as e:
                        logger.warning("Callback error: %s", e)
                
                # Display evaluation results
                match_status = "✅ YES" if evaluation['matches_intent'] else "❌ NO"
                logger.info("🎯 Match: %s", match_status)
                logger.info("📊 Confidence: %.2f%%", evaluation['confidence'] * 100)
                
                if not evaluation['matches_intent'] and evaluation['improvements']:
                    logger.info("💡 Next: %s...", evaluation['improvements'][:100])
                
                # Check for success
                if evaluation['matches_intent'] and evaluation['confidence'] >= success_threshold:
                    logger.info("🎉 Success! Image matches the prompt after %s iteration(s)", iteration)
                    
                    # Save final image
                    final_filename = f"final_image_{sanitize_filename(prompt[:30])}.png"
                    final_path = self.session_dir / final_filename
                    save_image(current_image, final_path)
                    
                    result = {
                        'success': True,
                        'final_image': current_image,
                        'final_image_path': str(final_path),
                        'iterations': iteration,
                        'history': history,
                        'session_dir': str(self.session_dir),
                        'confidence': evaluation['confidence'],
                        'session_id': self.session_id
                    }
                    
                    # Save session report
                    self._save_session_report(result, prompt)
                    logger.info(create_session_summary(prompt, result, self.session_start_time))
                    
                    return result
                    
            except Exception as e:
                logger.error("Error in iteration %s: %s", iteration, e)
                continue
        
        # Max iterations reached without success
        logger.warning("Maximum iterations (%s) reached", max_iterations)
        
        # Find best attempt
        if history:
            best_iteration = max(history, key=lambda x: x['evaluation']['confidence'])
            best_confidence = best_iteration['evaluation']['confidence']
        else:
            best_confidence = 0.0
        
        # Save final image
        final_filename = f"best_attempt_{sanitize_filename(prompt[:30])}.png"
        final_path = self.session_dir / final_filename
        if current_image and validate_image(current_image):
            save_image(current_image, final_path)
        
        result = {
            'success': False,
            'final_image': current_image,
            'final_image_path': str(final_path) if current_image else None,
            'iterations': max_iterations,
            'history': history,
            'session_dir': str(self.session_dir),
            'best_confidence': best_confidence,
            'session_id': self.session_id,
            'message': f"Best result: {best_confidence:.2%} confidence"
        }
        
        # Save session report
        self._save_session_report(result, prompt)
        logger.info(create_session_summary(prompt, result, self.session_start_time))
        
        return result
    
    def straighten_iterative(
        self,
        prompt: str,
        input_image: Optional[Image.Image] = None,
        input_images: Optional[List[Image.Image]] = None,
        max_iterations: Optional[int] = None,
        success_threshold: Optional[float] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generator version that yields results after each iteration.
        Useful for real-time UI updates.
        """
        max_iterations = max_iterations or self.config.default_max_iterations
        success_threshold = success_threshold or self.config.success_threshold
        
        # Normalize input images
        imgs: List[Image.Image] = []
        if input_images:
            imgs.extend([img for img in input_images if img is not None])
        if input_image is not None:
            imgs.append(input_image)

        history = []
        current_image = imgs[0] if imgs else None
        current_prompt = prompt
        
        # Validate input image
        if current_image:
            current_image = resize_image_if_needed(current_image)
            if not validate_image(current_image):
                current_image = None
        input_images_resized: List[Image.Image] = []
        if imgs:
            for im in imgs:
                if validate_image(im):
                    input_images_resized.append(resize_image_if_needed(im))
        
        for iteration in range(1, max_iterations + 1):
            try:
                # Generate or improve image
                if iteration == 1 and not imgs:
                    current_image = self.generator.generate_image(prompt)
                else:
                    if history:
                        feedback = history[-1]['evaluation']['improvements']
                        if feedback and feedback.lower() not in ['none', 'n/a', 'none needed!']:
                            current_prompt = enhance_prompt_with_feedback(
                                original_prompt=prompt,
                                feedback=feedback,
                                iteration=iteration,
                                previous_history=history
                            )
                    
                    if iteration == 1 and input_images_resized:
                        current_image = self.generator.generate_image(
                            current_prompt,
                            base_images=input_images_resized,
                        )
                    else:
                        current_image = self.generator.generate_image(
                            current_prompt,
                            base_images=[current_image] if current_image else None,
                        )
                
                if not validate_image(current_image):
                    continue
                
                # Evaluate the generated image
                evaluation = self.evaluator.evaluate_image(
                    current_image,
                    prompt,
                    prompt_template=self.config.evaluation_prompt_template,
                )
                
                # Create iteration record
                iteration_data = {
                    'iteration': iteration,
                    'current_image': current_image,
                    'prompt_used': current_prompt,
                    'evaluation': evaluation,
                    'success': evaluation['matches_intent'] and evaluation['confidence'] >= success_threshold,
                    'timestamp': datetime.now().isoformat()
                }
                history.append(iteration_data)
                
                # Yield current state
                yield iteration_data
                
                # Stop if successful
                if iteration_data['success']:
                    break
                    
            except Exception as e:
                # Yield error state
                yield {
                    'iteration': iteration,
                    'current_image': current_image,
                    'prompt_used': current_prompt,
                    'evaluation': {
                        'matches_intent': False,
                        'confidence': 0.0,
                        'improvements': f'Error: {e}'
                    },
                    'success': False,
                    'error': str(e)
                }
    
    def _save_session_report(self, result: Dict[str, Any], original_prompt: str) -> Path:
        """Save a detailed report of the straightening session."""
        report_data = {
            'session_id': self.session_id,
            'timestamp': self.session_start_time.isoformat(),
            'original_prompt': original_prompt,
            'success': result['success'],
            'total_iterations': result['iterations'],
            'final_confidence': result.get('confidence', result.get('best_confidence', 0)),
            'config': {
                'generator_model': self.config.generator_model,
                'evaluator_model': self.config.evaluator_model,
                'success_threshold': self.config.success_threshold
            },
            'history': result['history']
        }
        
        report_path = self.session_dir / "session_report.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            logger.info("📄 Session report saved: %s", report_path)
        except Exception as e:
            logger.warning("Failed to save session report: %s", e)
        
        return report_path
