import logging

from fastapi import FastAPI
from ray import serve

from folder_classifier.classifier import FolderClassifier
from folder_classifier.dto import ModelConfig, FolderClassificationRequest, FolderClassificationResponse

web_api = FastAPI(title=f"Folder Classifier API")

@serve.deployment
@serve.ingress(web_api)
class FolderClassifierAPI:
    def __init__(self, model_config: ModelConfig):
        assert model_config, "model_config is required"
        assert model_config.app_name and model_config.deployment, "Invalid ModelConfig values"
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.classifier = FolderClassifier(app_name=model_config.app_name, deployment=model_config.deployment, model=model_config.model,
                                           fallback_config = model_config.fallback)
        self.logger.info(f"Successfully initialized Folder Classifier API using config: {model_config}")

    @web_api.post("/predict")
    async def predict(self, request: FolderClassificationRequest) -> FolderClassificationResponse:
        self.logger.info(f"Received new request")
        category, reasoning = await self.classifier.predict(request)
        self.logger.info(f"Request with items: {request.items} classified as '{category}' with reasoning: '{reasoning}'")
        return FolderClassificationResponse(category=category, reasoning=reasoning)
