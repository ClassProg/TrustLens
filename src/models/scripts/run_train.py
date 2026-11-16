import yaml
import torch

from models.dataset import get_dataloaders
from models.model import build_model
from models.train import train_and_evaluate


def main():
    # Load configuration
    with open("models/configs/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    # Select available GPU or CPU
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print(f"Training on device: {device}")

    # Load training and validation datasets
    train_loader, val_loader = get_dataloaders(cfg)

    # Build selected model architecture
    model = build_model(
        architecture=cfg["model"]["architecture"],
        num_classes=cfg["model"]["num_classes"],
        pretrained=cfg["model"]["pretrained"],
    )

    print(f"Training model: {cfg['model']['architecture']}")

    # Train and validate model
    train_and_evaluate(
        model,
        train_loader,
        val_loader,
        cfg,
        device,
    )


if __name__ == "__main__":
    main()