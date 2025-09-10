import click
import os
import shlex
import traceback
import warnings
from transformers import logging
import importlib.resources
import yaml

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession 
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.document import Document

from GenIText.pipelines import End2EndCaptionPipeline
from GenIText.prompt_refiner import refiner
from GenIText.utils import *
from GenIText.config_editor import ConfigEditor
from GenIText.prompt_refiner.GA_utils import get_valid_image_files

warnings.filterwarnings("ignore")
logging.set_verbosity_error()

class CommandAuotSuggest(AutoSuggest):
    def __init__(self, commands):
        self.commands = commands
    
    def get_suggestion(self, buffer, document):
        text = document.text_before_cursor
        for cmd in self.commands:
            if cmd.startswith(text) and cmd != text:
                return Suggestion(cmd[len(text):])
        return None

class PathAndOptionsAutoSuggest(AutoSuggest):
    def __init__(self):
        self.dir = os.getcwd()
        self.dir_list = os.listdir(self.dir)
        self.options = {
            "/caption": ["--model", "--output", "-m", "-o"],
            "/refine": ["--model", "--pop", "--gen", "-m", "-p", "-g"],
        }
        
    def get_suggestion(self, command, buffer, document):
        text = document.text_before_cursor
        for file in self.dir_list:
            if file.startswith(text):
                return Suggestion(file[len(text):])
        
        if command in self.options:
            for option in self.options[command]:
                if option.startswith(text):
                    return Suggestion(option[len(text):])
        return None

class InterfaceAutoSuggest(AutoSuggest):
    def __init__(self, commands):
        self.command_suggestor = CommandAuotSuggest(commands)
        self.path_suggestor = PathAndOptionsAutoSuggest()
    
    def get_suggestion(self, buffer, document):
        tokens = document.text_before_cursor.split()
        
        if not tokens:
            return None
        
        if len(tokens) == 1:
            return self.command_suggestor.get_suggestion(buffer, document)
        else:
            last_token = tokens[-1]
            dummy_doc = Document(text=last_token, cursor_position=len(last_token))
            return self.path_suggestor.get_suggestion(tokens[0], buffer, dummy_doc)

def title_screen():
    os.system("clear" if os.name == "posix" else "cls")
    click.echo(click.style("\n ██████╗ ███████╗███╗   ██╗██╗████████╗███████╗██╗  ██╗████████╗", fg="red", bold=True))
    click.echo(click.style("██╔════╝ ██╔════╝████╗  ██║██║╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝", fg="red", bold=True))
    click.echo(click.style("██║  ███╗█████╗  ██╔██╗ ██║██║   ██║   █████╗   ╚███╔╝    ██║   ", fg="red", bold=True))
    click.echo(click.style("██║   ██║██╔══╝  ██║╚██╗██║██║   ██║   ██╔══╝   ██╔██╗    ██║   ", fg="red", bold=True))
    click.echo(click.style("╚██████╔╝███████╗██║ ╚████║██║   ██║   ███████╗██╔╝ ██╗   ██║   ", fg="red", bold=True))
    click.echo(click.style(" ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   ", fg="red", bold=True))

    click.echo(click.style("\n🎯 GENITEXT v0.4.1 - Advanced Image Captioning Framework", fg="green", bold=True))
    click.echo(click.style("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", fg="cyan"))

    click.echo(click.style("\n✨ FEATURES:", fg="yellow", bold=True))
    click.echo("  • Generate high-quality captions using LLaVA, ViT-GPT2, or BLIPv2")
    click.echo("  • Optimize prompts with genetic algorithms and LLM evaluation")
    click.echo("  • Support for multiple output formats (JSON, CSV, images+text)")
    click.echo("  • Interactive configuration editor for fine-tuning models")

    click.echo(click.style("\n🚀 QUICK START:", fg="yellow", bold=True))
    click.echo("  1. Generate captions:  /caption /path/to/images --model llava")
    click.echo("  2. Refine prompts:     /refine 'Describe this image' /path/to/images")
    click.echo("  3. View help:          /help")

    click.echo(click.style("\n💡 TIP:", fg="magenta", bold=True), nl=False)
    click.echo(" Use Tab for auto-completion and arrow keys for navigation")

    click.echo(click.style("\nType '/help' for detailed command reference or start captioning!", fg="blue"))

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx): 
    """GenIText: General Image-to-Text Automated package"""
    if ctx.invoked_subcommand is None: 
        start_interactive_shell()

def show_help():
    click.echo("\n" + "="*60)
    click.echo("                    GENITEXT HELP")
    click.echo("="*60)
    click.echo("\n📸 IMAGE CAPTIONING COMMANDS:")
    click.echo("  /caption <image_path> [--model MODEL] [--output PATH] [--format FORMAT]")
    click.echo("    Generate captions for images using specified model")
    click.echo("    • image_path: Single image file or directory of images")
    click.echo("    • --model: llava, vit_gpt2, or blipv2 (default: vit_gpt2)")
    click.echo("    • --output: Output directory (default: current directory)")
    click.echo("    • --format: json, jsonl, csv, or img&txt (default: json)")

    click.echo("\n🔬 PROMPT REFINEMENT COMMANDS:")
    click.echo("  /refine <prompt> <image_dir> [context] [--model MODEL] [--pop SIZE] [--gen COUNT]")
    click.echo("    Use genetic algorithms to optimize prompts for better captions")
    click.echo("    • prompt: Initial prompt to refine")
    click.echo("    • image_dir: Directory with images for evaluation")
    click.echo("    • context: Optional context for refinement")
    click.echo("    • --pop: Population size (3-20, default: 5)")
    click.echo("    • --gen: Number of generations (1-20, default: 5)")

    click.echo("\n⚙️  CONFIGURATION & MANAGEMENT:")
    click.echo("  /models - Show all available captioning models")
    click.echo("  /config <model_name> - Edit model configuration interactively")
    click.echo("  /delete <model_name> - Remove model from cache")

    click.echo("\n📁 UTILITY COMMANDS:")
    click.echo("  /ls - List files in current directory")
    click.echo("  /clear - Clear the terminal screen")
    click.echo("  /help - Show this help menu")
    click.echo("  /exit - Exit GenIText")

    click.echo("\n" + "💡 TIPS:")
    click.echo("  • Use Tab for auto-completion of commands and paths")
    click.echo("  • Supported image formats: PNG, JPG, JPEG")
    click.echo("  • For best results, use 5-20 images for prompt refinement")
    click.echo("  • Ollama must be running for prompt refinement features")
    click.echo("="*60)

@cli.command()
def models():
    """
    Show available models for captioning.
    """
    models = End2EndCaptionPipeline.models
    click.echo("Available models:")
    for model in models:
        click.echo(f"- {model}")
        
@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--model", "-m", default="vit_gpt2", type=click.Choice(list(End2EndCaptionPipeline.models.keys())), help="Model name to use for captioning.")
@click.option("--output", "-o", default=None, help="Output directory.")
@click.option("--format", "-f", default="json", type=click.Choice(['json', 'jsonl', 'csv', 'img&txt'], case_sensitive=False), help="Output format (json/jsonl/csv/img&txt).")
@click.option("--keyword", "-k", is_flag=True, help="Embed metadata in the image files.")
def caption(image_path: str, model: str, output: str, format: str, keyword: bool):
    """
    Generate captions for a list of images.

    IMAGE_PATH can be either a single image file or a directory containing images.
    Supported image formats: PNG, JPG, JPEG.
    """
    # Validate input path
    if not os.path.exists(image_path):
        raise click.BadParameter(f"Path '{image_path}' does not exist.")

    if os.path.isfile(image_path):
        # Validate file extension for single file
        valid_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
        if not any(image_path.lower().endswith(ext) for ext in valid_extensions):
            raise click.BadParameter(f"File '{image_path}' is not a supported image format. Supported: {', '.join(valid_extensions)}")
        image_paths = [image_path]
    elif os.path.isdir(image_path):
        # Get all image files from directory
        image_paths = []
        valid_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
        for file in os.listdir(image_path):
            file_path = os.path.join(image_path, file)
            if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in valid_extensions):
                image_paths.append(file_path)

        if not image_paths:
            raise click.BadParameter(f"No valid image files found in directory '{image_path}'. Supported formats: {', '.join(valid_extensions)}")
    else:
        raise click.BadParameter(f"Path '{image_path}' is neither a file nor a directory.")

    # Validate output directory if specified
    if output is not None:
        if os.path.exists(output) and not os.path.isdir(output):
            raise click.BadParameter(f"Output path '{output}' exists but is not a directory.")
        # Don't create directory here - let the pipeline handle it
    
    click.echo(f"[INFO] Generating captions for {len(image_paths)} images using {model} model")
    pipeline = End2EndCaptionPipeline(model=model, config=None)
    
    captions = pipeline.generate_captions(image_paths)
    
    if output is not None:
        os.makedirs(output, exist_ok=True)
        
        if format == "json":
            save_caption_as_json(captions, output)
        elif format == "jsonl":
            save_caption_as_jsonl(captions, output)
        elif format == "csv":
            save_caption_as_csv(captions, output)
        elif format == "img&txt":
            save_images_and_txt(captions, output)
        else: 
            raise ValueError(f"[ERROR] Invalid format: {format}")
    
    if keyword:
        for img, cap in tqdm(zip(image_paths, captions), desc="Embedding metadata"):
            embed_metadata(img, None, cap)
    else: 
        for img, cap in tqdm(zip(image_paths, captions), desc="Embedding metadata"):
            embed_metadata(img, cap, None)
    click.echo("[INFO] Metadata embedded in image files")
    
    click.echo(f"[INFO] Captions saved to {output}")
    
@cli.command()
@click.argument("model", default="llava", type=click.Choice(list(End2EndCaptionPipeline.models.keys())))
def delete(model: str):
    """
    Delete a model.
    """
    with importlib.resources.path('GenIText.configs', f'{model}_config.yaml') as path:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
            model_url = config["model"]["model_id"]
            if(remove_model_cache(model_url)): 
                click.echo(f"[INFO] Model {model} deleted.")
            else:
                click.echo(f"[ERROR] Model {model} not found.")
                
@cli.command() 
@click.argument("model", default="llava", type=click.Choice(list(End2EndCaptionPipeline.models.keys())))         
def config(model: str):
    """
    Modify configs
    """
    with importlib.resources.path('GenIText.configs', f'{model}_config.yaml') as path:
        editor = ConfigEditor(config=path, model=model)
        editor.run()

@cli.command()
@click.argument("prompt")
@click.argument("image_dir", type=click.Path(exists=True))
@click.argument("context", default=None)
@click.option("--model", "-m", default="llava", type=click.Choice(list(End2EndCaptionPipeline.models.keys())), help="Model to use for refinement.")
@click.option("--pop", "-p", default=5, help="Population size for refinement.")
@click.option("--gen", "-g", default=5, help="Number of generations for refinement.")
def refine(prompt: str, image_dir: str, context: str, model: str = "llava", pop: int = 5, gen: int = 5):
    """
    Refine a prompt to generate better captions using genetic algorithm optimization.

    This command uses evolutionary algorithms to improve prompt quality for image captioning.
    It requires Ollama to be installed and running for LLM-based evaluation.

    PROMPT: The initial prompt to refine
    IMAGE_DIR: Path to directory containing images or single image file
    CONTEXT: Optional additional context for refinement (can be None)

    Examples:
        genitext /refine "Describe this image" /path/to/images "photorealistic style"
        genitext /refine "A beautiful scene" /path/to/single/image.jpg
    """
    # Validate prompt
    if not prompt or not prompt.strip():
        raise click.BadParameter("Prompt cannot be empty.")

    if len(prompt.strip()) < 5:
        raise click.BadParameter("Prompt must be at least 5 characters long.")

    # Validate population and generation parameters
    if pop < 3:
        raise click.BadParameter("Population size must be at least 3.")
    if pop > 20:
        raise click.BadParameter("Population size cannot exceed 20.")

    if gen < 1:
        raise click.BadParameter("Number of generations must be at least 1.")
    if gen > 20:
        raise click.BadParameter("Number of generations cannot exceed 20.")

    click.echo(f"[INFO] Starting refine with image_dir: {image_dir}")

    # Validate and collect image paths
    if os.path.isfile(image_dir):
        # Validate file extension for single file
        valid_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
        if not any(image_dir.lower().endswith(ext) for ext in valid_extensions):
            raise click.BadParameter(f"File '{image_dir}' is not a supported image format. Supported: {', '.join(valid_extensions)}")
        image_paths = [image_dir]
        click.echo(f"[INFO] Single file mode: {image_paths}")
    elif os.path.isdir(image_dir):
        image_paths = get_valid_image_files(image_dir)
        if not image_paths:
            valid_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
            raise click.BadParameter(f"No valid image files found in directory '{image_dir}'. Supported formats: {', '.join(valid_extensions)}")
        click.echo(f"[INFO] Directory mode: Found {len(image_paths)} files")
    else:
        raise click.BadParameter(f"Path '{image_dir}' is neither a valid file nor directory.")
    
    click.echo(f"[INFO] Refining prompt for {len(image_paths)} images using {model} model")
    for i, path in enumerate(image_paths):
        if path is None:
            click.echo(f"[WARNING] Path {i} is None!")
        elif not os.path.exists(path):
            click.echo(f"[WARNING] Path {i} does not exist: {path}")
        

    click.echo(f"[INFO] Model: {model}, Population: {pop}, Generations: {gen}")
    
    refined_prompt = refiner(
        prompt=prompt, 
        image_dir=image_paths, 
        population_size=pop, 
        generations=gen, 
        config=None,
        model_id=model, 
        context=context
    )
    
    optimal_prompt = refined_prompt["population"][0]
    
    click.echo(f"[INFO] Initial prompt: \n{prompt}")
    click.echo(f"[INFO] Refined prompt: \n{optimal_prompt}")

def start_interactive_shell(): 
    os.system('clear' if os.name == 'posix' else 'cls')
    title_screen()
    
    bindings = KeyBindings()
    @bindings.add("tab")
    def accept_auto_suggestion(event):
        """
        When Tab is pressed, check if there's an auto-suggestion available.
        If yes, insert the suggestion text into the buffer.
        Otherwise, you can trigger the default completion behavior.
        """
        buff = event.current_buffer
        if buff.suggestion:
            buff.insert_text(buff.suggestion.text)
        else:
            event.app.current_buffer.start_completion(select_first=False)
    
    command_map = {
        '/caption': caption,
        '/refine': refine,
        '/models': models,
        '/help': show_help,
        '/delete': delete,
        '/config': config,
        '/ls': None,
        '/clear': None,
        '/exit': None
    }
    
    session = PromptSession(auto_suggest=InterfaceAutoSuggest(list(command_map.keys())),key_bindings=bindings)
    while True: 
        try: 
            command = session.prompt(f"\n~/GenIText> ")
            
            if command == "/help": 
                show_help()
            elif command == "/exit": 
                click.echo(click.style("\n[INFO] Exiting GenIText", fg="red"))
                break
            elif command == "/clear":
                os.system('clear' if os.name == 'posix' else 'cls')
                title_screen()
                
            elif command == "/ls":
                current_dir = os.getcwd()
                click.echo(f"Current directory: {current_dir}")
                for file in os.listdir(current_dir):
                    click.echo(f"- {file}")
            elif command.startswith(tuple(command_map.keys())):
                parts = shlex.split(command)
                cmd = command_map.get(parts[0])
                
                if cmd is None: 
                    click.echo(click.style("[ERROR] Invalid command. Type '/help' to see the available commands.", fg="red"))
                else:
                    args = parts[1:]
                    try:
                        cmd.main(args=args, standalone_mode=False)
                    except click.BadParameter as e:
                        click.echo(click.style(f"❌ Parameter Error: {e}", fg="red"))
                        click.echo(click.style("💡 Tip: Check your command syntax with '/help'", fg="yellow"))
                    except click.ClickException as e:
                        click.echo(click.style(f"❌ Command Error: {e}", fg="red"))
                    except FileNotFoundError as e:
                        click.echo(click.style(f"❌ File Error: {e}", fg="red"))
                        click.echo(click.style("💡 Tip: Verify the file/directory path exists", fg="yellow"))
                    except Exception as e:
                        click.echo(click.style(f"❌ Unexpected Error: {e}", fg="red"))
                        click.echo(click.style("💡 Tip: Try running with different parameters", fg="yellow"))
            else:
                click.echo(click.style("❌ Unknown command. Available commands:", fg="red"))
                click.echo(click.style("   /caption, /refine, /models, /config, /delete, /help, /exit", fg="cyan"))
                click.echo(click.style("💡 Tip: Type '/help' for detailed command reference", fg="yellow"))
        except KeyboardInterrupt:
            click.echo(click.style("\n👋 Goodbye! Thanks for using GenIText!", fg="green"))
            break
    
if __name__ == "__main__":
    cli()