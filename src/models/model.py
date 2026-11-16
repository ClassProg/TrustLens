import os
import torch
import torch.nn as nn
from torchvision import models


def build_resnet50(num_classes=2, pretrained=True):
    weights = models.ResNet50_Weights.DEFAULT if pretrained else None
    model = models.resnet50(weights=weights)

    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)

    return model


def build_densenet121(num_classes=2, pretrained=True):
    weights = models.DenseNet121_Weights.DEFAULT if pretrained else None
    model = models.densenet121(weights=weights)

    in_features = model.classifier.in_features
    model.classifier = nn.Linear(in_features, num_classes)

    return model


def build_model(architecture, num_classes=2, pretrained=True):
    if architecture == "resnet50":
        return build_resnet50(num_classes, pretrained)

    elif architecture == "densenet121":
        return build_densenet121(num_classes, pretrained)

    else:
        raise ValueError(f"Unsupported architecture: {architecture}")


def load_checkpoint(model, checkpoint_path, device):
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(
            f"Checkpoint not found at {checkpoint_path}. Run training first."
        )

    state_dict = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=True,
    )
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    return model