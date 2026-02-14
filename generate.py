import argparse
import base64
import sys
import time
from pathlib import Path

import pyvips
import replicate
from colorama import Fore, Style, init
from dotenv import load_dotenv
from tqdm import tqdm

# Initialize colorama for cross-platform colored output
init()

load_dotenv()


def process_existing_image(filename):
    print(f"{Fore.BLUE}📂 Processing existing image: {filename}{Style.RESET_ALL}")

    try:
        with open(filename, "rb") as file:
            image_data = file.read()
    except FileNotFoundError:
        print(f"{Fore.RED}❌ Error: File {filename} not found{Style.RESET_ALL}")
        sys.exit(1)

    return image_data


def generate_new_image(prompt):
    print(f"\n{Fore.YELLOW}🔄 Generating image...{Style.RESET_ALL}")

    input = {
        "prompt": prompt,
        "prompt_upsampling": False,
    }

    output = replicate.run("black-forest-labs/flux-1.1-pro", input=input)
    print(f"\n{Fore.GREEN}✨ Image generated successfully!{Style.RESET_ALL}")

    return output.read()


def main():
    parser = argparse.ArgumentParser(description="Generate or process images with Flux")
    parser.add_argument(
        "--previous", help="Use an existing image file instead of generating new one"
    )
    args = parser.parse_args()

    if args.previous:
        image_data = process_existing_image(args.previous)
    else:
        print(f"{Fore.CYAN}🎨 Flux Image Generator{Style.RESET_ALL}")
        prompt = input(f"{Fore.GREEN}Enter your prompt:{Style.RESET_ALL} ")
        image_data = generate_new_image(prompt)

    Path("generations").mkdir(exist_ok=True)
    timestamp = int(time.time())

    print(f"{Fore.BLUE}💾 Saving files...{Style.RESET_ALL}")

    # Only save to generations if we're generating a new image
    if not args.previous:
        with open(f"generations/{timestamp}.jpg", "wb") as file:
            file.write(image_data)
        print(f"  ├─ Saved JPG to: generations/{timestamp}.jpg")

    # Convert to base64
    img_str = base64.b64encode(image_data).decode("utf-8")

    with open("template.svg", "r") as f:
        svg = f.read()

    svg = svg.replace("__BASE64JPG__", img_str)

    Path("icons").mkdir(exist_ok=True)

    # Save svg
    with open(f"icons/{timestamp}.svg", "w") as f:
        f.write(svg)
    print(f"  ├─ Saved SVG to: icons/{timestamp}.svg")

    # Convert SVG to JPG using pyvips
    image = pyvips.Image.new_from_buffer(svg.encode(), "")
    image.write_to_file(f"icons/{timestamp}.png")
    print(f"  └─ Saved PNG to: icons/{timestamp}.png")

    print(f"\n{Fore.GREEN}✅ All done! Your images are ready.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
