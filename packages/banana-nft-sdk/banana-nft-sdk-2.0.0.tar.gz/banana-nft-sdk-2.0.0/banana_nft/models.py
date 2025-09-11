"""
Data models for Recreate NFT SDK
"""

import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


# Type aliases for better readability
SupportedStyle = str  # "adventure_time", "crypto_punks", etc.
SupportedNetwork = str  # "ethereum", "polygon", "base", "arbitrum"


class RarityTier(str, Enum):
    """NFT rarity tiers"""
    COMMON = "common"
    UNCOMMON = "uncommon"  
    RARE = "rare"
    LEGENDARY = "legendary"


@dataclass
class RaritySettings:
    """Rarity distribution settings for collection generation"""
    common: int = 60
    uncommon: int = 25
    rare: int = 12
    legendary: int = 3
    
    def __post_init__(self):
        total = self.common + self.uncommon + self.rare + self.legendary
        if total != 100:
            raise ValueError(f"Rarity percentages must sum to 100, got {total}")
    
    def dict(self) -> Dict[str, int]:
        return {
            "common": self.common,
            "uncommon": self.uncommon, 
            "rare": self.rare,
            "legendary": self.legendary
        }


@dataclass
class ImageResult:
    """Enhanced result of image style transfer with BananaNFT features"""
    success: bool
    styled_image: str  # Base64 encoded image data
    style_id: str
    aspect_ratio: str = "auto"
    original_path: str = ""
    error_message: Optional[str] = None
    
    # BananaNFT enhanced fields
    chain_count: Optional[int] = None
    chain_history: Optional[List[Dict]] = None
    creativity_score: Optional[float] = None
    multi_image_conditioning: Optional[bool] = None
    reference_count: Optional[int] = None
    complexity_score: Optional[int] = None
    rarity_boost: Optional[float] = None
    nano_banana_description: Optional[str] = None
    conditioning_prompt: Optional[str] = None
    
    @property
    def image_bytes(self) -> bytes:
        """Get image as bytes for saving to file"""
        if not self.styled_image:
            raise ValueError("No styled image data available")
        
        # Remove data:image/jpeg;base64, prefix if present
        image_data = self.styled_image.split(',')[-1]
        return base64.b64decode(image_data)
    
    def save_image(self, filename: str):
        """Save styled image to file"""
        with open(filename, "wb") as f:
            f.write(self.image_bytes)


@dataclass 
class NFTToken:
    """Individual NFT token in a collection"""
    token_id: int
    image_data: str  # Base64 encoded image
    rarity: RarityTier
    traits: List[str]
    style: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def image_bytes(self) -> bytes:
        """Get image as bytes"""
        image_data = self.image_data.split(',')[-1]
        return base64.b64decode(image_data)
    
    @property
    def traits_dict(self) -> Dict[str, str]:
        """Get traits as key-value dictionary"""
        traits_dict = {}
        for trait in self.traits:
            if ':' in trait:
                key, value = trait.split(':', 1)
                traits_dict[key.strip()] = value.strip()
            else:
                traits_dict[f"trait_{len(traits_dict)}"] = trait
        return traits_dict
    
    @property
    def rarity_color(self) -> str:
        """Get color associated with rarity tier"""
        colors = {
            RarityTier.COMMON: "#9CA3AF",      # Gray
            RarityTier.UNCOMMON: "#3B82F6",    # Blue  
            RarityTier.RARE: "#F97316",        # Orange
            RarityTier.LEGENDARY: "#A855F7"    # Purple
        }
        return colors.get(self.rarity, "#9CA3AF")
    
    def save_image(self, filename: str):
        """Save NFT image to file"""
        with open(filename, "wb") as f:
            f.write(self.image_bytes)


@dataclass
class NFTCollection:
    """Complete NFT collection with all tokens and metadata"""
    collection_id: str
    name: str
    description: str
    style: str
    total_supply: int
    tokens: List[NFTToken]
    rarity_distribution: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def common_tokens(self) -> List[NFTToken]:
        """Get all common tokens"""
        return [t for t in self.tokens if t.rarity == RarityTier.COMMON]
    
    @property
    def uncommon_tokens(self) -> List[NFTToken]:
        """Get all uncommon tokens"""
        return [t for t in self.tokens if t.rarity == RarityTier.UNCOMMON]
    
    @property
    def rare_tokens(self) -> List[NFTToken]:
        """Get all rare tokens"""
        return [t for t in self.tokens if t.rarity == RarityTier.RARE]
    
    @property
    def legendary_tokens(self) -> List[NFTToken]:
        """Get all legendary tokens"""
        return [t for t in self.tokens if t.rarity == RarityTier.LEGENDARY]
    
    def get_tokens_by_rarity(self, rarity: RarityTier) -> List[NFTToken]:
        """Get tokens filtered by rarity"""
        return [t for t in self.tokens if t.rarity == rarity]
    
    def get_rarity_percentage(self, rarity: RarityTier) -> float:
        """Get actual percentage of tokens with given rarity"""
        if not self.tokens:
            return 0.0
        count = len(self.get_tokens_by_rarity(rarity))
        return (count / len(self.tokens)) * 100
    
    def summary(self) -> str:
        """Get collection summary string"""
        lines = [
            f"🦙 {self.name}",
            f"📊 {len(self.tokens)} NFTs • {self.style} style",
            f"🎨 Rarity Distribution:",
            f"   • Common: {self.get_rarity_percentage(RarityTier.COMMON):.1f}% ({len(self.common_tokens)} NFTs)",
            f"   • Uncommon: {self.get_rarity_percentage(RarityTier.UNCOMMON):.1f}% ({len(self.uncommon_tokens)} NFTs)",
            f"   • Rare: {self.get_rarity_percentage(RarityTier.RARE):.1f}% ({len(self.rare_tokens)} NFTs)",
            f"   • Legendary: {self.get_rarity_percentage(RarityTier.LEGENDARY):.1f}% ({len(self.legendary_tokens)} NFTs)",
        ]
        return "\n".join(lines)


@dataclass
class DeploymentResult:
    """Result of NFT collection deployment to blockchain"""
    success: bool
    collection_id: str
    network: str
    contract_address: Optional[str] = None
    opensea_url: Optional[str] = None
    transaction_hash: Optional[str] = None
    deployment_cost: Optional[str] = None
    gas_used: Optional[int] = None
    block_number: Optional[int] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    
    def __str__(self) -> str:
        if self.success:
            return f"✅ Deployed to {self.network}: {self.contract_address}"
        else:
            return f"❌ Deployment failed: {self.error_message}"


@dataclass
class StyleInfo:
    """Information about a supported style"""
    id: str
    name: str
    description: str
    category: str  # "cartoon", "crypto", "artistic"
    example_traits: List[str] = field(default_factory=list)
    
    
# Predefined style information
STYLE_CATALOG = {
    # Cartoon Network & Animation
    "adventure_time": StyleInfo(
        id="adventure_time",
        name="Adventure Time", 
        description="Mathematical Land of Ooo aesthetic with bright colors and whimsical characters",
        category="cartoon",
        example_traits=["Candy Kingdom background", "algebraic mood", "Finn's hat accessory"]
    ),
    "rick_morty": StyleInfo(
        id="rick_morty",
        name="Rick & Morty",
        description="Interdimensional sci-fi chaos with existential themes", 
        category="cartoon",
        example_traits=["spaceship background", "wubba lubba dub dub mood", "portal gun accessory"]
    ),
    "gravity_falls": StyleInfo(
        id="gravity_falls", 
        name="Gravity Falls",
        description="Mysterious Pacific Northwest vibes with supernatural elements",
        category="cartoon", 
        example_traits=["Mystery Shack background", "mysterious mood", "journal #3 accessory"]
    ),
    "steven_universe": StyleInfo(
        id="steven_universe",
        name="Steven Universe", 
        description="Gem magic with pastel colors and emotional growth themes",
        category="cartoon",
        example_traits=["Beach City background", "magical mood", "gem weapon accessory"]
    ),
    "simpsons": StyleInfo(
        id="simpsons",
        name="The Simpsons", 
        description="Classic Springfield yellow with iconic animation style",
        category="cartoon",
        example_traits=["Nuclear Plant background", "d'oh moment mood", "donut accessory"] 
    ),
    "south_park": StyleInfo(
        id="south_park",
        name="South Park",
        description="Cut-out paper animation style with irreverent humor",
        category="cartoon",
        example_traits=["South Park Elementary background", "oh my god mood", "orange parka accessory"]
    ),
    
    # Crypto Collections
    "crypto_punks": StyleInfo(
        id="crypto_punks",
        name="CryptoPunks",
        description="8-bit pixel art rebels with punk rock attitude", 
        category="crypto",
        example_traits=["blue background", "mohawk accessory", "cigarette feature"]
    ),
    "bored_apes": StyleInfo(
        id="bored_apes",
        name="Bored Ape Yacht Club", 
        description="Ape characteristics with exclusive club member vibes",
        category="crypto",
        example_traits=["yellow background", "brown fur", "3d glasses accessory"]
    ),
    "azuki": StyleInfo(
        id="azuki",
        name="Azuki",
        description="Anime streetwear culture with Japanese aesthetic",
        category="crypto", 
        example_traits=["off white background", "hoodie clothing", "katana accessory"]
    ),
    "labubu": StyleInfo(
        id="labubu",
        name="Labubu",
        description="Cute vinyl figure aesthetic with designer toy vibes",
        category="crypto",
        example_traits=["classic white color", "bow tie accessory", "happy expression"]
    ),
    
    # Artistic Styles
    "anime": StyleInfo(
        id="anime", 
        name="Anime",
        description="Japanese animation style with expressive characters",
        category="artistic",
        example_traits=["dramatic lighting", "expressive eyes", "dynamic poses"]
    ),
    "cartoon": StyleInfo(
        id="cartoon",
        name="Cartoon", 
        description="Western cartoon style with exaggerated features",
        category="artistic",
        example_traits=["bold outlines", "vibrant colors", "expressive features"]
    ),
    "realistic": StyleInfo(
        id="realistic",
        name="Realistic",
        description="Photorealistic rendering with natural details", 
        category="artistic",
        example_traits=["natural lighting", "detailed textures", "lifelike proportions"]
    ),
    "pixel": StyleInfo(
        id="pixel",
        name="Pixel Art",
        description="8-bit pixel style with retro gaming aesthetic",
        category="artistic", 
        example_traits=["pixelated edges", "limited color palette", "retro vibes"]
    ),
    "watercolor": StyleInfo(
        id="watercolor",
        name="Watercolor",
        description="Artistic painting style with flowing colors",
        category="artistic",
        example_traits=["soft edges", "color bleeding", "artistic texture"]
    )
}