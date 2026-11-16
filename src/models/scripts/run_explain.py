import argparse
import yaml
import torch
from models.model import build_resnet50, load_checkpoint
from models.explain import explain_image


def main():
    parser = argparse.ArgumentParser(description="Explain REFUGE prediction with Captum")
    parser.add_argument("--image", type=str, required=True, help="Path to target fundus image")
    parser.add_argument("--config", type=str, default="models/configs/config.yaml", help="Path to config file")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = build_resnet50(num_classes=cfg["model"]["num_classes"], pretrained=False)
    model = load_checkpoint(model, cfg["model"]["checkpoint_path"], device)

    explain_image(model, args.image, cfg, device)


if __name__ == "__main__":
    main()
