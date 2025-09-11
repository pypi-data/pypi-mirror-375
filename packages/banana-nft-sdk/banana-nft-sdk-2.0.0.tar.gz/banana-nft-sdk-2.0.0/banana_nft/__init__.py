"""
🍌 BananaNFT SDK - Powered by Nano-Banana AI

Revolutionary AI-powered NFT collection generation with mathematical rarity control.
Harness the power of Google's nano-banana model for unlimited creative possibilities!

🚀 Why BananaNFT?
- 🍌 Powered by cutting-edge nano-banana multimodal AI
- 🧠 Mathematical rarity precision (not random combinations)
- 🎯 Multi-image conditioning for ultra-unique results  
- 📈 Market intelligence learns from successful collections
- ⚡ One-click generate → deploy → OpenSea pipeline
- 🔗 Advanced prompt chaining for legendary-tier NFTs

Quick Start:
    from recreate_nft import BananaNFT
    
    # Initialize with your OpenRouter API key
    nft = BananaNFT(api_key="your_openrouter_key")
    
    # Go bananas with simple generation
    collection = nft.go_bananas(
        image="selfie.jpg", 
        style="crypto_punks",
        size=1000,
        vibe="legendary"  # Auto-optimizes everything
    )
    
    # Advanced rarity control
    collection = nft.create_collection(
        image="base.jpg",
        style="bored_apes", 
        size=10000,
        
        # Mathematical rarity distribution
        rarity_curve={
            "legendary": 0.005,  # 50 NFTs (0.5%)
            "epic": 0.025,       # 250 NFTs (2.5%)
            "rare": 0.12,        # 1,200 NFTs (12%)
            "uncommon": 0.255,   # 2,550 NFTs (25.5%)
            "common": 0.60       # 6,000 NFTs (60%)
        },
        
        # Custom trait weights for homogeneous collections
        trait_system={
            "backgrounds": {"space": 0.01, "blue": 0.4, "forest": 0.15},
            "accessories": {"crown": 0.005, "hat": 0.2, "glasses": 0.3},
            "expressions": {"smile": 0.4, "serious": 0.2, "wink": 0.08}
        },
        
        # AI enhancement features
        prompt_evolution=True,        # Gets smarter each generation
        market_intelligence=True,     # Learns from trending NFTs  
        nano_banana_chains=5,         # Multi-iteration creativity
        json_metadata_generation=True # Auto-generate OpenSea metadata
    )
    
Chrome Extension Integration:
    # Load image from browser
    image_data = nft.from_url("https://example.com/image.jpg")
    
    # Generate with nano-banana chaining
    result = nft.create_chain_enhanced_image(
        image_data, 
        style="cyberpunk",
        chain_count=3,
        creativity_boost=1.8
    )
"""

__version__ = "2.0.0"
__author__ = "BananaNFT Team"

# Main client classes
from .client import BananaNFT                    # Primary brand
from .client import BananaNFT as RecreateNFT     # Backward compatibility
from .models import (
    ImageResult,
    NFTCollection,
    NFTToken,
    RaritySettings,
    DeploymentResult,
    SupportedStyle,
    SupportedNetwork,
)
from .exceptions import (
    RecreateError,
    APIError,
    ValidationError,
    RateLimitError,
)
from .contract_builder import (
    VisualContractBuilder,
    SmartContractConfig,
    BusinessRule,
    RuleType,
    TriggerCondition,
)

__all__ = [
    # Main client classes  
    "BananaNFT",
    "RecreateNFT",      # Backward compatibility
    
    # Core models
    "ImageResult", 
    "NFTCollection",
    "NFTToken",
    "RaritySettings",
    "DeploymentResult",
    "SupportedStyle",
    "SupportedNetwork",
    
    # Smart contract builder
    "VisualContractBuilder",
    "SmartContractConfig",
    "BusinessRule",
    "RuleType",
    "TriggerCondition",
    
    # Exceptions
    "RecreateError",
    "APIError", 
    "ValidationError",
    "RateLimitError",
]