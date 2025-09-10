from ray.serve import Application

from folder_classifier.app import FolderClassifierAPI
from folder_classifier.dto import AppConfig
from folder_classifier.util import get_openapi_key


def build_app(args: AppConfig) -> Application:
    assert args and args.model, "AppConfig model is required"
    assert args.model.app_name and args.model.deployment, "Model's app_name and deployment are required"

    if args.model.fallback and args.model.fallback.openai_base_url and args.model.fallback.model:
        if not args.model.fallback.openai_api_key:
            args.model.fallback.openai_api_key = get_openapi_key()

    app = FolderClassifierAPI.bind(args.model)
    return app
