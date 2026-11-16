import os
import yaml
import torch
import numpy as np


from PIL import Image, ImageDraw
from models.dataset import REFUGEDataset, get_transforms
from models.model import build_resnet50, load_checkpoint
from models.train import train_and_evaluate
from models.explain import explain_image


def _create_dummy_refuge(base_dir):
    """Creates a tiny 4-image synthetic REFUGE folder with textured retinal features."""
    rng = np.random.default_rng(42)
    for split in ("train", "val"):
        for cls_name in ("Glaucoma", "Non-Glaucoma"):
            folder = os.path.join(base_dir, split, cls_name)
            os.makedirs(folder, exist_ok=True)
            for i in range(2):
                # Textured background + bright simulated optic disc
                arr = rng.integers(40, 180, size=(224, 224, 3), dtype=np.uint8)
                img = Image.fromarray(arr)
                draw = ImageDraw.Draw(img)
                draw.ellipse((40, 80, 100, 140), fill=(245, 240, 210))
                img.save(os.path.join(folder, f"sample_{i}.jpg"))


def test_dataset_and_model_forward(tmp_path):
    _create_dummy_refuge(tmp_path)
    _, eval_tf = get_transforms(224)
    ds = REFUGEDataset(os.path.join(tmp_path, "train"), transform=eval_tf)
    assert len(ds) == 4

    model = build_resnet50(num_classes=2, pretrained=False)
    sample_img, label, _ = ds[0]
    logits = model(sample_img.unsqueeze(0))
    assert logits.shape == (1, 2)


def test_train_and_captum_explain_end_to_end(tmp_path):
    _create_dummy_refuge(tmp_path)

    with open("models/configs/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    # Override config to use temp directories and fast CI settings
    ckpt_path = os.path.join(tmp_path, "checkpoints", "test_resnet50.pth")
    heatmap_dir = os.path.join(tmp_path, "heatmaps")
    cfg["data"]["train_dir"] = os.path.join(tmp_path, "train")
    cfg["data"]["val_dir"] = os.path.join(tmp_path, "val")
    cfg["data"]["batch_size"] = 2
    cfg["data"]["num_workers"] = 0
    cfg["model"]["checkpoint_path"] = ckpt_path
    cfg["training"]["epochs"] = 1
    cfg["explainability"]["output_dir"] = heatmap_dir
    cfg["explainability"]["ig_steps"] = 5
    cfg["explainability"]["lime_segments"] = 10
    cfg["explainability"]["lime_samples"] = 15
    cfg["explainability"]["lime_batch_size"] = 5

    device = torch.device("cpu")
    train_tf, eval_tf = get_transforms(224)
    train_loader = torch.utils.data.DataLoader(
        REFUGEDataset(cfg["data"]["train_dir"], transform=train_tf), batch_size=2
    )
    val_loader = torch.utils.data.DataLoader(
        REFUGEDataset(cfg["data"]["val_dir"], transform=eval_tf), batch_size=2
    )

    # 1. Test 1-epoch training and checkpoint creation
    model = build_resnet50(num_classes=2, pretrained=False)
    train_and_evaluate(model, train_loader, val_loader, cfg, device)
    assert os.path.exists(ckpt_path)

    # 2. Test loading checkpoint and running IG, Grad-CAM, and LIME
    loaded_model = build_resnet50(num_classes=2, pretrained=False)
    loaded_model = load_checkpoint(loaded_model, ckpt_path, device)

    test_img = os.path.join(tmp_path, "val", "Glaucoma", "sample_0.jpg")
    explain_image(loaded_model, test_img, cfg, device)

    expected_png = os.path.join(heatmap_dir, "sample_0_captum.png")
    assert os.path.exists(expected_png)
