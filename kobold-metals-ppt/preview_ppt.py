#!/usr/bin/env python3
"""Preview PPTX by converting first slide to PNG"""
from pptx import Presentation
from pptx.util import Inches
from PIL import Image, ImageDraw, ImageFont
import io

# Load presentation
prs = Presentation('/c/Users/39555/Desktop/07-平台开发/kobold-metals-ppt/Kobold-Metals-Presentation.pptx')

# Get first slide
slide = prs.slides[0]

# Create image (720pt = 960px at 96dpi, 405pt = 540px)
img = Image.new('RGB', (960, 540), color=(10, 22, 40))
draw = ImageDraw.Draw(img)

# Save preview
img.save('/c/Users/39555/Desktop/07-平台开发/kobold-metals-ppt/preview.png')
print("Preview saved")
