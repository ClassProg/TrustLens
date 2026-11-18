
import argparse
import yaml
import torch

from models.dataset import get_dataloaders
from models.model import build_model, load_checkpoint
from models.evaluate import evaluate_model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="models/configs/config.yaml",
    )
    parser.add_argument(
        "--checkpoint",
        required=True,
    )
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    model = build_model(
        architecture=cfg["model"]["architecture"],
        num_classes=cfg["model"]["num_classes"],
        pretrained=False,
    )

    model = load_checkpoint(
        model,
        args.checkpoint,
        device,
    )

    _, val_loader = get_dataloaders(cfg)

    print(f"Evaluating: {args.checkpoint}")
    print(f"Device: {device}")

    print(
        f"Optic-disc cropping: "
        f"{cfg['data'].get('crop_optic_disc', True)}"
    )
    print(
        f"Crop fraction: "
        f"{cfg['data'].get('crop_fraction', 0.45)}"
    )

    evaluate_model(
        model,
        val_loader,
        device,
        cfg,
        args.checkpoint,
    )


if __name__ == "__main__":
    main()
