from PIL import Image, ImageDraw, ImageFont
import os
import time
import sys

# Extract frames from a GIF
def extract_gif_frames(gif, fillEmpty=False):
    frames = []
    try:
        while True:
            gif.seek(gif.tell() + 1)
            new_frame = Image.new('RGBA', gif.size)
            new_frame.paste(gif, (0, 0), gif.convert('RGBA'))
            
            if fillEmpty:
                canvas = Image.new('RGBA', new_frame.size, (255, 255, 255, 255))
                canvas.paste(new_frame, mask=new_frame)
                new_frame = canvas
            
            frames.append(new_frame)
    except EOFError:
        pass  # End of sequence
    return frames

# Save frames to files for debugging
def save_frames_list(frames):
    for i, frame in enumerate(frames):
        frame.save(f'test{i+1}.png', **frame.info)

# Convert a single image to ASCII
def convert_image_to_ascii(image):
    font = ImageFont.load_default()  # Load default bitmap monospaced font
    # Create a dummy image and get a drawing context
    dummy_image = Image.new('L', (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    # Get the size of a single character
    (chrx, chry) = draw.textbbox((0, 0), chr(32), font=font)[2:]

    # Calculate weights of ASCII chars
    weights = []
    for i in range(32, 127):
        chrImage = Image.new('L', (chrx, chry), color=0)
        d = ImageDraw.Draw(chrImage)
        d.text((0, 0), chr(i), fill=255, font=font)
        ctr = sum(chrImage.getpixel((x, y)) > 0 for y in range(chry) for x in range(chrx))
        weights.append(float(ctr) / (chrx * chry))
    
    output = ""
    (imgx, imgy) = image.size
    imgx = int(imgx / chrx)
    imgy = int(imgy / chry)

    image = image.resize((imgx, imgy), Image.BICUBIC)
    image = image.convert("L")  # Convert to grayscale
    pixels = image.load()

    for y in range(imgy):
        for x in range(imgx):
            w = float(pixels[x, y]) / 255 / intensity_multiplier
            # Find closest weight match
            k = min(range(len(weights)), key=lambda i: abs(weights[i] - w))
            output += chr(k + 32)
        output += "\n"
    return output

# Convert frames to ASCII
def convert_frames_to_ascii(frames):
    return [convert_image_to_ascii(frame) for frame in frames]

# Animate ASCII frames
def animate_ascii(ascii_frames, frame_pause=.02, num_iterations=15, clear_prev_frame=True):
    for _ in range(num_iterations):
        for frame in ascii_frames:
            print(frame)
            time.sleep(frame_pause)
            if clear_prev_frame:
                os.system('cls' if os.name == 'nt' else 'clear')

# Load GIF and process
intensity_multiplier = 4
im = Image.open("Hands.gif")
frames = extract_gif_frames(im, fillEmpty=True)
ascii_frames = convert_frames_to_ascii(frames)

# Start animation
animate_ascii(ascii_frames, num_iterations=200)
