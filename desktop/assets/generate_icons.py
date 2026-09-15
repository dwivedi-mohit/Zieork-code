"""Generate multi-resolution PNG and Windows ICO icons for Zieork Desktop App."""
import os
from PIL import Image, ImageDraw

def create_zieork_icon():
    size = (512, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Rounded rectangle squircle
    # Corner radius ~110px
    x0, y0, x1, y1 = 20, 20, 492, 492
    radius = 110
    
    # Outer glow / border
    draw.rounded_rectangle([x0-4, y0-4, x1+4, y1+4], radius=radius+4, fill=(67, 56, 202, 100))
    
    # Dark gradient-like background
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=(15, 23, 42, 255), outline=(99, 102, 241, 255), width=6)
    
    # Inner subtle background plate
    draw.rounded_rectangle([x0+12, y0+12, x1-12, y1-12], radius=radius-10, fill=(24, 20, 56, 255))

    # 2. Concentric neural rings
    cx, cy = 256, 256
    draw.ellipse([cx-170, cy-170, cx+170, cy+170], outline=(79, 70, 229, 90), width=3)
    draw.ellipse([cx-120, cy-120, cx+120, cy+120], outline=(168, 85, 247, 80), width=2)
    draw.ellipse([cx-70, cy-70, cx+70, cy+70], outline=(56, 189, 248, 70), width=2)

    # 3. Dynamic Lightning Bolt points
    # Sharp polygon representing the Zieork neural thunderbolt
    bolt_points = [
        (280, 80),   # top point
        (150, 260),  # left middle
        (246, 260),  # inner notch
        (210, 432),  # bottom sharp point
        (362, 236),  # right middle
        (266, 236)   # right inner notch
    ]
    
    # Glow shadow behind bolt
    glow_offsets = [(-3, -3), (3, 3), (-2, 2), (2, -2)]
    for ox, oy in glow_offsets:
        glow_pts = [(x + ox, y + oy) for x, y in bolt_points]
        draw.polygon(glow_pts, fill=(168, 85, 247, 80))

    # Main vibrant bolt
    draw.polygon(bolt_points, fill=(245, 158, 11, 255), outline=(255, 255, 255, 255), width=4)

    # Core inner accent
    inner_bolt = [
        (275, 120),
        (185, 250),
        (250, 250),
        (225, 380),
        (325, 245),
        (260, 245)
    ]
    draw.polygon(inner_bolt, fill=(254, 240, 138, 220))

    # Energy nucleus
    draw.ellipse([cx-14, cy-14, cx+14, cy+14], fill=(255, 255, 255, 255), outline=(56, 189, 248, 255), width=3)

    return img

def main():
    assets_dir = os.path.dirname(os.path.abspath(__file__))
    img_512 = create_zieork_icon()
    
    # Save standard high-res PNG
    png_path = os.path.join(assets_dir, "icon.png")
    img_512.save(png_path, "PNG")
    print(f"Generated {png_path} (512x512)")

    # Save multiple sizes for Linux desktop icons
    sizes = [256, 128, 64, 48, 32, 16]
    ico_images = [img_512]
    for s in sizes:
        resized = img_512.resize((s, s), Image.Resampling.LANCZOS)
        out_path = os.path.join(assets_dir, f"icon_{s}x{s}.png")
        resized.save(out_path, "PNG")
        ico_images.append(resized)

    # Save Windows multi-resolution ICO
    ico_path = os.path.join(assets_dir, "icon.ico")
    img_512.save(ico_path, format="ICO", sizes=[(s, s) for s in [256, 128, 64, 48, 32, 16]])
    print(f"Generated Windows {ico_path}")

if __name__ == "__main__":
    main()
