from PIL import Image, ImageDraw, ImageFont
import requests

def generate_report(weekly_data, daily_data):
    """
    Generates a multi-line report string, combining weekly_data and daily_data.
    """
    report = f"""
=== Weekly Overview ===
SPY Trend: {weekly_data.get('trend', 'N/A')}
RSI: {weekly_data.get('rsi', 'N/A')} ({weekly_data.get('rsi_comment', 'N/A')})
Key Levels: Support at {weekly_data.get('support', 'N/A')}, Resistance at {weekly_data.get('resistance', 'N/A')}

=== Daily Overview ===
SPY Momentum: {daily_data.get('momentum', 'N/A')}
RSI: {daily_data.get('rsi', 'N/A')} ({daily_data.get('rsi_comment', 'N/A')})
Volatility: ATR={daily_data.get('atr', 'N/A')}
Trade Setup: {daily_data.get('trade_setup', 'N/A')}
"""
    return report.strip()

def create_report_image(report_text, output_file="report.png", color_coding=None):
    """
    Creates an image of the report text and saves it to a file with optional color coding.
    
    :param report_text: The report text to be displayed on the image.
    :param output_file: The file path to save the image.
    :param color_coding: A dictionary of keywords mapped to colors for text styling.
    """
    # Font settings (ensure you have a valid .ttf font on your system)
    font_path = "arial.ttf"  # Replace with a valid path to a font file
    font = ImageFont.truetype(font_path, 20)
    header_font = ImageFont.truetype(font_path, 24)
    padding = 20
    image_width = 800
    max_line_length = 70

    # Wrap text and split into lines
    lines = []
    for paragraph in report_text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= max_line_length:
                line += word + " "
            else:
                lines.append(line.strip())
                line = word + " "
        if line:
            lines.append(line.strip())

    # Calculate image height
    image_height = padding * 2 + len(lines) * 30

    # Create image
    img = Image.new("RGB", (image_width, image_height), color="white")
    draw = ImageDraw.Draw(img)

    # Draw text with color coding
    y = padding
    for line in lines:
        line_color = "black"  # Default text color
        if color_coding:
            for keyword, color in color_coding.items():
                if keyword.lower() in line.lower():
                    line_color = color
                    break

        # Use bold font for headers
        if "===" in line:
            draw.text((padding, y), line, fill="blue", font=header_font)
        else:
            draw.text((padding, y), line, fill=line_color, font=font)
        y += 30

    # Save image
    img.save(output_file)
    print(f"Report image saved to {output_file}")

def post_image_to_discord(image_path, webhook_url):
    """
    Posts the report image to Discord.
    """
    with open(image_path, "rb") as image_file:
        payload = {"content": "Here is your trading report with support and resistance levels!"}
        files = {"file": image_file}
        response = requests.post(webhook_url, data=payload, files=files)
        if response.status_code in [200, 204]:
            print("Image successfully posted to Discord!")
        else:
            print(f"Failed to post to Discord. Status Code: {response.status_code}")
