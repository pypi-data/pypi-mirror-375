import os
from tqdm import tqdm
from typing import Dict, List, Union
from random import sample
import requests
import zipfile
from PIL import Image
import json
import shutil
import subprocess

def download_dataset(url: str = None, path: str = "dataset/"):
    """
    Download dataset from a URL and extract it to the specified path.
    """
    if url is None:
        url = "https://www.kaggle.com/api/v1/datasets/download/hadiepratamatulili/anime-vs-cartoon-vs-human"

    # Validate path
    if not path or not path.strip():
        raise ValueError("Path cannot be empty.")

    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        raise ValueError(f"Invalid URL format: {url}")

    os.makedirs(path, exist_ok=True)
    download_path = os.path.join(path, "anime-vs-cartoon-vs-human.zip")

    if not os.path.exists(download_path):
        if os.path.exists(os.path.join(path, "Data")) and len(os.listdir(os.path.join(path, "Data", "anime"))) > 0 and len(os.listdir(os.path.join(path, "Data", "human"))) > 0 and len(os.listdir(os.path.join(path, "Data", "cartoon"))) > 0:
            print(f"[INFO] {os.path.join(path, 'Data')} already exists")
            return os.path.join(path, "Data/")

        response = requests.get(url, stream=True)
        
        if response.status_code == 200:
            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024

            with open(download_path, "wb") as f, tqdm(
                desc="Downloading Dataset from kaggle URL",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(block_size):
                    f.write(chunk)
                    bar.update(len(chunk))

            print(f"[INFO] Successfully downloaded to {download_path}")
        else:
            print(f"Download failed with status code: {response.status_code}")
    else: 
        print(f"[INFO] {download_path} already exists")
        
    print("[INFO] Extracting files...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref, tqdm(
        desc="Extracting files",
        total=len(zip_ref.namelist()),
        unit="files",
    ) as bar:
        for file in zip_ref.namelist():
            zip_ref.extract(file, path)
            bar.update(1)
        print(f"[INFO] Extracted all files to {path}")
    
    os.remove(download_path)
    return os.path.join(path, "Data/")

def cut_data(dataset_path: str, sample_threshold: int):
    """
    Reduce the dataset to a specified number of samples by randomly removing excess files.

    Args:
        dataset_path (str): Path to the dataset directory containing image files.
        sample_threshold (int): Maximum number of samples to keep in the dataset.

    Note:
        This function randomly selects files to remove if the current dataset
        size exceeds the threshold. The selection is not reproducible across runs.
    """
    # Validate inputs
    if not os.path.exists(dataset_path):
        raise ValueError(f"Dataset path '{dataset_path}' does not exist.")

    if not os.path.isdir(dataset_path):
        raise ValueError(f"Path '{dataset_path}' is not a directory.")

    if sample_threshold <= 0:
        raise ValueError("Sample threshold must be greater than 0.")

    files = os.listdir(dataset_path)
    if len(files) > sample_threshold:
        files = os.listdir(dataset_path)
        for file in sample(files, len(files) - sample_threshold):
            os.remove(os.path.join(dataset_path, file))
        print(f"[INFO] Removed {len(files) - sample_threshold} files")

def prepare_data(sample_threshold: int = 100, target_dir: str = "dataset/"):
    """
    Prepare the test dataset for training.
    
    Args:
        sample_threshold (int): Number of samples to keep.
        target_dir (str): Path to save the dataset.
        
    Returns:
        Tuple[List[str], List[str], List[str]]: List of anime, cartoon, and human images.
    """

    data_path = download_dataset(path=target_dir)
    print(f"[INFO] Data downloaded to {data_path}")
    
    anime_path = os.path.join(data_path, "anime")
    cartoon_path = os.path.join(data_path, "cartoon")
    human_path = os.path.join(data_path, "human")
    
    cut_data(anime_path, sample_threshold)
    cut_data(cartoon_path, sample_threshold)
    cut_data(human_path, sample_threshold)
    
    return {"anime": anime_path, "cartoon": cartoon_path, "human": human_path}
            
def save_images_and_txt(captions: List[Dict[str, str]], output_path: str = "output/samples/"):
    """
    Save a list of images and their captions to a directory structure.

    Creates separate directories for images and captions, then saves each image
    as a PNG file and its corresponding caption as a text file.

    Args:
        captions (List[Dict[str, str]]): List of dictionaries containing 'image' paths
            and 'caption' text pairs.
        output_path (str): Base directory path to save the images and captions.
            Defaults to "output/samples/".

    Raises:
        OSError: If there are issues creating directories or writing files.
        IOError: If there are issues reading the source images.
    """
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(os.path.join(output_path, "captions"), exist_ok=True)
    os.makedirs(os.path.join(output_path, "images"), exist_ok=True)
    
    caption_ls = [] 
    image_ls = []
    for i, pair in enumerate(captions):
        caption_ls.append((os.path.join(output_path, "captions", f"caption_{i}.txt"), pair["caption"]))
        
        with Image.open(pair["image"]) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            image_ls.append((os.path.join(output_path, "images", f"image_{i}.png"), img.copy()))
    
    for path, caption in tqdm(caption_ls, total=len(caption_ls), desc=f"Saving captions to {output_path}"):
        with open(path, 'w') as f:
            f.write(caption)
        
    print("[INFO] Finished saving images")
    
def save_caption_as_csv(captions: List[Dict[str, str]], output_path: str = "output"):
    """
    Save a list of dictionaries to a csv file.
    
    Args:
        captions (List[Dict[str, str]]): List of dictionaries to save.
        output_path (str): Path to save the csv file.
    """
    os.makedirs(output_path, exist_ok=True)
    file_name = os.path.join(output_path, "captions.csv")
    
    with open(file_name, 'w') as f: 
        f.write(','.join(captions[0].keys()) + '\n')
        f.write('\n')
        for row in captions: 
            f.write(','.join(str(x) for x in row.values()) + '\n')
            
def save_caption_as_json(captions: List[Dict[str, str]], output_path: str = "output"):
    """
    Save a list of dictionaries to a json file.
    
    Args:
        captions (List[Dict[str, str]]): List of dictionaries to save.
        output_path (str): Path to save the json file.
    """
    os.makedirs(output_path, exist_ok=True)
    file_name = os.path.join(output_path, "captions.json")
    
    with open(file_name, 'w') as f: 
        for row in captions: 
            f.write(json.dumps(row) + '\n')
        
def save_caption_as_jsonl(captions: List[Dict[str, str]], output_path: str = "output"):
    """
    Save a list of dictionaries to a jsonl file.
    
    Args:
        captions (List[Dict[str, str]]): List of dictionaries to save.
        output_path (str): Path to save the jsonl file.
    """
    os.makedirs(output_path, exist_ok=True)
    file_name = os.path.join(output_path, "captions.jsonl")
    
    with open(file_name, 'w') as f: 
        for row in captions: 
            f.write(json.dumps(row) + '\n')
            
def check_model_exists(model_url: str) -> str:
    """
    Check if a HuggingFace model exists in the local cache.

    Args:
        model_url (str): HuggingFace model URL in format "organization/model-name".

    Returns:
        str: Path to the model cache directory if it exists, regardless of whether
        the model is actually cached there.

    Note:
        This function only checks for the existence of the cache directory path,
        not whether the model files are actually present.
    """
    parsed_url = model_url.split("/")
    path = os.path.join(os.path.expanduser("~/.cache/huggingface/hub"), "models--" + parsed_url[0] + "--" + parsed_url[1])
    return path

def remove_model_cache(model_url: str) -> bool:
    """
    Remove a HuggingFace model's cache directory from the local filesystem.

    Args:
        model_url (str): HuggingFace model URL in format "organization/model-name".

    Returns:
        bool: True if the cache was successfully removed, False if the cache
        directory didn't exist.

    Raises:
        OSError: If there are permission issues or other filesystem errors
        when attempting to remove the cache directory.
    """
    path = check_model_exists(model_url)
    if os.path.exists(path):
        shutil.rmtree(path)
        return True
    else:
        return False
    
def embed_metadata(image_path: str, caption: str = None, keywords: Union[List[str], str] = None):
    """
    Embed metadata (caption and keywords) into an image file using EXIF tags.

    Args:
        image_path (str): Path to the image file to modify.
        caption (str, optional): Caption text to embed in the image metadata.
        keywords (Union[List[str], str], optional): Keywords to embed. Can be a single
            string or list of strings.

    Note:
        This function requires the 'exiftool' command-line utility to be installed
        on the system. It modifies the original image file in-place.

    Raises:
        subprocess.CalledProcessError: If exiftool fails to execute or returns an error.
        FileNotFoundError: If the specified image file doesn't exist.
    """
    if(caption == None):
        caption = ""
        
    cmd = ["exiftool", "-overwrite_original"]
    
    if caption != None:
        cmd.append(f"-IPTC:Caption-Abstract={caption}")
        
    if keywords != None:
        if isinstance(keywords, str):
            keywords = keywords.split(",")
        for keyword in keywords:
            cmd.append(f"-IPTC:Keywords={keyword}")
    
    cmd.append(image_path)
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 