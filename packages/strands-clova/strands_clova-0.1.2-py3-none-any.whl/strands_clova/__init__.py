"""CLOVA Studio model provider for Strands Agents SDK.

This package provides integration between CLOVA Studio (Naver's Korean AI platform)
and the Strands Agents SDK, enabling Korean language support for agent applications.
"""

from typing import Optional

from .clova import ClovaModel, ClovaModelError

__version__ = "0.1.2"
__all__ = ["ClovaModel", "ClovaModelError"]


# Convenience exports for common use cases
def create_clova_model(api_key: Optional[str] = None, **kwargs) -> ClovaModel:
    """Create a CLOVA model instance with default settings.

    Args:
        api_key: CLOVA API key (can also be set via CLOVA_API_KEY env var)
        **kwargs: Additional model parameters

    Returns:
        Configured ClovaModel instance
    """
    return ClovaModel(api_key=api_key, **kwargs)
