# Gemini Image Generator

A robust Python library and command-line tool (CLI) to batch-generate images using the Google Gemini API.

This tool is designed for large-scale tasks, featuring resumable sessions via a manifest file, smart scanning for new files, and robust error handling.

## Features

- **Powerful CLI**: Generate images directly from your terminal.
- **Batch Processing**: Scan directories (including subdirectories) for thousands of media files and generate a cover for each.
- **Resumable & Robust**: Uses a `manifest.json` file to track the status of every task. If the process is interrupted, it can be resumed from where it left off, never re-processing completed work.
- **Smart Scanning**: Use `--force-scan` to intelligently discover new files without losing the status of existing ones.
- **Verification**: Use `--verify` to check for missing output images and automatically re-queue them for generation.
- **Flexible Configuration**: Control models, prompts, and output settings via `config.yml`.

## Installation

```bash
pip install gemini-image-generator
```

## Configuration

Before using the tool, you need to configure two files in your project directory:

**1. `.env` file (for your API Key):**
```
GOOGLE_API_KEY="YOUR_GOOGLE_AI_API_KEY_HERE"
```

**2. `config.yml` file (for prompts and settings):**
```yaml
model: "gemini-2.5-flash-image-preview"

output_settings:
  directory: "output_images"
  filename_template: "{timestamp}_{prompt_brief}.png"

prompt_templates:
  podcast_cover: "An abstract artwork for a podcast cover, inspired by the theme '{filename_stem}'. Primary visual elements: {keywords}. Style: minimalist, symbolic, impactful colors. NO text, NO letters, NO writing."
```

## Usage

### As a Command-Line Tool

The `gemini-image` command will be available after installation.

```bash
# Get help
gemini-image --help

# Generate a simple image from a prompt
gemini-image -p "A majestic lion in a futuristic city" -o "lion_v1.png"

# Use a prompt template from your config.yml
gemini-image -t "podcast_cover" -c "my_awesome_podcast.mp3"
```

### As a Library

You can also import `ImageGenerator` into your own Python scripts.

```python
from gemini_image_generator import ImageGenerator

try:
    generator = ImageGenerator(config_path='path/to/your/config.yml')

    # Simple text-to-image
    generator.generate(prompt="A beautiful watercolor painting of a robot cat.")

    # Using a template
    generator.generate_from_template(
        template_name='podcast_cover',
        context={'filename_stem': 'The History of Rome', 'keywords': 'rome, history, podcast'}
    )
except Exception as e:
    print(f"An error occurred: {e}")
```