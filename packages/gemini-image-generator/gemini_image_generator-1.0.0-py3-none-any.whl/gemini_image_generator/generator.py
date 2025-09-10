import os
import yaml
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from google import genai
from datetime import datetime

class ImageGenerator:
    def __init__(self, config_path: str = 'config.yml'):
        load_dotenv(override=True)
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found.")
        
        self.client = genai.Client()

        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")

        self.model_name = self.config.get('model')
        if not self.model_name:
            raise ValueError("Model name not found in config.yml.")

    def _get_output_path(self, prompt: str, filename: str = None) -> str:
        settings = self.config.get('output_settings', {})
        directory = settings.get('directory', 'output_images')
        os.makedirs(directory, exist_ok=True)

        if filename:
            return os.path.join(directory, filename)
        else:
            template = settings.get('filename_template', '{timestamp}.png')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            prompt_brief = '_'.join(prompt.split()[:5]).lower().replace('"', '')
            dynamic_filename = template.format(timestamp=timestamp, prompt_brief=prompt_brief)
            return os.path.join(directory, dynamic_filename)

    def generate_from_template(self, template_name: str, context: dict, **kwargs):
        templates = self.config.get('prompt_templates', {})
        template_str = templates.get(template_name)
        if not template_str:
            raise ValueError(f"Prompt template '{template_name}' not found in config.yml.")
        
        prompt = template_str.format(**context)
        print(f"--- Generated prompt from template '{template_name}' ---")
        # Ensure the return from generate() is passed up correctly
        return self.generate(prompt=prompt, **kwargs)

    def generate(self, prompt: str = None, input_images: list = None, output_filename: str = None):
        prompt_to_use = prompt or self.config.get('default_prompt')
        if not prompt_to_use:
            raise ValueError("No prompt provided and no default_prompt found.")

        images_to_use = input_images if input_images is not None else self.config.get('default_input_images', [])
        print(f"\nModel: '{self.model_name}'\nPrompt: '{prompt_to_use}'")
        
        contents = [prompt_to_use]
        if images_to_use:
            print(f"Input images: {images_to_use}")
            for image_path in images_to_use:
                try:
                    contents.append(Image.open(image_path))
                except FileNotFoundError:
                    print(f"Warning: Skipping missing image '{image_path}'")
        
        response = self.client.models.generate_content(model=self.model_name, contents=contents)
        output_path = self._get_output_path(prompt_to_use, output_filename)
        
        generated_image = None
        response_text = None
        
        # --- 核心修改：移除 break，完整遍历 ---
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                try:
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(output_path)
                    print(f"Image successfully saved to '{output_path}'")
                    generated_image = image # 保存图片对象
                except Exception as e:
                    print(f"Error saving image: {e}")
            elif part.text:
                response_text = part.text # 保存文本

        if response_text:
            if generated_image:
                print(f"API returned an image AND accompanying text: {response_text[:100]}...")
            else:
                print(f"API returned text instead of an image: {response_text[:100]}...")
        
        return generated_image, response_text