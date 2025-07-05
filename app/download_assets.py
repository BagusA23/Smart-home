import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io

def create_assets_folder():
    """Create assets folder if it doesn't exist"""
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Created {assets_dir} directory")
    return assets_dir

def create_banner_image(assets_dir):
    """Create a custom banner image"""
    # Create a banner image (800x100)
    width, height = 800, 100
    
    # Create gradient background
    img = Image.new('RGB', (width, height), color='#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Create gradient effect
    for i in range(height):
        color_value = int(26 + (i / height) * 50)  # Gradient from dark to lighter
        color = (color_value, color_value + 20, color_value + 40)
        draw.line([(0, i), (width, i)], fill=color)
    
    # Add text overlay
    try:
        # Try to use a better font if available
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add title text
    title_text = "Smart Home Dashboard"
    draw.text((50, 25), title_text, fill='white', font=font_large)
    
    # Add subtitle
    subtitle_text = "Monitor dan kontrol perangkat rumah pintar Anda"
    draw.text((50, 55), subtitle_text, fill='#cccccc', font=font_small)
    
    # Add home icon (simple house shape)
    # House outline
    house_points = [
        (750, 70), (770, 50), (790, 70),  # Roof
        (790, 85), (750, 85), (750, 70)   # Base
    ]
    draw.polygon(house_points, outline='white', width=2)
    
    # Door
    draw.rectangle([765, 75, 775, 85], outline='white', width=1)
    
    # Save the image
    banner_path = os.path.join(assets_dir, "banner.png")
    img.save(banner_path)
    print(f"Created banner image: {banner_path}")
    return banner_path

def create_home_icon(assets_dir):
    """Create a home icon image"""
    # Create a 60x60 home icon
    size = 60
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Draw house
    # Roof (triangle)
    roof_points = [(10, 30), (30, 10), (50, 30)]
    draw.polygon(roof_points, fill='#4a90e2', outline='#357abd', width=2)
    
    # House body (rectangle)
    draw.rectangle([15, 30, 45, 50], fill='#5ba3f5', outline='#357abd', width=2)
    
    # Door
    draw.rectangle([25, 40, 35, 50], fill='#8b4513', outline='#654321', width=1)
    
    # Door knob
    draw.ellipse([32, 44, 34, 46], fill='#ffd700')
    
    # Windows
    draw.rectangle([18, 35, 23, 40], fill='#87ceeb', outline='#357abd', width=1)
    draw.rectangle([37, 35, 42, 40], fill='#87ceeb', outline='#357abd', width=1)
    
    # Save the image
    icon_path = os.path.join(assets_dir, "home_icon.png")
    img.save(icon_path)
    print(f"Created home icon: {icon_path}")
    return icon_path

def create_room_icons(assets_dir):
    """Create room-specific icons"""
    room_icons_dir = os.path.join(assets_dir, "room_icons")
    if not os.path.exists(room_icons_dir):
        os.makedirs(room_icons_dir)
    
    icons = {
        "bedroom.png": ("🛏️", "#ff6b9d"),
        "kitchen.png": ("🍳", "#ffa726"),
        "living_room.png": ("🛋️", "#42a5f5")
    }
    
    for filename, (emoji, color) in icons.items():
        # Create simple colored square with emoji-like design
        img = Image.new('RGBA', (40, 40), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw colored circle background
        draw.ellipse([5, 5, 35, 35], fill=color)
        
        icon_path = os.path.join(room_icons_dir, filename)
        img.save(icon_path)
        print(f"Created room icon: {icon_path}")

def main():
    """Main function to create all assets"""
    print("Creating Smart Home App Assets...")
    
    # Create assets directory
    assets_dir = create_assets_folder()
    
    # Create banner image
    create_banner_image(assets_dir)
    
    # Create home icon
    create_home_icon(assets_dir)
    
    # Create room icons
    create_room_icons(assets_dir)
    
    print("\n✅ All assets created successfully!")
    print("\nGenerated files:")
    print("- assets/banner.png")
    print("- assets/home_icon.png") 
    print("- assets/room_icons/bedroom.png")
    print("- assets/room_icons/kitchen.png")
    print("- assets/room_icons/living_room.png")
    
    print("\n🚀 Now you can run your main.py file!")

if __name__ == "__main__":
    main()