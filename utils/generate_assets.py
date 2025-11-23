from PIL import Image, ImageDraw
import random
import os

def generate_torn_edge(width, height, top_torn=False, bottom_torn=False, color=(255, 255, 255, 255)):
    # Create a transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Define the polygon points
    points = []

    # Top edge
    if top_torn:
        points.append((0, 0))
        current_x = 0
        while current_x < width:
            next_x = min(width, current_x + random.randint(5, 15))
            y_offset = random.randint(0, 15)
            points.append((next_x, y_offset))
            current_x = next_x
    else:
        points.append((0, 0))
        points.append((width, 0))

    # Bottom edge
    if bottom_torn:
        current_x = width
        while current_x > 0:
            next_x = max(0, current_x - random.randint(5, 15))
            y_offset = height - random.randint(0, 15)
            points.append((next_x, y_offset))
            current_x = next_x
    else:
        points.append((width, height))
        points.append((0, height))

    # Close the polygon
    draw.polygon(points, fill=color)

    return img

def main():
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    # Generate torn_paper_top (torn at bottom)
    img_top = generate_torn_edge(1920, 100, top_torn=False, bottom_torn=True)
    img_top.save(os.path.join(assets_dir, "torn_paper_top.png"))
    print("Generated torn_paper_top.png")

    # Generate torn_paper_bottom (torn at top)
    img_bottom = generate_torn_edge(1920, 100, top_torn=True, bottom_torn=False)
    img_bottom.save(os.path.join(assets_dir, "torn_paper_bottom.png"))
    print("Generated torn_paper_bottom.png")

    # Generate torn_paper_divider (torn at both)
    img_divider = generate_torn_edge(1920, 100, top_torn=True, bottom_torn=True)
    img_divider.save(os.path.join(assets_dir, "torn_paper_divider.png"))
    print("Generated torn_paper_divider.png")

if __name__ == "__main__":
    main()
