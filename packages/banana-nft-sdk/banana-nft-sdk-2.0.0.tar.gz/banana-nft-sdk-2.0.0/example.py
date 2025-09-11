#!/usr/bin/env python3
"""
🦙 Recreate.ai NFT SDK Example

This example demonstrates how to use the Recreate NFT SDK to:
1. Generate a single styled image
2. Create a full NFT collection with rarity traits
3. Analyze the collection
4. Save everything to disk

Run this example after starting the Recreate backend server.
"""

import os
from pathlib import Path

# Create a sample image for testing
def create_sample_image():
    """Create a simple sample image for testing"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple colorful image
        img = Image.new('RGB', (512, 512), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw some simple shapes
        draw.rectangle([100, 100, 400, 400], fill='coral', outline='darkred', width=5)
        draw.ellipse([150, 150, 350, 350], fill='yellow', outline='orange', width=3)
        draw.polygon([(256, 180), (200, 300), (312, 300)], fill='lightgreen', outline='darkgreen')
        
        # Add some text
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
            draw.text((200, 350), "Sample Image", fill='black', font=font)
        except:
            draw.text((200, 350), "Sample Image", fill='black')
        
        img.save('sample_image.jpg', quality=85)
        print("✅ Created sample_image.jpg for testing")
        return True
        
    except ImportError:
        print("⚠️  PIL not available, creating simple image file...")
        # Create a placeholder file
        with open('sample_image.txt', 'w') as f:
            f.write("This is a placeholder image file for testing")
        return False


def main():
    """Main example function"""
    print("🦙 Recreate.ai NFT SDK Example")
    print("=" * 50)
    
    # Check if we have an API key
    api_key = os.getenv("RECREATE_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  No API key found!")
        print("Set RECREATE_API_KEY or OPENROUTER_API_KEY environment variable")
        print("Example: export RECREATE_API_KEY='your_openrouter_key'")
        print("\n💡 For testing, the SDK will use mock responses")
        api_key = "mock_key_for_testing"
    else:
        print(f"✅ Using API key: {api_key[:8]}...")
    
    # Create sample image if needed
    sample_image = "sample_image.jpg"
    if not Path(sample_image).exists():
        print(f"\n📸 Sample image not found, creating {sample_image}...")
        create_sample_image()
    
    try:
        # Import the SDK
        from recreate_nft import RecreateNFT, RaritySettings
        
        print("\n🔧 Initializing Recreate NFT client...")
        nft = RecreateNFT(
            api_key=api_key,
            provider="openrouter",
            backend_url="http://localhost:8000"
        )
        
        print("✅ Client initialized successfully!")
        
        # Example 1: Single Image Generation
        print("\n" + "="*50)
        print("📸 EXAMPLE 1: Single Image Generation")
        print("="*50)
        
        try:
            result = nft.create_image(
                image_path=sample_image,
                style="adventure_time",
                aspect_ratio="1:1"
            )
            
            output_file = "styled_adventure_time.jpg"
            result.save_image(output_file)
            
            print(f"✅ Created {result.style_id} styled image!")
            print(f"💾 Saved as: {output_file}")
            
        except Exception as e:
            print(f"❌ Single image generation failed: {e}")
        
        # Example 2: NFT Collection Generation
        print("\n" + "="*50)
        print("🚀 EXAMPLE 2: NFT Collection Generation")
        print("="*50)
        
        try:
            # Custom rarity settings
            rarity_settings = RaritySettings(
                common=50,
                uncommon=30,
                rare=15,
                legendary=5
            )
            
            print(f"🎨 Generating NFT collection...")
            print(f"   • Style: crypto_punks")
            print(f"   • Size: 20 NFTs") 
            print(f"   • Rarity: {rarity_settings.dict()}")
            
            collection = nft.create_collection(
                image_path=sample_image,
                style="crypto_punks",
                collection_size=20,
                name="Example Punk Collection",
                description="AI-generated punk-style NFT collection created with Recreate SDK",
                rarity_settings=rarity_settings,
                show_progress=True
            )
            
            print(f"\n✅ Collection generated successfully!")
            print(collection.summary())
            
            # Example 3: Collection Analysis
            print("\n" + "="*50)
            print("📊 EXAMPLE 3: Collection Analysis")
            print("="*50)
            
            # Analyze rarity distribution
            print("🔍 Rarity Analysis:")
            rarities = ["common", "uncommon", "rare", "legendary"]
            for rarity in rarities:
                tokens = collection.get_tokens_by_rarity(rarity)
                percentage = collection.get_rarity_percentage(rarity)
                print(f"   • {rarity.title():<10}: {len(tokens):2} NFTs ({percentage:4.1f}%)")
            
            # Find most valuable NFTs
            if collection.legendary_tokens:
                rarest = max(collection.legendary_tokens, key=lambda t: len(t.traits))
                print(f"\n🏆 Rarest NFT: #{rarest.token_id}")
                print(f"   • Rarity: {rarest.rarity}")
                print(f"   • Traits: {len(rarest.traits)}")
                print(f"   • Color: {rarest.rarity_color}")
                for trait in rarest.traits[:3]:  # Show first 3 traits
                    print(f"     - {trait}")
            
            # Example 4: Save Collection
            print("\n" + "="*50)
            print("💾 EXAMPLE 4: Save Collection to Disk")
            print("="*50)
            
            output_dir = "example_nft_collection"
            print(f"📁 Saving collection to: {output_dir}/")
            
            nft.save_collection(collection, output_dir)
            
            # Show what was created
            output_path = Path(output_dir)
            if output_path.exists():
                files = list(output_path.glob("*"))
                print(f"✅ Created {len(files)} files:")
                for file in sorted(files)[:5]:  # Show first 5 files
                    print(f"   • {file.name}")
                if len(files) > 5:
                    print(f"   ... and {len(files) - 5} more files")
            
            # Example 5: Mock Deployment
            print("\n" + "="*50)
            print("🌐 EXAMPLE 5: Blockchain Deployment (Mock)")
            print("="*50)
            
            try:
                deployment = nft.deploy_collection(collection, "ethereum")
                
                if deployment.success:
                    print(f"✅ {deployment.message}")
                    print(f"🏗️  Contract: {deployment.contract_address}")
                    print(f"🌊 OpenSea: {deployment.opensea_url}")
                    print(f"💰 Cost: {deployment.deployment_cost}")
                else:
                    print(f"❌ Deployment failed: {deployment.error_message}")
                    
            except Exception as e:
                print(f"❌ Deployment failed: {e}")
            
            print("\n" + "="*50)
            print("🎉 Example completed successfully!")
            print("="*50)
            print(f"📁 Check the '{output_dir}/' folder for your NFT collection")
            print("🖼️  Individual NFT images and metadata are ready for OpenSea")
            print("🦙 Happy NFT creating with Recreate.ai!")
            
        except Exception as e:
            print(f"❌ Collection generation failed: {e}")
            print("💡 Make sure the Recreate backend is running on localhost:8000")
    
    except ImportError:
        print("❌ Recreate NFT SDK not installed!")
        print("Install it with: pip install -e .")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()