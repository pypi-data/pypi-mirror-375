"""
Command line interface for Recreate NFT SDK
"""

import argparse
import os
import sys
from pathlib import Path

from .client import RecreateNFT
from .models import RaritySettings
from .exceptions import RecreateError


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🦙 Recreate.ai NFT SDK - Generate AI-powered NFT collections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single styled image
  recreate-nft create-image photo.jpg adventure_time --output styled.jpg
  
  # Generate NFT collection
  recreate-nft create-collection photo.jpg crypto_punks --size 40 --name "My Punks"
  
  # List available styles
  recreate-nft list-styles
  
  # Deploy collection (mock)
  recreate-nft deploy my_collection.json ethereum
        """
    )
    
    parser.add_argument("--api-key", 
                       help="AI provider API key (or set RECREATE_API_KEY env var)")
    parser.add_argument("--provider", default="openrouter",
                       choices=["openrouter", "gemini", "openai"],
                       help="AI provider to use")
    parser.add_argument("--backend-url", default="http://localhost:8000",
                       help="Recreate backend URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create image command
    create_img_parser = subparsers.add_parser("create-image", 
                                             help="Create single styled image")
    create_img_parser.add_argument("image", help="Path to input image")
    create_img_parser.add_argument("style", help="Style to apply")
    create_img_parser.add_argument("--aspect-ratio", default="auto",
                                  help="Target aspect ratio")
    create_img_parser.add_argument("--output", "-o", help="Output filename")
    
    # Create collection command  
    create_coll_parser = subparsers.add_parser("create-collection",
                                              help="Create NFT collection")
    create_coll_parser.add_argument("image", help="Path to base image")
    create_coll_parser.add_argument("style", help="Style to apply")
    create_coll_parser.add_argument("--size", "-s", type=int, default=40,
                                   help="Collection size (10-100)")
    create_coll_parser.add_argument("--name", "-n", help="Collection name")
    create_coll_parser.add_argument("--description", "-d", 
                                   help="Collection description")
    create_coll_parser.add_argument("--output-dir", "-o", default="nft_collection",
                                   help="Output directory")
    create_coll_parser.add_argument("--common", type=int, default=60,
                                   help="Common rarity percentage")
    create_coll_parser.add_argument("--uncommon", type=int, default=25, 
                                   help="Uncommon rarity percentage")
    create_coll_parser.add_argument("--rare", type=int, default=12,
                                   help="Rare rarity percentage") 
    create_coll_parser.add_argument("--legendary", type=int, default=3,
                                   help="Legendary rarity percentage")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy NFT collection")
    deploy_parser.add_argument("collection", help="Collection metadata JSON file")
    deploy_parser.add_argument("network", 
                              choices=["ethereum", "polygon", "base", "arbitrum"],
                              help="Target blockchain network")
    
    # List commands
    subparsers.add_parser("list-styles", help="List available styles")
    subparsers.add_parser("list-networks", help="List supported networks")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Get API key
    api_key = args.api_key or os.getenv("RECREATE_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    
    try:
        if args.command in ["create-image", "create-collection", "deploy"]:
            if not api_key:
                print("❌ Error: API key required. Set --api-key or RECREATE_API_KEY env var")
                sys.exit(1)
            
            nft = RecreateNFT(
                api_key=api_key,
                provider=args.provider,
                backend_url=args.backend_url
            )
        
        if args.command == "create-image":
            print(f"🎨 Creating styled image: {args.image} → {args.style}")
            
            result = nft.create_image(
                image_path=args.image,
                style=args.style,
                aspect_ratio=args.aspect_ratio
            )
            
            output_file = args.output or f"styled_{args.style}.jpg"
            result.save_image(output_file)
            
            print(f"✅ Styled image saved: {output_file}")
        
        elif args.command == "create-collection":
            print(f"🚀 Creating NFT collection: {args.size} × {args.style}")
            
            rarity_settings = RaritySettings(
                common=args.common,
                uncommon=args.uncommon, 
                rare=args.rare,
                legendary=args.legendary
            )
            
            collection = nft.create_collection(
                image_path=args.image,
                style=args.style,
                collection_size=args.size,
                name=args.name,
                description=args.description,
                rarity_settings=rarity_settings
            )
            
            nft.save_collection(collection, args.output_dir)
            
            print("\n" + collection.summary())
            print(f"\n💾 Collection saved to: {args.output_dir}/")
        
        elif args.command == "deploy":
            print(f"🚀 Deploying to {args.network}...")
            
            # Load collection metadata (simplified)
            import json
            with open(args.collection, 'r') as f:
                metadata = json.load(f)
            
            # Create minimal collection object for deployment
            from .models import NFTCollection
            collection = NFTCollection(
                collection_id=metadata["collection_id"],
                name=metadata["name"], 
                description=metadata["description"],
                style=metadata["style"],
                total_supply=metadata["total_supply"],
                tokens=[]  # Simplified for CLI
            )
            
            result = nft.deploy_collection(collection, args.network)
            
            if result.success:
                print(f"✅ {result.message}")
                if result.opensea_url:
                    print(f"🌊 OpenSea: {result.opensea_url}")
            else:
                print(f"❌ Deployment failed: {result.error_message}")
                sys.exit(1)
        
        elif args.command == "list-styles":
            print("🎨 Available Styles:")
            print()
            
            if api_key:
                nft = RecreateNFT(api_key=api_key, provider=args.provider)
                styles = nft.list_styles()
            else:
                from .models import STYLE_CATALOG
                styles = list(STYLE_CATALOG.keys())
            
            for style in sorted(styles):
                from .models import STYLE_CATALOG
                if style in STYLE_CATALOG:
                    info = STYLE_CATALOG[style]
                    print(f"  • {style:<15} - {info.name}")
                    print(f"    {info.description}")
                else:
                    print(f"  • {style}")
                print()
        
        elif args.command == "list-networks":
            print("🌐 Supported Networks:")
            print()
            networks = [
                ("ethereum", "Ethereum Mainnet"),
                ("polygon", "Polygon Network"), 
                ("base", "Base Network"),
                ("arbitrum", "Arbitrum Network")
            ]
            
            for network_id, name in networks:
                print(f"  • {network_id:<10} - {name}")
        
    except RecreateError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()