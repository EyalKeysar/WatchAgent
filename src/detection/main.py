import nudenet
from PIL import Image, ImageDraw, ImageFont
import tempfile

# Load the model
nude_detector = nudenet.NudeDetector()

# Load the image
image_path = 'image.jpg'
image = Image.open(image_path)

# Save the image to a temporary file
temp_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
image.save(temp_image.name)

# Perform nudity detection
results = nude_detector.detect(temp_image.name)

# Close the temporary file
temp_image.close()

# Draw bounding boxes and labels on the image
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("arial.ttf", 20)

for result in results:
    x0, y0, width, height = result['box']
    x1 = x0 + width
    y1 = y0 + height
    box = (x0, y0, x1, y1)
    draw.rectangle(box, outline='red', width=3)
    
    label = result['class'].replace('_', ' ').title()
    score = result['score']
    text = f"{label} ({score:.2f})"
    draw.text((x0, y0), text, fill='red', font=font)

# Save the output image
output_image_path = 'output.jpg'
image.save(output_image_path)

# Check the results
print("Output image saved as:", output_image_path)
