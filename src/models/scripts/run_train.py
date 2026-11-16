import yaml
import torch
from models.dataset import get_dataloaders
from models.model import build_resnet50
from models.train import train_and_evaluate


def main():
    with open("models/configs/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    train_loader, val_loader = get_dataloaders(cfg)
    model = build_resnet50(
        num_classes=cfg["model"]["num_classes"],
        pretrained=cfg["model"]["pretrained"],
    )

    train_and_evaluate(model, train_loader, val_loader, cfg, device)


if __name__ == "__main__":
    main()
