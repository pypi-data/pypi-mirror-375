import os
from pathlib import PurePosixPath
from typing import List, Union

from folder_classifier.dto import Folder, File
import boto3


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gemini-2.0-flash")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openaiproxy.dev.cortoaws.com/v1")

PARAM_STORE_OPENAI_API_KEY = os.getenv("PARAM_STORE_OPENAI_API_KEY", "/AiService/OpenAiSettings/ApiKey")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME", "us-west-2")


def get_openapi_key() -> str:
    boto_session = boto3.Session(region_name=AWS_REGION_NAME)
    ssm_client = boto_session.client("ssm")
    response = ssm_client.get_parameter(Name=PARAM_STORE_OPENAI_API_KEY, WithDecryption=True)
    return response["Parameter"]["Value"]


def build_folder(paths: List[str]) -> Folder:
    """
    Create a Folder tree from a list of file paths.
    Assumptions:
    - The file paths are delimited by "/"
    - There are no '.' and '..' entries in the paths
    - The paths are case-insensitive (Windows paths) -> 'ABC' and 'abc' resolve to the same item
    """
    if not paths:
        raise ValueError("No paths provided")

    # Build a LOWER-CASED directory-prefix set so folder/file disambiguation is case-insensitive.
    prefix_set_lower = set()
    for p in paths:
        parts = p.split('/')
        for i in range(1, len(parts)):
            prefix_set_lower.add('/'.join(parts[:i]).lower())

    # Sort by depth so parents are created before children
    sorted_paths = sorted(paths, key=lambda x: x.count('/'))

    # Create the root folder (preserve first-seen casing)
    root_name = sorted_paths[0].split('/')[0]
    root = Folder(name=root_name, type="root_folder", items=[])

    # Build the tree
    for p in sorted_paths:
        parts = p.split('/')
        current = root

        for idx, part in enumerate(parts[1:], start=1):
            part_lower = part.lower()
            full_path_lower = '/'.join(parts[:idx + 1]).lower()
            is_last = idx == len(parts) - 1

            # Case-insensitive lookup of existing child
            existing = next((item for item in current.items if item.name.lower() == part_lower), None)
            if existing:
                if isinstance(existing, Folder):
                    current = existing
                continue

            # Determine type for new item
            if is_last and full_path_lower not in prefix_set_lower:
                if part.strip() in (".", ".."):
                    # These won't appear in the paths, ignore if they do.
                    continue
                has_ext = bool(PurePosixPath(part).suffix)
                is_dotfile = part.startswith('.') and len(part) > 1
                is_file = has_ext or is_dotfile
                new_item = File(name=part, type="file") if is_file else Folder(name=part, type="sub_folder", items=[])
            else:
                new_item = Folder(name=part, type="sub_folder", items=[])

            current.items.append(new_item)
            if isinstance(new_item, Folder):
                current = new_item

    return root


def render_tree(folder: Folder) -> str:
    """
    Render Folder tree using ASCII tree characters (├──, └──, │).
    """
    lines: List[str] = []

    def recurse(node: Union[Folder, File], prefix: str, is_last: bool):
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{node.name}")
        if isinstance(node, Folder):
            child_prefix = prefix + ("    " if is_last else "│   ")
            for idx, child in enumerate(node.items):
                recurse(child, child_prefix, idx == len(node.items) - 1)

    # root
    lines.append(folder.name)
    for idx, child in enumerate(folder.items):
        recurse(child, "", idx == len(folder.items) - 1)

    return "\n".join(lines)
