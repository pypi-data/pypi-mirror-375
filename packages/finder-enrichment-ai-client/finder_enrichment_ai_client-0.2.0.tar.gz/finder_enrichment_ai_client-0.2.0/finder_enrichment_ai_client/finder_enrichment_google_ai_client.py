"""
Lightweight Google AI client using direct HTTP requests.
Part of the finder-enrichment-ai-client package for managing AI API calls.
"""
import os
import json
import time
import base64
import binascii
from typing import Dict, Any, Optional
import requests

class FinderEnrichmentGoogleAIClient:
    """Lightweight client for Google AI services using direct HTTP requests."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google AI client.
        
        Args:
            api_key: Google Gemini API key. If None, will check GOOGLE_GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"  # Default model
        
        if not self.api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY environment variable is required or pass api_key parameter")
    
    def generate_content(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate content using Google's Generative AI API.
        
        Args:
            prompt: The input prompt
            model: Model to use (defaults to gemini-1.5-flash)
            temperature: Creativity level (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            API response as dictionary with 'text', 'raw_response', 'success', and optional 'error'
        """
        if not model:
            model = self.model
            
        url = f"{self.base_url}/{model}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the generated text
            if "candidates" in result and result["candidates"]:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "text": text,
                    "raw_response": result,
                    "success": True
                }
            else:
                return {
                    "text": "",
                    "raw_response": result,
                    "success": False,
                    "error": "No content generated"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "text": "",
                "raw_response": None,
                "success": False,
                "error": str(e)
            }
    
    def analyze_image(
        self, 
        image_data: str,
        prompt: str,
        image_content_type: Optional[str] = "image/webp",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image using Google's Generative AI API.
        
        Args:
            image_data: base 64 encoded image data
            prompt: Analysis prompt
            model: Model to use
            
        Returns:
            Analysis result as dictionary with 'text', 'raw_response', 'success', and optional 'error'
        """
        if not model:
            model = "gemini-1.5-flash"
        
        # Validate inputs
        if not image_data:
            return {
                "text": "",
                "raw_response": None,
                "success": False,
                "error": "Image data is empty"
            }
        
        if not prompt:
            return {
                "text": "",
                "raw_response": None,
                "success": False,
                "error": "Prompt is empty"
            }
        
        # Validate base64 format
        try:
            base64.b64decode(image_data, validate=True)
        except (binascii.Error, ValueError) as e:
            return {
                "text": "",
                "raw_response": None,
                "success": False,
                "error": f"Invalid base64 image data: {str(e)}"
            }
            
        try:
            url = f"{self.base_url}/{model}:generateContent"
            
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            data = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": image_content_type,
                                "data": image_data
                            }
                        }
                    ]
                }]
            }
            
            # Log request details (without sensitive data)
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Sending image analysis request: model={model}, content_type={image_content_type}, image_size={len(image_data)}, prompt_size={len(prompt)}")
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if "candidates" in result and result["candidates"]:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "text": text,
                    "raw_response": result,
                    "success": True
                }
            else:
                return {
                    "text": "",
                    "raw_response": result,
                    "success": False,
                    "error": "No content generated"
                }
                
        except requests.exceptions.HTTPError as e:
            # Log error details for production troubleshooting
            error_detail = str(e)
            response_data = None
            
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"AI API HTTP error: status={e.response.status_code}")
                
                try:
                    response_data = e.response.json()
                    if 'error' in response_data:
                        api_error = response_data['error']
                        logger.error(f"AI API error: {api_error.get('message', 'Unknown error')} (code: {api_error.get('code', 'unknown')})")
                        error_detail = f"{str(e)} - {api_error.get('message', 'Unknown API error')}"
                    else:
                        logger.error(f"AI API returned unexpected response format")
                        error_detail = f"{str(e)} - Unexpected response format"
                except json.JSONDecodeError:
                    logger.error(f"AI API returned non-JSON response: {e.response.text[:200]}...")
                    error_detail = f"{str(e)} - Invalid response format"
                except Exception as parse_error:
                    logger.error(f"Error parsing AI API response: {parse_error}")
                    error_detail = f"{str(e)} - Response parsing failed"
            
            return {
                "text": "",
                "raw_response": response_data,
                "success": False,
                "error": error_detail
            }
        except Exception as e:
            return {
                "text": "",
                "raw_response": None,
                "success": False,
                "error": str(e)
            }
    
    def set_model(self, model: str):
        """Set the default model to use for API calls."""
        self.model = model
    
    def set_temperature(self, temperature: float):
        """Set the default temperature for content generation."""
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        self.temperature = temperature
    
    def get_available_models(self, page_size: int = 100) -> list[str]:
        """Retrieve available models from Google's Generative Language API.

        Returns a list of model identifiers (e.g., "gemini-1.5-flash").
        If the request fails, returns an empty list.
        """
        try:
            # The models endpoint lists all available models
            # Using API key via header for consistency with other methods
            url = f"{self.base_url}?pageSize={page_size}"
            headers = {
                "x-goog-api-key": self.api_key
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            payload = response.json()
            models_field = payload.get("models", [])

            model_names: list[str] = []
            for model_info in models_field:
                # Prefer canonical name without the "models/" prefix
                name = model_info.get("name", "")
                if name.startswith("models/"):
                    name = name.split("/", 1)[1]
                display_name = model_info.get("displayName", "")

                if name:
                    model_names.append(name)
                elif display_name:
                    model_names.append(display_name)

            # Deduplicate and sort for stable output
            unique_sorted = sorted({m for m in model_names if m})
            return unique_sorted
        except requests.exceptions.RequestException:
            return []
