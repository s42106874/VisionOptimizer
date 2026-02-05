from PIL import Image, ImageDraw, ImageFont

def create_icon():
    # Create a 256x256 image with alpha channel
    size = (256, 256)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a gradient-like background circle
    # Outer circle
    draw.ellipse((10, 10, 246, 246), fill=(65, 105, 225), outline=(30, 144, 255), width=5)
    
    # Inner design - Shield shape approximate
    draw.polygon([(128, 40), (200, 70), (200, 160), (128, 220), (56, 160), (56, 70)], 
                 fill=(30, 30, 50), outline=(255, 255, 255), width=5)

    # Rocket (Simplified)
    draw.polygon([(128, 60), (150, 120), (128, 110), (106, 120)], fill=(255, 69, 0)) # Tip
    draw.rectangle((118, 110, 138, 170), fill=(220, 220, 220)) # Body
    draw.polygon([(118, 170), (100, 190), (128, 180), (156, 190), (138, 170)], fill=(255, 69, 0)) # Flame
    
    # Save as ICO
    img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("icon.ico created!")

if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("Pillow not installed. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "Pillow"])
        create_icon()
