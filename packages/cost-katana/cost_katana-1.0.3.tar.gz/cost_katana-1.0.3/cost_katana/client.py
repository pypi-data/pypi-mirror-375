"""
Cost Katana HTTP Client
Handles communication with the Cost Katana backend API
"""

import json
from typing import Dict, Any, Optional, List
import httpx
from .config import Config
from .exceptions import (
    CostKatanaError,
    AuthenticationError,
    ModelNotAvailableError,
    RateLimitError,
    CostLimitExceededError,
)

# Global client instance for the configure function
_global_client = None


def configure(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    config_file: Optional[str] = None,
    **kwargs,
):
    """
    Configure Cost Katana client globally.

    Args:
        api_key: Your Cost Katana API key (starts with 'dak_')
        base_url: Base URL for Cost Katana API (optional)
        config_file: Path to JSON configuration file (optional)
        **kwargs: Additional configuration options

    Example:
        # Using API key
        cost_katana.configure(api_key='dak_your_key_here')

        # Using config file
        cost_katana.configure(config_file='config.json')
    """
    global _global_client
    _global_client = CostKatanaClient(
        api_key=api_key, base_url=base_url, config_file=config_file, **kwargs
    )
    return _global_client


def get_global_client():
    """Get the global client instance"""
    if _global_client is None:
        raise CostKatanaError("Cost Katana not configured. Call cost_katana.configure() first.")
    return _global_client


class CostKatanaClient:
    """HTTP client for Cost Katana API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config_file: Optional[str] = None,
        timeout: int = 30,
        **kwargs,
    ):
        """
        Initialize Cost Katana client.

        Args:
            api_key: Your Cost Katana API key
            base_url: Base URL for the API
            config_file: Path to JSON configuration file
            timeout: Request timeout in seconds
        """
        self.config = Config.from_file(config_file) if config_file else Config()

        # Override with provided parameters
        if api_key:
            self.config.api_key = api_key
        if base_url:
            self.config.base_url = base_url

        # Apply additional config
        for key, value in kwargs.items():
            setattr(self.config, key, value)

        # Validate configuration
        if not self.config.api_key:
            raise AuthenticationError(
                "API key is required. Get one from https://costkatana.com/integrations"
            )

        # Initialize HTTP client
        self.client = httpx.Client(
            base_url=self.config.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"cost-katana-python/1.0.0",
            },
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client"""
        if hasattr(self, "client"):
            self.client.close()

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise CostKatanaError(f"Invalid JSON response: {response.text}")

        if response.status_code == 401:
            raise AuthenticationError(data.get("message", "Authentication failed"))
        elif response.status_code == 403:
            raise AuthenticationError(data.get("message", "Access forbidden"))
        elif response.status_code == 404:
            raise ModelNotAvailableError(data.get("message", "Model not found"))
        elif response.status_code == 429:
            raise RateLimitError(data.get("message", "Rate limit exceeded"))
        elif response.status_code == 400 and "cost" in data.get("message", "").lower():
            raise CostLimitExceededError(data.get("message", "Cost limit exceeded"))
        elif not response.is_success:
            raise CostKatanaError(data.get("message", f"API error: {response.status_code}"))

        return data

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            response = self.client.get("/api/chat/models")
            data = self._handle_response(response)
            return data.get("data", [])
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to get models: {str(e)}")

    def send_message(
        self,
        message: str,
        model_id: str,
        conversation_id: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        chat_mode: str = "balanced",
        use_multi_agent: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Send a message to the AI model via Cost Katana.

        Args:
            message: The message to send
            model_id: ID of the model to use
            conversation_id: Optional conversation ID
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            chat_mode: Chat optimization mode ('fastest', 'cheapest', 'balanced')
            use_multi_agent: Whether to use multi-agent processing

        Returns:
            Response data from the API
        """
        payload = {
            "message": message,
            "modelId": model_id,
            "temperature": temperature,
            "maxTokens": max_tokens,
            "chatMode": chat_mode,
            "useMultiAgent": use_multi_agent,
            **kwargs,
        }

        if conversation_id:
            payload["conversationId"] = conversation_id

        try:
            response = self.client.post("/api/chat/message", json=payload)
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to send message: {str(e)}")

    def create_conversation(
        self, title: Optional[str] = None, model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new conversation"""
        payload = {}
        if title:
            payload["title"] = title
        if model_id:
            payload["modelId"] = model_id

        try:
            response = self.client.post("/api/chat/conversations", json=payload)
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to create conversation: {str(e)}")

    def get_conversation_history(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation history"""
        try:
            response = self.client.get(f"/api/chat/conversations/{conversation_id}/history")
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to get conversation history: {str(e)}")

    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Delete a conversation"""
        try:
            response = self.client.delete(f"/api/chat/conversations/{conversation_id}")
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to delete conversation: {str(e)}")

    # SAST (Semantic Abstract Syntax Tree) Methods

    def optimize_with_sast(
        self,
        prompt: str,
        service: str = "openai",
        model: str = "gpt-4o-mini",
        language: str = "en",
        ambiguity_resolution: bool = True,
        cross_lingual: bool = False,
        disambiguation_strategy: str = "hybrid",
        preserve_ambiguity: bool = False,
        max_primitives: int = 100,
        semantic_threshold: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Optimize a prompt using SAST (Semantic Abstract Syntax Tree) processing.

        Args:
            prompt: The text prompt to optimize
            service: AI service to use ('openai', 'anthropic', etc.)
            model: Model to use for optimization
            language: Language for SAST processing
            ambiguity_resolution: Enable ambiguity resolution
            cross_lingual: Enable cross-lingual semantic mapping
            disambiguation_strategy: Strategy for disambiguation ('strict', 'permissive', 'hybrid')
            preserve_ambiguity: Keep ambiguous structures for analysis
            max_primitives: Maximum semantic primitives to use
            semantic_threshold: Semantic confidence threshold
            **kwargs: Additional parameters

        Returns:
            Dict containing optimization results with SAST metadata
        """
        payload = {
            "prompt": prompt,
            "service": service,
            "model": model,
            "enableCortex": True,
            "cortexOperation": "sast",
            "cortexStyle": "conversational",
            "cortexFormat": "plain",
            "cortexSemanticCache": True,
            "cortexPreserveSemantics": True,
            "cortexIntelligentRouting": True,
            "cortexSastProcessing": True,
            "cortexAmbiguityResolution": ambiguity_resolution,
            "cortexCrossLingualMode": cross_lingual,
            **kwargs,
        }

        headers = {
            "CostKatana-Cortex-Operation": "sast",
            "CostKatana-Cortex-Sast-Language": language,
            "CostKatana-Cortex-Disambiguation-Strategy": disambiguation_strategy,
            "CostKatana-Cortex-Preserve-Ambiguity": str(preserve_ambiguity).lower(),
            "CostKatana-Cortex-Max-Primitives": str(max_primitives),
            "CostKatana-Cortex-Semantic-Threshold": str(semantic_threshold),
        }

        try:
            response = self.client.post("/api/optimizations", json=payload, headers=headers)
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to optimize with SAST: {str(e)}")

    def compare_sast_vs_traditional(
        self,
        prompt: str,
        service: str = "openai",
        model: str = "gpt-4o-mini",
        language: str = "en",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Compare traditional Cortex optimization vs SAST optimization.

        Args:
            prompt: The text prompt to compare
            service: AI service to use
            model: Model to use
            language: Language for analysis
            **kwargs: Additional parameters

        Returns:
            Dict containing comparison results
        """
        payload = {"text": prompt, "language": language, **kwargs}

        try:
            response = self.client.post("/api/optimizations/sast/compare", json=payload)
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to compare SAST vs traditional: {str(e)}")

    def get_sast_vocabulary_stats(self) -> Dict[str, Any]:
        """
        Get SAST semantic primitives vocabulary statistics.

        Returns:
            Dict containing vocabulary statistics
        """
        try:
            response = self.client.get("/api/optimizations/sast/vocabulary")
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to get SAST vocabulary stats: {str(e)}")

    def search_semantic_primitives(
        self,
        term: Optional[str] = None,
        category: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Search semantic primitives by term, category, or language.

        Args:
            term: Search term for primitives
            category: Filter by category ('concept', 'action', 'property', etc.)
            language: Filter by language support
            limit: Maximum number of results

        Returns:
            Dict containing search results
        """
        payload = {}
        if term:
            payload["term"] = term
        if category:
            payload["category"] = category
        if language:
            payload["language"] = language
        payload["limit"] = limit

        try:
            response = self.client.post("/api/optimizations/sast/search", json=payload)
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to search semantic primitives: {str(e)}")

    def get_telescope_demo(self) -> Dict[str, Any]:
        """
        Get the telescope ambiguity resolution demonstration.

        Returns:
            Dict containing telescope demo results
        """
        try:
            response = self.client.get("/api/optimizations/sast/telescope-demo")
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to get telescope demo: {str(e)}")

    def test_universal_semantics(
        self,
        concept: str,
        languages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Test universal semantic representation across languages.

        Args:
            concept: Concept to test universally
            languages: List of language codes to test (default: ['en', 'es', 'fr'])

        Returns:
            Dict containing universal semantics test results
        """
        if languages is None:
            languages = ["en", "es", "fr"]

        payload = {"concept": concept, "languages": languages}

        try:
            response = self.client.post("/api/optimizations/sast/universal-test", json=payload)
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to test universal semantics: {str(e)}")

    def get_sast_stats(self) -> Dict[str, Any]:
        """
        Get SAST performance and usage statistics.

        Returns:
            Dict containing SAST statistics
        """
        try:
            response = self.client.get("/api/optimizations/sast/stats")
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to get SAST stats: {str(e)}")

    def get_sast_showcase(self) -> Dict[str, Any]:
        """
        Get SAST showcase with examples and performance analytics.

        Returns:
            Dict containing SAST showcase data
        """
        try:
            response = self.client.get("/api/optimizations/sast/showcase")
            return self._handle_response(response)
        except Exception as e:
            if isinstance(e, CostKatanaError):
                raise
            raise CostKatanaError(f"Failed to get SAST showcase: {str(e)}")
