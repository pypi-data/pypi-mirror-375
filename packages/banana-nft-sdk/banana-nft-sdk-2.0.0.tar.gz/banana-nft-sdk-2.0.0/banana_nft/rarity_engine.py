#!/usr/bin/env python3
"""
🍌 BananaNFT Rarity Engine - Mathematical Precision Trait System

Revolutionary trait generation system that creates homogeneous collections
with mathematical rarity control using nano-banana AI conditioning.
"""

import random
import hashlib
import json
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

class RarityTier(Enum):
    LEGENDARY = "legendary"     # 0.1-1%
    EPIC = "epic"              # 1-5%  
    RARE = "rare"              # 5-15%
    UNCOMMON = "uncommon"       # 15-35%
    COMMON = "common"          # 35-80%

@dataclass
class TraitElement:
    """Individual trait with market intelligence"""
    name: str
    category: str
    rarity_weight: float        # 0.0-1.0, lower = rarer
    prompt_fragment: str        # Nano-banana prompt component
    visual_impact: float        # How much it changes the image (0.0-1.0)
    market_appeal: float        # Historical performance (0.0-1.0)
    compatibility: List[str]    # Compatible with these traits
    exclusions: List[str]       # Cannot combine with these traits

@dataclass
class NFTMetadata:
    """Complete NFT metadata for OpenSea compatibility"""
    token_id: int
    name: str
    description: str
    image_url: str
    external_url: Optional[str]
    animation_url: Optional[str]
    attributes: List[Dict[str, Any]]
    rarity_tier: RarityTier
    rarity_score: float
    nano_banana_prompt: str
    generation_params: Dict[str, Any]

class BananaNFTRarityEngine:
    """
    🧠 Revolutionary rarity engine for mathematical precision collections
    
    Creates homogeneous collections where:
    - Every NFT shares the same base style/theme
    - Traits create natural rarity distribution  
    - Nano-banana AI ensures artistic coherence
    - JSON metadata auto-generated for OpenSea
    """
    
    def __init__(self):
        self.trait_database = self._initialize_comprehensive_traits()
        self.compatibility_matrix = self._build_compatibility_matrix()
        self.successful_combinations = {}
        self.generation_history = []
        
    def _initialize_comprehensive_traits(self) -> Dict[str, Dict[str, TraitElement]]:
        """Initialize the most comprehensive trait system ever built"""
        
        return {
            # Base character/style (always present, homogeneous across collection)
            "base_character": {
                "human": TraitElement("Human", "base_character", 1.0, "human character", 1.0, 0.85, [], []),
                "ape": TraitElement("Ape", "base_character", 1.0, "anthropomorphic ape character", 1.0, 0.92, [], []),
                "robot": TraitElement("Robot", "base_character", 1.0, "futuristic robot character", 1.0, 0.88, [], []),
                "alien": TraitElement("Alien", "base_character", 1.0, "extraterrestrial being", 1.0, 0.87, [], []),
                "penguin": TraitElement("Penguin", "base_character", 1.0, "cute anthropomorphic penguin", 1.0, 0.83, [], [])
            },
            
            # Backgrounds (major rarity driver)
            "backgrounds": {
                "blue_gradient": TraitElement("Blue Gradient", "backgrounds", 0.40, "soft blue gradient background", 0.3, 0.78, [], []),
                "green_solid": TraitElement("Green Solid", "backgrounds", 0.25, "solid green background", 0.3, 0.80, [], []),
                "purple_cosmic": TraitElement("Purple Cosmic", "backgrounds", 0.15, "cosmic purple nebula background", 0.6, 0.85, [], []),
                "rainbow_hologram": TraitElement("Rainbow Hologram", "backgrounds", 0.08, "shimmering rainbow holographic background", 0.8, 0.90, [], []),
                "gold_luxury": TraitElement("Gold Luxury", "backgrounds", 0.05, "luxurious gold leaf background", 0.7, 0.92, [], []),
                "diamond_sparkle": TraitElement("Diamond Sparkle", "backgrounds", 0.03, "sparkling diamond crystal background", 0.9, 0.95, [], []),
                "void_dimension": TraitElement("Void Dimension", "backgrounds", 0.02, "interdimensional void background", 0.9, 0.96, [], []),
                "time_warp": TraitElement("Time Warp", "backgrounds", 0.01, "time-space warping background", 1.0, 0.98, [], []),
                "genesis_light": TraitElement("Genesis Light", "backgrounds", 0.005, "primordial creation light background", 1.0, 0.99, [], [])
            },
            
            # Eyes (personality and rarity)
            "eyes": {
                "normal_brown": TraitElement("Brown Eyes", "eyes", 0.35, "warm brown eyes", 0.2, 0.75, [], []),
                "blue_bright": TraitElement("Bright Blue", "eyes", 0.25, "piercing bright blue eyes", 0.3, 0.82, [], []),
                "green_emerald": TraitElement("Emerald Green", "eyes", 0.18, "brilliant emerald green eyes", 0.4, 0.85, [], []),
                "violet_mystic": TraitElement("Mystic Violet", "eyes", 0.12, "mystical violet glowing eyes", 0.6, 0.88, [], []),
                "gold_divine": TraitElement("Divine Gold", "eyes", 0.06, "divine golden radiant eyes", 0.8, 0.92, [], []),
                "silver_chrome": TraitElement("Chrome Silver", "eyes", 0.025, "liquid chrome silver eyes", 0.7, 0.94, [], []),
                "rainbow_prism": TraitElement("Prism Rainbow", "eyes", 0.015, "prismatic rainbow shifting eyes", 0.9, 0.96, [], []),
                "void_black": TraitElement("Void Black", "eyes", 0.008, "infinite void black eyes", 0.9, 0.97, [], []),
                "cosmic_galaxy": TraitElement("Galaxy Cosmic", "eyes", 0.003, "swirling galaxy universe eyes", 1.0, 0.99, [], [])
            },
            
            # Accessories (major rarity and value driver)
            "accessories": {
                "none": TraitElement("None", "accessories", 0.30, "no accessories", 0.0, 0.70, [], []),
                "simple_hat": TraitElement("Simple Hat", "accessories", 0.20, "wearing a simple hat", 0.2, 0.78, [], []),
                "cool_sunglasses": TraitElement("Cool Sunglasses", "accessories", 0.15, "wearing cool sunglasses", 0.3, 0.82, [], []),
                "gold_chain": TraitElement("Gold Chain", "accessories", 0.12, "wearing a gold chain necklace", 0.4, 0.85, [], []),
                "diamond_earrings": TraitElement("Diamond Earrings", "accessories", 0.08, "wearing sparkling diamond earrings", 0.5, 0.88, [], []),
                "laser_visor": TraitElement("Laser Visor", "accessories", 0.05, "wearing futuristic laser visor", 0.7, 0.91, [], []),
                "crown_royal": TraitElement("Royal Crown", "accessories", 0.03, "wearing a majestic royal crown", 0.8, 0.94, [], []),
                "halo_divine": TraitElement("Divine Halo", "accessories", 0.015, "radiating divine golden halo", 0.9, 0.96, [], []),
                "phoenix_crown": TraitElement("Phoenix Crown", "accessories", 0.008, "wearing mythical phoenix feather crown", 1.0, 0.98, [], []),
                "time_circlet": TraitElement("Time Circlet", "accessories", 0.002, "wearing ancient time manipulation circlet", 1.0, 0.99, [], [])
            },
            
            # Expressions (personality traits)
            "expressions": {
                "neutral_calm": TraitElement("Calm Neutral", "expressions", 0.25, "calm neutral expression", 0.2, 0.78, [], []),
                "happy_smile": TraitElement("Happy Smile", "expressions", 0.20, "warm happy smile", 0.3, 0.81, [], []),
                "confident_smirk": TraitElement("Confident Smirk", "expressions", 0.18, "confident knowing smirk", 0.3, 0.83, [], []),
                "mysterious_gaze": TraitElement("Mysterious Gaze", "expressions", 0.15, "mysterious piercing gaze", 0.4, 0.85, [], []),
                "fierce_determination": TraitElement("Fierce Determination", "expressions", 0.10, "fierce determined expression", 0.5, 0.87, [], []),
                "serene_wisdom": TraitElement("Serene Wisdom", "expressions", 0.08, "serene ancient wisdom expression", 0.6, 0.90, [], []),
                "playful_wink": TraitElement("Playful Wink", "expressions", 0.03, "playful mischievous wink", 0.4, 0.88, [], []),
                "cosmic_enlightenment": TraitElement("Cosmic Enlightenment", "expressions", 0.008, "transcendent cosmic enlightenment", 0.8, 0.95, [], []),
                "divine_grace": TraitElement("Divine Grace", "expressions", 0.002, "radiating divine grace and power", 1.0, 0.98, [], [])
            },
            
            # Special effects (visual enhancement)
            "special_effects": {
                "none": TraitElement("None", "special_effects", 0.45, "no special effects", 0.0, 0.70, [], []),
                "soft_glow": TraitElement("Soft Glow", "special_effects", 0.20, "subtle soft glow aura", 0.3, 0.82, [], []),
                "neon_outline": TraitElement("Neon Outline", "special_effects", 0.15, "vibrant neon outline effect", 0.5, 0.84, [], []),
                "holographic_shimmer": TraitElement("Holographic Shimmer", "special_effects", 0.10, "holographic shimmer effects", 0.6, 0.87, [], []),
                "energy_crackling": TraitElement("Energy Crackling", "special_effects", 0.06, "crackling energy lightning", 0.7, 0.90, [], []),
                "particle_swirl": TraitElement("Particle Swirl", "special_effects", 0.025, "swirling magical particles", 0.8, 0.93, [], []),
                "dimensional_rift": TraitElement("Dimensional Rift", "special_effects", 0.01, "reality-bending dimensional rift", 0.9, 0.96, [], []),
                "time_distortion": TraitElement("Time Distortion", "special_effects", 0.003, "time-space distortion waves", 1.0, 0.98, [], [])
            }
        }
    
    def _build_compatibility_matrix(self) -> Dict[str, List[str]]:
        """Build trait compatibility for natural combinations"""
        return {
            # Backgrounds that work well together (none - backgrounds are exclusive)
            "time_warp": ["cosmic_galaxy", "divine_grace", "time_circlet", "time_distortion"],
            "void_dimension": ["void_black", "cosmic_enlightenment", "dimensional_rift"],
            "diamond_sparkle": ["diamond_earrings", "divine_halo", "rainbow_prism"],
            
            # Accessories that enhance each other
            "phoenix_crown": ["cosmic_galaxy", "divine_grace", "energy_crackling"],
            "divine_halo": ["serene_wisdom", "divine_grace", "soft_glow"],
            "time_circlet": ["cosmic_enlightenment", "time_warp", "time_distortion"]
        }
    
    def calculate_mathematical_rarity(self, trait_combination: Dict[str, TraitElement]) -> Tuple[RarityTier, float]:
        """Calculate precise mathematical rarity"""
        
        # Calculate probability product (excluding base character)
        total_probability = 1.0
        for category, trait in trait_combination.items():
            if category != "base_character":  # Base doesn't affect rarity in homogeneous collections
                total_probability *= trait.rarity_weight
        
        # Apply compatibility bonuses/penalties
        compatibility_bonus = self._calculate_compatibility_bonus(trait_combination)
        adjusted_probability = total_probability * compatibility_bonus
        
        # Convert to rarity score (0-100, higher = rarer)
        rarity_score = max(0, 100 - (adjusted_probability * 100))
        
        # Determine tier
        if adjusted_probability <= 0.001:
            return RarityTier.LEGENDARY, rarity_score
        elif adjusted_probability <= 0.01:
            return RarityTier.EPIC, rarity_score
        elif adjusted_probability <= 0.05:
            return RarityTier.RARE, rarity_score
        elif adjusted_probability <= 0.20:
            return RarityTier.UNCOMMON, rarity_score
        else:
            return RarityTier.COMMON, rarity_score
    
    def _calculate_compatibility_bonus(self, traits: Dict[str, TraitElement]) -> float:
        """Calculate compatibility bonus for trait synergy"""
        bonus = 1.0
        trait_names = [trait.name.lower().replace(" ", "_") for trait in traits.values()]
        
        # Check for synergistic combinations
        for trait_name in trait_names:
            if trait_name in self.compatibility_matrix:
                compatible_traits = self.compatibility_matrix[trait_name]
                for compatible in compatible_traits:
                    if compatible in trait_names:
                        bonus *= 0.8  # Make combination rarer (lower probability)
        
        return bonus
    
    def generate_homogeneous_collection(
        self,
        collection_size: int,
        base_character_type: str = "ape",  # Consistent across collection
        rarity_distribution: Optional[Dict[RarityTier, float]] = None,
        custom_trait_weights: Optional[Dict[str, Dict[str, float]]] = None
    ) -> List[NFTMetadata]:
        """
        Generate mathematically precise homogeneous collection
        
        Args:
            collection_size: Total NFTs to generate
            base_character_type: Consistent character type across all NFTs
            rarity_distribution: Custom rarity percentages
            custom_trait_weights: Override default trait probabilities
        """
        
        # Default rarity distribution (inspired by successful collections)
        if rarity_distribution is None:
            rarity_distribution = {
                RarityTier.COMMON: 0.50,      # 50%
                RarityTier.UNCOMMON: 0.30,    # 30% 
                RarityTier.RARE: 0.15,        # 15%
                RarityTier.EPIC: 0.04,        # 4%
                RarityTier.LEGENDARY: 0.01    # 1%
            }
        
        # Apply custom trait weights if provided
        if custom_trait_weights:
            self._apply_custom_weights(custom_trait_weights)
        
        # Generate collection plan
        collection_plan = self._create_collection_plan(collection_size, rarity_distribution)
        
        # Generate each NFT
        collection = []
        used_combinations = set()  # Ensure uniqueness
        
        for token_id, target_rarity in enumerate(collection_plan, 1):
            max_attempts = 50
            for attempt in range(max_attempts):
                
                # Generate trait combination
                traits = self._generate_targeted_traits(base_character_type, target_rarity)
                combination_hash = self._hash_trait_combination(traits)
                
                # Ensure uniqueness
                if combination_hash not in used_combinations:
                    used_combinations.add(combination_hash)
                    
                    # Calculate actual rarity
                    actual_rarity, rarity_score = self.calculate_mathematical_rarity(traits)
                    
                    # Generate nano-banana prompt
                    prompt = self._build_nano_banana_prompt(traits, token_id)
                    
                    # Create metadata
                    metadata = self._create_nft_metadata(
                        token_id=token_id,
                        traits=traits,
                        rarity_tier=actual_rarity,
                        rarity_score=rarity_score,
                        prompt=prompt,
                        base_character=base_character_type
                    )
                    
                    collection.append(metadata)
                    break
            else:
                # Fallback if couldn't find unique combination
                print(f"⚠️  Warning: Could not generate unique combination for token {token_id}")
        
        return collection
    
    def _create_collection_plan(self, size: int, distribution: Dict[RarityTier, float]) -> List[RarityTier]:
        """Create exact rarity plan for collection"""
        plan = []
        
        for rarity, percentage in distribution.items():
            count = int(size * percentage)
            plan.extend([rarity] * count)
        
        # Fill remainder with common
        while len(plan) < size:
            plan.append(RarityTier.COMMON)
        
        # Shuffle for random order
        random.shuffle(plan)
        return plan
    
    def _generate_targeted_traits(self, base_character: str, target_rarity: RarityTier) -> Dict[str, TraitElement]:
        """Generate traits that achieve target rarity"""
        
        traits = {
            "base_character": self.trait_database["base_character"][base_character]
        }
        
        # Select traits based on target rarity
        if target_rarity == RarityTier.LEGENDARY:
            # Ultra-rare combinations
            traits["backgrounds"] = self._select_trait_by_max_weight("backgrounds", 0.01)
            traits["eyes"] = self._select_trait_by_max_weight("eyes", 0.008)
            traits["accessories"] = self._select_trait_by_max_weight("accessories", 0.01)
            traits["expressions"] = self._select_trait_by_max_weight("expressions", 0.01)
            traits["special_effects"] = self._select_trait_by_max_weight("special_effects", 0.01)
            
        elif target_rarity == RarityTier.EPIC:
            # Very rare combinations
            traits["backgrounds"] = self._select_trait_by_max_weight("backgrounds", 0.05)
            traits["eyes"] = self._select_trait_by_max_weight("eyes", 0.03)
            traits["accessories"] = self._select_trait_by_max_weight("accessories", 0.05)
            traits["expressions"] = self._select_trait_by_max_weight("expressions", 0.05)
            if random.random() < 0.7:  # 70% chance for special effect
                traits["special_effects"] = self._select_trait_by_max_weight("special_effects", 0.03)
            
        elif target_rarity == RarityTier.RARE:
            # Rare combinations
            traits["backgrounds"] = self._select_trait_by_max_weight("backgrounds", 0.15)
            traits["eyes"] = self._select_trait_by_max_weight("eyes", 0.15)
            traits["accessories"] = self._select_trait_by_max_weight("accessories", 0.15)
            traits["expressions"] = self._select_trait_by_max_weight("expressions", 0.15)
            if random.random() < 0.4:  # 40% chance for special effect
                traits["special_effects"] = self._select_trait_by_max_weight("special_effects", 0.15)
                
        elif target_rarity == RarityTier.UNCOMMON:
            # Uncommon combinations  
            traits["backgrounds"] = self._select_trait_by_max_weight("backgrounds", 0.30)
            traits["eyes"] = self._select_trait_by_max_weight("eyes", 0.30)
            traits["accessories"] = self._select_trait_by_max_weight("accessories", 0.30)
            traits["expressions"] = self._select_trait_by_max_weight("expressions", 0.30)
            if random.random() < 0.2:  # 20% chance for special effect
                traits["special_effects"] = self._select_trait_by_max_weight("special_effects", 0.25)
                
        else:  # COMMON
            # Common combinations
            traits["backgrounds"] = self._select_trait_by_min_weight("backgrounds", 0.25)
            traits["eyes"] = self._select_trait_by_min_weight("eyes", 0.25)  
            traits["accessories"] = self._select_trait_by_min_weight("accessories", 0.15)
            traits["expressions"] = self._select_trait_by_min_weight("expressions", 0.20)
            # Common rarely gets special effects (10% chance)
            if random.random() < 0.1:
                traits["special_effects"] = self._select_trait_by_min_weight("special_effects", 0.20)
        
        return traits
    
    def _select_trait_by_max_weight(self, category: str, max_weight: float) -> TraitElement:
        """Select trait with weight <= max_weight"""
        valid_traits = [
            trait for trait in self.trait_database[category].values()
            if trait.rarity_weight <= max_weight
        ]
        return random.choice(valid_traits) if valid_traits else random.choice(list(self.trait_database[category].values()))
    
    def _select_trait_by_min_weight(self, category: str, min_weight: float) -> TraitElement:
        """Select trait with weight >= min_weight (common traits)"""
        valid_traits = [
            trait for trait in self.trait_database[category].values()
            if trait.rarity_weight >= min_weight
        ]
        return random.choice(valid_traits) if valid_traits else random.choice(list(self.trait_database[category].values()))
    
    def _build_nano_banana_prompt(self, traits: Dict[str, TraitElement], token_id: int) -> str:
        """Build sophisticated nano-banana prompt for homogeneous generation"""
        
        # Start with base character transformation
        base_trait = traits["base_character"]
        base_prompt = f"Transform into detailed {base_trait.prompt_fragment}"
        
        # Add trait-specific details
        trait_details = []
        for category, trait in traits.items():
            if category != "base_character" and trait.name != "None":
                trait_details.append(trait.prompt_fragment)
        
        # Build comprehensive prompt
        if trait_details:
            full_prompt = f"{base_prompt}, {', '.join(trait_details)}"
        else:
            full_prompt = base_prompt
        
        # Add quality and style consistency modifiers
        quality_modifiers = [
            "ultra high quality 8K digital art",
            "perfect professional lighting and shadows", 
            "consistent art style across entire collection",
            "trending on SuperRare and Foundation",
            "museum-quality masterpiece"
        ]
        
        # Add iteration-based enhancements
        iteration_bonus = (token_id % 100) / 100  # Cycle through enhancement levels
        if iteration_bonus > 0.8:  # Top 20% get maximum enhancement
            full_prompt += f". {'. '.join(quality_modifiers)}"
        elif iteration_bonus > 0.5:  # Middle tier gets partial enhancement
            full_prompt += f". {random.choice(quality_modifiers)}"
        
        return full_prompt
    
    def _create_nft_metadata(
        self,
        token_id: int,
        traits: Dict[str, TraitElement],
        rarity_tier: RarityTier,
        rarity_score: float,
        prompt: str,
        base_character: str
    ) -> NFTMetadata:
        """Create complete OpenSea-compatible metadata"""
        
        # Build attributes array
        attributes = []
        for category, trait in traits.items():
            if trait.name != "None":  # Skip "None" traits
                attributes.append({
                    "trait_type": category.replace("_", " ").title(),
                    "value": trait.name,
                    "rarity": trait.rarity_weight
                })
        
        # Add computed attributes
        attributes.extend([
            {"trait_type": "Rarity Tier", "value": rarity_tier.value.title()},
            {"trait_type": "Rarity Score", "value": round(rarity_score, 2)},
            {"trait_type": "Generation", "value": "Nano-Banana AI"},
            {"trait_type": "Collection Type", "value": "Homogeneous"}
        ])
        
        return NFTMetadata(
            token_id=token_id,
            name=f"BananaNFT #{token_id:04d}",
            description=f"AI-generated {base_character.title()} NFT from the BananaNFT collection. "
                       f"Created using advanced nano-banana multimodal AI with mathematical rarity precision. "
                       f"Rarity: {rarity_tier.value.title()} (Score: {rarity_score:.2f})",
            image_url=f"https://banana-nft.ai/images/{token_id:04d}.png",
            external_url="https://banana-nft.ai",
            animation_url=None,
            attributes=attributes,
            rarity_tier=rarity_tier,
            rarity_score=rarity_score,
            nano_banana_prompt=prompt,
            generation_params={
                "model": "google/nano-banana",
                "creativity_boost": 1.0 + (rarity_score / 100),
                "chain_iterations": min(3, int(rarity_score / 30)),
                "temperature": 0.7 + (rarity_score / 200)
            }
        )
    
    def _hash_trait_combination(self, traits: Dict[str, TraitElement]) -> str:
        """Create hash for uniqueness checking"""
        trait_string = "|".join([f"{cat}:{trait.name}" for cat, trait in sorted(traits.items())])
        return hashlib.md5(trait_string.encode()).hexdigest()
    
    def _apply_custom_weights(self, custom_weights: Dict[str, Dict[str, float]]):
        """Apply custom trait weights to the database"""
        for category, weights in custom_weights.items():
            if category in self.trait_database:
                for trait_name, weight in weights.items():
                    for trait in self.trait_database[category].values():
                        if trait.name.lower().replace(" ", "_") == trait_name:
                            trait.rarity_weight = weight
    
    def export_collection_json(self, collection: List[NFTMetadata], output_file: str = "collection_metadata.json"):
        """Export collection metadata as JSON for OpenSea integration"""
        collection_data = {
            "collection_info": {
                "name": "BananaNFT Collection",
                "description": "Revolutionary AI-generated NFT collection powered by nano-banana multimodal AI",
                "total_supply": len(collection),
                "generation_method": "Mathematical Rarity with Nano-Banana AI"
            },
            "rarity_distribution": self._calculate_rarity_distribution(collection),
            "tokens": [asdict(nft) for nft in collection]
        }
        
        with open(output_file, 'w') as f:
            json.dump(collection_data, f, indent=2, default=str)
        
        print(f"✅ Exported collection metadata to {output_file}")
        return collection_data
    
    def _calculate_rarity_distribution(self, collection: List[NFTMetadata]) -> Dict[str, Dict[str, Any]]:
        """Calculate final rarity distribution statistics"""
        distribution = defaultdict(int)
        rarity_scores = defaultdict(list)
        
        for nft in collection:
            tier = nft.rarity_tier.value
            distribution[tier] += 1
            rarity_scores[tier].append(nft.rarity_score)
        
        stats = {}
        total = len(collection)
        for tier, count in distribution.items():
            stats[tier] = {
                "count": count,
                "percentage": round((count / total) * 100, 2),
                "avg_rarity_score": round(sum(rarity_scores[tier]) / len(rarity_scores[tier]), 2),
                "max_rarity_score": round(max(rarity_scores[tier]), 2) if rarity_scores[tier] else 0
            }
        
        return stats


# Example usage and testing
if __name__ == "__main__":
    engine = BananaNFTRarityEngine()
    
    print("🍌 BananaNFT Rarity Engine Test")
    print("=" * 50)
    
    # Generate small test collection
    collection = engine.generate_homogeneous_collection(
        collection_size=20,
        base_character_type="ape",  # Homogeneous ape collection
        custom_trait_weights={
            "backgrounds": {
                "blue_gradient": 0.5,      # Make blue more common
                "diamond_sparkle": 0.01    # Keep diamond ultra-rare
            }
        }
    )
    
    # Display results
    rarity_counts = defaultdict(int)
    for nft in collection:
        rarity_counts[nft.rarity_tier.value] += 1
    
    print("📊 Generated Collection:")
    for tier, count in rarity_counts.items():
        percentage = (count / len(collection)) * 100
        print(f"  • {tier.title()}: {count} NFTs ({percentage:.1f}%)")
    
    print(f"\n🏆 Most Rare NFT:")
    rarest = max(collection, key=lambda x: x.rarity_score)
    print(f"  • Token #{rarest.token_id}: {rarest.rarity_tier.value.title()}")
    print(f"  • Rarity Score: {rarest.rarity_score:.2f}")
    print(f"  • Traits: {len(rarest.attributes)} unique traits")
    print(f"  • Prompt: {rarest.nano_banana_prompt[:100]}...")
    
    # Export collection
    engine.export_collection_json(collection, "test_collection.json")
    print(f"\n✅ Test collection exported successfully!")