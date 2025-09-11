#!/usr/bin/env python3
"""
🍌 BananaNFT Multi-Image Conditioning Engine

Revolutionary multi-modal image conditioning system that allows nano-banana
to process multiple reference images simultaneously for ultra-precise NFT generation.

This is the secret sauce that makes BananaNFT collections truly unique:
- Base character image
- Style reference image  
- Background reference image
- Texture/material reference image
- Lighting reference image

Each combination creates completely unique NFTs impossible to replicate.
"""

import base64
import requests
from io import BytesIO
from PIL import Image
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from pathlib import Path
import random
import json

@dataclass
class ImageReference:
    """Single image reference for multi-conditioning"""
    name: str
    purpose: str                    # "base", "style", "background", "texture", "lighting"
    image_data: str                 # Base64 encoded image
    influence_weight: float         # 0.0-1.0, how much this image influences the result
    prompt_enhancement: str         # Additional prompt text this image adds
    rarity_modifier: float          # How this affects rarity (0.5-2.0)

@dataclass 
class MultiImagePrompt:
    """Complete multi-image prompt for nano-banana conditioning"""
    primary_image: ImageReference
    reference_images: List[ImageReference]
    text_prompt: str
    combined_influence: float
    estimated_rarity_boost: float
    generation_complexity: int      # 1-5, affects processing time

class BananaNFTMultiImageEngine:
    """
    🎨 Revolutionary Multi-Image Conditioning System
    
    This engine processes multiple reference images simultaneously to create
    NFTs with unprecedented uniqueness and artistic coherence.
    
    Traditional NFT generation: 1 image + text → output
    BananaNFT generation: 5 images + intelligent text → masterpiece
    """
    
    def __init__(self):
        self.reference_library = self._initialize_reference_library()
        self.conditioning_strategies = self._initialize_conditioning_strategies()
        
    def _initialize_reference_library(self) -> Dict[str, Dict[str, ImageReference]]:
        """Initialize library of reference images for different purposes"""
        
        # In production, these would be actual curated reference images
        # For now, we'll create placeholder references with detailed prompts
        
        return {
            "style_references": {
                "crypto_punks_original": ImageReference(
                    name="Original CryptoPunk",
                    purpose="style",
                    image_data="[base64_crypto_punk_reference]",
                    influence_weight=0.8,
                    prompt_enhancement="with authentic CryptoPunks pixel art style, 8-bit aesthetic",
                    rarity_modifier=1.2
                ),
                "bored_ape_original": ImageReference(
                    name="Original Bored Ape",
                    purpose="style", 
                    image_data="[base64_bored_ape_reference]",
                    influence_weight=0.9,
                    prompt_enhancement="with authentic Bored Ape Yacht Club art style and proportions",
                    rarity_modifier=1.3
                ),
                "azuki_original": ImageReference(
                    name="Original Azuki",
                    purpose="style",
                    image_data="[base64_azuki_reference]",
                    influence_weight=0.85,
                    prompt_enhancement="with authentic Azuki anime-inspired art style and clean lines",
                    rarity_modifier=1.1
                )
            },
            
            "background_references": {
                "cosmic_nebula": ImageReference(
                    name="Cosmic Nebula",
                    purpose="background",
                    image_data="[base64_nebula_reference]",
                    influence_weight=0.6,
                    prompt_enhancement="set against swirling cosmic nebula with deep space colors",
                    rarity_modifier=1.4
                ),
                "golden_luxury": ImageReference(
                    name="Gold Leaf Luxury",
                    purpose="background",
                    image_data="[base64_gold_reference]",
                    influence_weight=0.7,
                    prompt_enhancement="set against luxurious gold leaf background with rich textures",
                    rarity_modifier=1.6
                ),
                "crystal_cave": ImageReference(
                    name="Crystal Cave",
                    purpose="background",
                    image_data="[base64_crystal_reference]",
                    influence_weight=0.65,
                    prompt_enhancement="set in mystical crystal cave with refracting light",
                    rarity_modifier=1.5
                ),
                "neon_cityscape": ImageReference(
                    name="Cyberpunk City",
                    purpose="background",
                    image_data="[base64_city_reference]",
                    influence_weight=0.6,
                    prompt_enhancement="set against neon-lit cyberpunk cityscape at night",
                    rarity_modifier=1.2
                )
            },
            
            "texture_references": {
                "holographic_foil": ImageReference(
                    name="Holographic Foil",
                    purpose="texture",
                    image_data="[base64_holographic_reference]",
                    influence_weight=0.5,
                    prompt_enhancement="with holographic foil texture and rainbow shimmer",
                    rarity_modifier=1.8
                ),
                "liquid_chrome": ImageReference(
                    name="Liquid Chrome", 
                    purpose="texture",
                    image_data="[base64_chrome_reference]",
                    influence_weight=0.6,
                    prompt_enhancement="with liquid chrome metallic texture and reflections",
                    rarity_modifier=1.7
                ),
                "diamond_crystal": ImageReference(
                    name="Diamond Crystal",
                    purpose="texture",
                    image_data="[base64_diamond_reference]",
                    influence_weight=0.7,
                    prompt_enhancement="with crystalline diamond texture and light refraction",
                    rarity_modifier=1.9
                ),
                "organic_wood": ImageReference(
                    name="Natural Wood",
                    purpose="texture",
                    image_data="[base64_wood_reference]",
                    influence_weight=0.4,
                    prompt_enhancement="with natural wood grain texture and organic feel",
                    rarity_modifier=1.1
                )
            },
            
            "lighting_references": {
                "studio_portrait": ImageReference(
                    name="Studio Portrait Lighting",
                    purpose="lighting",
                    image_data="[base64_studio_reference]",
                    influence_weight=0.3,
                    prompt_enhancement="with professional studio portrait lighting setup",
                    rarity_modifier=1.0
                ),
                "dramatic_rim": ImageReference(
                    name="Dramatic Rim Lighting",
                    purpose="lighting", 
                    image_data="[base64_rim_reference]",
                    influence_weight=0.4,
                    prompt_enhancement="with dramatic rim lighting creating silhouette effects",
                    rarity_modifier=1.3
                ),
                "golden_hour": ImageReference(
                    name="Golden Hour",
                    purpose="lighting",
                    image_data="[base64_golden_reference]",
                    influence_weight=0.35,
                    prompt_enhancement="with warm golden hour lighting and soft shadows",
                    rarity_modifier=1.2
                ),
                "neon_glow": ImageReference(
                    name="Neon Glow",
                    purpose="lighting",
                    image_data="[base64_neon_reference]",
                    influence_weight=0.5,
                    prompt_enhancement="with vibrant neon glow lighting effects",
                    rarity_modifier=1.4
                )
            },
            
            "material_references": {
                "silk_fabric": ImageReference(
                    name="Silk Fabric",
                    purpose="material",
                    image_data="[base64_silk_reference]",
                    influence_weight=0.3,
                    prompt_enhancement="with flowing silk fabric texture and sheen",
                    rarity_modifier=1.1
                ),
                "volcanic_rock": ImageReference(
                    name="Volcanic Rock",
                    purpose="material",
                    image_data="[base64_volcanic_reference]",
                    influence_weight=0.4,
                    prompt_enhancement="with rough volcanic rock texture and dark tones",
                    rarity_modifier=1.2
                ),
                "ice_crystal": ImageReference(
                    name="Ice Crystal",
                    purpose="material", 
                    image_data="[base64_ice_reference]",
                    influence_weight=0.45,
                    prompt_enhancement="with crystalline ice texture and transparency",
                    rarity_modifier=1.5
                )
            }
        }
    
    def _initialize_conditioning_strategies(self) -> Dict[str, Dict]:
        """Initialize strategies for different rarity tiers"""
        
        return {
            "common": {
                "max_references": 2,
                "allowed_purposes": ["style", "background"],
                "influence_range": (0.3, 0.6),
                "complexity_limit": 2
            },
            "uncommon": {
                "max_references": 3,
                "allowed_purposes": ["style", "background", "lighting"],
                "influence_range": (0.4, 0.7),
                "complexity_limit": 3
            },
            "rare": {
                "max_references": 4,
                "allowed_purposes": ["style", "background", "lighting", "texture"],
                "influence_range": (0.5, 0.8),
                "complexity_limit": 4
            },
            "epic": {
                "max_references": 5,
                "allowed_purposes": ["style", "background", "lighting", "texture", "material"],
                "influence_range": (0.6, 0.9),
                "complexity_limit": 5
            },
            "legendary": {
                "max_references": 6,
                "allowed_purposes": ["style", "background", "lighting", "texture", "material"],
                "influence_range": (0.7, 1.0),
                "complexity_limit": 5,
                "special_effects": True
            }
        }
    
    def generate_multi_image_prompt(
        self,
        base_image_data: str,
        style: str,
        target_rarity: str = "rare",
        custom_references: Optional[List[ImageReference]] = None,
        creativity_boost: float = 1.0
    ) -> MultiImagePrompt:
        """
        Generate multi-image conditioning prompt for nano-banana
        
        Args:
            base_image_data: Primary image as base64
            style: Target style (crypto_punks, bored_apes, etc.)
            target_rarity: Target rarity tier for reference selection
            custom_references: Optional custom reference images
            creativity_boost: Multiplier for reference influence
            
        Returns:
            Complete multi-image prompt ready for nano-banana processing
        """
        
        # Create primary image reference
        primary_ref = ImageReference(
            name="Primary Subject",
            purpose="base",
            image_data=base_image_data,
            influence_weight=1.0,
            prompt_enhancement="as the main subject character",
            rarity_modifier=1.0
        )
        
        # Select reference images based on rarity strategy
        strategy = self.conditioning_strategies.get(target_rarity, self.conditioning_strategies["rare"])
        reference_images = custom_references or self._select_strategic_references(style, strategy, creativity_boost)
        
        # Build comprehensive text prompt
        text_prompt = self._build_multi_image_text_prompt(style, reference_images, creativity_boost)
        
        # Calculate combined influence and rarity boost
        combined_influence = sum(ref.influence_weight for ref in reference_images)
        rarity_boost = sum(ref.rarity_modifier for ref in reference_images) / len(reference_images)
        complexity = len([ref for ref in reference_images if ref.influence_weight > 0.5])
        
        return MultiImagePrompt(
            primary_image=primary_ref,
            reference_images=reference_images,
            text_prompt=text_prompt,
            combined_influence=combined_influence,
            estimated_rarity_boost=rarity_boost,
            generation_complexity=min(complexity, 5)
        )
    
    def _select_strategic_references(
        self, 
        style: str, 
        strategy: Dict, 
        creativity_boost: float
    ) -> List[ImageReference]:
        """Select reference images based on strategy and creativity level"""
        
        references = []
        allowed_purposes = strategy["allowed_purposes"]
        max_refs = min(strategy["max_references"], int(3 + creativity_boost * 2))
        influence_min, influence_max = strategy["influence_range"]
        
        # Always include style reference
        if "style" in allowed_purposes:
            style_key = f"{style}_original" if f"{style}_original" in self.reference_library["style_references"] else "crypto_punks_original"
            style_ref = self.reference_library["style_references"][style_key]
            # Adjust influence based on creativity boost
            style_ref.influence_weight = min(influence_max, style_ref.influence_weight * creativity_boost)
            references.append(style_ref)
        
        # Add other references based on rarity and creativity
        remaining_purposes = [p for p in allowed_purposes if p != "style"]
        num_additional = min(max_refs - 1, len(remaining_purposes))
        
        for purpose in random.sample(remaining_purposes, num_additional):
            category_key = f"{purpose}_references"
            if category_key in self.reference_library:
                category_refs = self.reference_library[category_key]
                
                # Weight selection by rarity modifier for higher tiers
                if strategy.get("special_effects") and creativity_boost > 1.5:
                    # Legendary tier: prefer high rarity modifiers
                    weights = [ref.rarity_modifier for ref in category_refs.values()]
                    selected_key = random.choices(list(category_refs.keys()), weights=weights)[0]
                else:
                    # Other tiers: random selection
                    selected_key = random.choice(list(category_refs.keys()))
                
                selected_ref = category_refs[selected_key]
                # Adjust influence based on strategy and creativity
                adjusted_influence = random.uniform(influence_min, influence_max) * creativity_boost
                selected_ref.influence_weight = min(1.0, adjusted_influence)
                references.append(selected_ref)
        
        return references
    
    def _build_multi_image_text_prompt(
        self,
        style: str,
        references: List[ImageReference], 
        creativity_boost: float
    ) -> str:
        """Build comprehensive text prompt incorporating all references"""
        
        # Base style prompt
        style_mapping = {
            "crypto_punks": "Transform into detailed CryptoPunks pixel art style",
            "bored_apes": "Transform into detailed Bored Ape Yacht Club style",
            "azuki": "Transform into detailed Azuki anime-inspired style",
            "pudgy_penguins": "Transform into detailed Pudgy Penguins style"
        }
        
        base_prompt = style_mapping.get(style, f"Transform into detailed {style.replace('_', ' ')} style")
        
        # Add reference-specific enhancements
        enhancements = []
        for ref in references:
            if ref.purpose != "base" and ref.influence_weight > 0.3:
                enhancements.append(ref.prompt_enhancement)
        
        # Combine with advanced modifiers
        if enhancements:
            full_prompt = f"{base_prompt}, {', '.join(enhancements)}"
        else:
            full_prompt = base_prompt
        
        # Add quality and creativity modifiers
        quality_modifiers = [
            "ultra high quality 8K digital art",
            "perfect lighting and composition", 
            "trending on SuperRare and Foundation",
            "museum-quality masterpiece"
        ]
        
        if creativity_boost > 1.5:
            full_prompt += f". {'. '.join(quality_modifiers)}"
        elif creativity_boost > 1.0:
            full_prompt += f". {random.choice(quality_modifiers)}"
        
        return full_prompt
    
    def prepare_nano_banana_payload(
        self,
        multi_prompt: MultiImagePrompt,
        model: str = "google/nano-banana",
        temperature: float = 0.8
    ) -> Dict:
        """
        Prepare complete payload for nano-banana API with multi-image conditioning
        
        This is the revolutionary part - nano-banana can process multiple images
        simultaneously to create unprecedented results.
        """
        
        # Build message content with multiple images
        content = [
            {
                "type": "text",
                "text": multi_prompt.text_prompt
            }
        ]
        
        # Add primary image
        primary_b64 = multi_prompt.primary_image.image_data
        if not primary_b64.startswith("data:image"):
            primary_b64 = f"data:image/jpeg;base64,{primary_b64}"
        
        content.append({
            "type": "image_url",
            "image_url": {
                "url": primary_b64,
                "detail": "high"  # High detail for primary
            }
        })
        
        # Add reference images (nano-banana can handle multiple!)
        for i, ref in enumerate(multi_prompt.reference_images[:3]):  # Limit to 3 additional for API efficiency
            if ref.influence_weight > 0.4:  # Only include influential references
                ref_b64 = ref.image_data
                if not ref_b64.startswith("data:image") and not ref_b64.startswith("[base64"):
                    ref_b64 = f"data:image/jpeg;base64,{ref_b64}"
                
                # Skip placeholder references in production
                if not ref_b64.startswith("[base64"):
                    content.append({
                        "type": "image_url", 
                        "image_url": {
                            "url": ref_b64,
                            "detail": "low" if ref.influence_weight < 0.6 else "high"
                        }
                    })
        
        # Create complete payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": 1500,
            "temperature": min(1.0, temperature + (multi_prompt.generation_complexity * 0.1))
        }
        
        return payload
    
    def create_reference_from_url(self, url: str, purpose: str, influence_weight: float = 0.5) -> ImageReference:
        """Create reference from image URL (for Chrome extension integration)"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Convert to base64
            img_b64 = base64.b64encode(response.content).decode()
            
            return ImageReference(
                name=f"Custom {purpose.title()}",
                purpose=purpose,
                image_data=f"data:image/jpeg;base64,{img_b64}",
                influence_weight=influence_weight,
                prompt_enhancement=f"incorporating {purpose} reference styling",
                rarity_modifier=1.0 + (influence_weight * 0.5)
            )
        except Exception as e:
            raise ValueError(f"Failed to load reference from URL: {e}")
    
    def create_reference_from_file(self, file_path: Union[str, Path], purpose: str, influence_weight: float = 0.5) -> ImageReference:
        """Create reference from local file"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB and optimize
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Optimize size
                max_size = 512
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buffer.getvalue()).decode()
                
                return ImageReference(
                    name=f"Custom {purpose.title()}",
                    purpose=purpose,
                    image_data=f"data:image/jpeg;base64,{img_b64}",
                    influence_weight=influence_weight,
                    prompt_enhancement=f"incorporating {purpose} reference styling from {Path(file_path).name}",
                    rarity_modifier=1.0 + (influence_weight * 0.5)
                )
        except Exception as e:
            raise ValueError(f"Failed to load reference from file: {e}")

# Example usage and testing
if __name__ == "__main__":
    engine = BananaNFTMultiImageEngine()
    
    print("🍌 BananaNFT Multi-Image Conditioning Engine Test")
    print("=" * 60)
    
    # Test multi-image prompt generation
    test_image_data = "test_base64_image_data"
    
    for rarity in ["common", "rare", "legendary"]:
        print(f"\n🎯 Testing {rarity.upper()} rarity conditioning:")
        
        multi_prompt = engine.generate_multi_image_prompt(
            base_image_data=test_image_data,
            style="bored_apes",
            target_rarity=rarity,
            creativity_boost=1.5 if rarity == "legendary" else 1.0
        )
        
        print(f"  • References: {len(multi_prompt.reference_images)}")
        print(f"  • Combined influence: {multi_prompt.combined_influence:.2f}")
        print(f"  • Rarity boost: {multi_prompt.estimated_rarity_boost:.2f}")
        print(f"  • Complexity: {multi_prompt.generation_complexity}/5")
        print(f"  • Prompt: {multi_prompt.text_prompt[:80]}...")
        
        # Test payload preparation
        payload = engine.prepare_nano_banana_payload(multi_prompt)
        content_items = len(payload["messages"][0]["content"])
        print(f"  • Nano-banana payload: {content_items} content items")
    
    print(f"\n✅ Multi-image conditioning system ready!")
    print(f"📚 Reference library: {sum(len(cat) for cat in engine.reference_library.values())} references")
    print(f"🎯 Strategies: {len(engine.conditioning_strategies)} rarity tiers")
    print(f"🚀 Ready to create unprecedented NFT uniqueness!")