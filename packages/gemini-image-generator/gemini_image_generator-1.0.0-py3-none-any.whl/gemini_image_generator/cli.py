import argparse
import os
import sys
from .generator import ImageGenerator

def main():
    parser = argparse.ArgumentParser(
        description="Generate images with the Gemini API via the command line.",
        # This makes the help message look a bit cleaner
        formatter_class=argparse.RawTextHelpFormatter 
    )
    
    # --- We can group arguments for better help output ---
    required_group = parser.add_argument_group('Primary Actions (choose one)')
    required_group.add_argument("-p", "--prompt", type=str, help="The text prompt for image generation.")
    required_group.add_argument("-t", "--template", type=str, help="Name of the prompt template to use from config.yml.")

    template_group = parser.add_argument_group('Template Options')
    template_group.add_argument("-c", "--context", type=str, help="Filename or topic to use as context for the template (e.g., 'history_of_rome.mp3').\nRequired if --template is used.")

    optional_group = parser.add_argument_group('Optional Modifiers')
    optional_group.add_argument("-i", "--input-images", nargs='+', help="One or more paths to input images for editing.")
    optional_group.add_argument("-o", "--output-filename", type=str, help="Specify a custom output filename.")

    args = parser.parse_args()

    # --- THIS IS THE FIX ---
    # If no primary action is specified, print a helpful message and the main help text, then exit.
    if not args.prompt and not args.template:
        print("Error: No action requested. You must specify either --prompt or --template.")
        print("--------------------")
        parser.print_help()
        sys.exit(1) # Exit with an error code

    # Also, ensure context is provided when a template is used
    if args.template and not args.context:
        print("Error: --context is required when using the --template argument.")
        sys.exit(1)
    # --- END OF FIX ---

    try:
        generator = ImageGenerator()
        
        if args.template:
            # For podcast_cover, we extract the filename without extension
            filename_stem = os.path.splitext(os.path.basename(args.context))[0].replace('_', ' ')
            context_dict = {'filename_stem': filename_stem, 'topic': args.context}
            generator.generate_from_template(
                template_name=args.template,
                context=context_dict,
                input_images=args.input_images,
                output_filename=args.output_filename
            )
        else: # This block now only runs if a prompt was given
            generator.generate(
                prompt=args.prompt,
                input_images=args.input_images,
                output_filename=args.output_filename
            )

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()