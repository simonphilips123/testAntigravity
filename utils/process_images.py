from PIL import Image, ImageDraw, ImageOps
import requests
from io import BytesIO
import os
import random

def generate_torn_mask(width, height):
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)

    # Create a polygon for the torn paper shape
    points = []

    # Top edge (torn)
    current_x = 0
    while current_x < width:
        next_x = min(width, current_x + random.randint(5, 15))
        y_offset = random.randint(0, 15)
        points.append((next_x, y_offset))
        current_x = next_x

    # Right edge (straight)
    points.append((width, height))

    # Bottom edge (torn)
    current_x = width
    while current_x > 0:
        next_x = max(0, current_x - random.randint(5, 15))
        y_offset = height - random.randint(0, 15)
        points.append((next_x, y_offset))
        current_x = next_x

    # Left edge (straight)
    points.append((0, 0))

    draw.polygon(points, fill=255)
    return mask

def process_product_image(input_path, save_path):
    img = None
    try:
        img = Image.open(input_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening {input_path}: {e}")
        return

    try:
        # Resize to standard size
        target_size = (400, 400)
        img = img.resize(target_size, Image.Resampling.LANCZOS)

        # Generate mask
        mask = generate_torn_mask(*target_size)

        # Apply mask
        output = Image.new('RGBA', target_size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask)

        # Save
        output.save(save_path, "PNG")
        print(f"Processed and saved: {save_path}")

    except Exception as e:
        print(f"Error processing/saving {save_path}: {e}")

def main():
    products_dir = "assets/products"
    if not os.path.exists(products_dir):
        os.makedirs(products_dir)

    # Process existing jpg images
    for i in range(1, 6):
        input_filename = f"{i}.jpg"
        input_path = os.path.join(products_dir, input_filename)
        output_filename = f"{i}.png"
        output_path = os.path.join(products_dir, output_filename)

        if os.path.exists(input_path):
             process_product_image(input_path, output_path)
        else:
            print(f"File not found: {input_path}")

    # Process logo
    logo_input = os.path.join(products_dir, "logo.jpg")
    logo_output = os.path.join(products_dir, "logo.png")
    if os.path.exists(logo_input):
        process_product_image(logo_input, logo_output)
    else:
        print(f"File not found: {logo_input}")

if __name__ == "__main__":
    main()
