
import argparse
import yaml
import torch

from models.model import build_model, load_checkpoint
from models.explain import explain_image


def main():
    parser = argparse.ArgumentParser(
        description="Explain retinal image predictions with Captum"
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to target fundus image"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="models/configs/config.yaml",
        help="Path to config file"
    )
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    # Select available GPU or CPU
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    architecture = cfg["model"]["architecture"]

    # Build the same architecture used during training
    model = build_model(
        architecture=architecture,
        num_classes=cfg["model"]["num_classes"],
        pretrained=False,
    )

    model = load_checkpoint(
        model,
        cfg["model"]["checkpoint_path"],
        device,
    )

    print(f"Explaining with: {architecture}")
    print(f"Device: {device}")

    explain_image(model, args.image, cfg, device)


if __name__ == "__main__":
    main()
