import os
import random
from PIL import Image
import json

# Configuration
OUTPUT_DIR = "output"
IMAGE_DIR = f"{OUTPUT_DIR}/images"
METADATA_DIR = f"{OUTPUT_DIR}/metadata"
NUM_NFTS = 100
LAYER_DIRS = ["background", "skin", "drip", "mouth", "hat", "earring"]

# Ensure output directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

# Load all layer images
layers = {}
for layer in LAYER_DIRS:
    layer_path = f"layers/{layer}"
    layers[layer] = [f for f in os.listdir(layer_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Track generated combinations to ensure uniqueness
generated_combinations = set()

def generate_nft(nft_id):
    # Randomly select one trait per layer
    combination = []
    for layer in LAYER_DIRS:
        trait = random.choice(layers[layer])
        combination.append((layer, trait))
    
    # Check for uniqueness
    combination_key = tuple(combination)
    if combination_key in generated_combinations:
        return None  # Skip if combination already exists
    generated_combinations.add(combination_key)
    
    # Create composite image
    base_image = None
    reference_size = None
    for layer, trait in combination:
        trait_path = f"layers/{layer}/{trait}"
        img = Image.open(trait_path).convert("RGBA")
        
        # Set reference size from the first image
        if reference_size is None:
            reference_size = img.size
        # Resize if dimensions don't match
        if img.size != reference_size:
            img = img.resize(reference_size, Image.LANCZOS)
        
        if base_image is None:
            base_image = img
        else:
            base_image = Image.alpha_composite(base_image, img)
    
    # Save image
    image_path = f"{IMAGE_DIR}/{nft_id}.png"
    base_image.save(image_path, "PNG")
    
    # Create metadata (OpenSea standard)
    metadata = {
        "name": f"NFT #{nft_id}",
        "description": "A unique NFT from my collection",
        "image": f"ipfs://<CID>/{nft_id}.png",
        "attributes": [
            {"trait_type": layer, "value": os.path.splitext(trait)[0]}
            for layer, trait in combination
        ]
    }
    
    # Save metadata
    metadata_path = f"{METADATA_DIR}/{nft_id}.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
    
    return combination

# Generate NFTs
count = 0
nft_id = 1
while count < NUM_NFTS:
    result = generate_nft(nft_id)
    if result:
        print(f"Generated NFT #{nft_id}")
        count += 1
        nft_id += 1

print(f"Generated {count} unique NFTs!")