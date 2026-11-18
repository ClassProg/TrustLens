
import os
import numpy as np
import torch
from PIL import Image
import matplotlib.pyplot as plt
from skimage.segmentation import slic

from captum.attr import (
    IntegratedGradients,
    LayerGradCam,
    Lime,
    LayerAttribution,
)
from captum.attr import visualization as viz
from captum._utils.models.linear_model import SkLearnLinearRegression

from models.dataset import get_transforms
from models.preprocessing.optic_disc import crop_optic_disc


def get_gradcam_target_layer(model, architecture):
    """
    Select the appropriate Grad-CAM target layer
    for the chosen model architecture.
    """
    architecture = architecture.lower()

    if architecture == "resnet50":
        return model.layer4[-1]

    elif architecture == "densenet121":
        return model.features.norm5

    else:
        raise ValueError(
            f"Unsupported architecture for Grad-CAM: {architecture}"
        )


def explain_image(model, image_path, cfg, device):
    model = model.to(device)
    model.eval()

    architecture = cfg["model"]["architecture"].lower()
    img_size = cfg["data"]["image_size"]

    _, eval_tf = get_transforms(img_size)

    # 1. Load the original retinal image
    with Image.open(image_path) as image:
        raw_img = image.convert("RGB")

    # 2. Apply optic-disc-centered cropping
    # Uses the same automatic locator as dataset.py.
    # Does not require segmentation masks.
    crop_enabled = cfg["data"].get("crop_optic_disc", True)
    crop_fraction = cfg["data"].get("crop_fraction", 0.45)

    if crop_enabled:
        raw_img = crop_optic_disc(
            raw_img,
            crop_fraction=crop_fraction,
        )

    # 3. Resize the cropped image to the model input size
    raw_img = raw_img.resize((img_size, img_size))

    # Keep the image for Captum visualizations
    orig_np = np.array(raw_img)

    # Apply evaluation transforms and normalization
    input_tensor = eval_tf(raw_img).unsqueeze(0).to(device)
    input_tensor.requires_grad_(True)

    # 4. Classification inference
    with torch.no_grad():
        logits = model(input_tensor)
        probs = torch.softmax(logits, dim=1)

        threshold = cfg["model"].get(
            "prediction_threshold", 0.5
        )

        pred_class = int(
            probs[0, 1].item() >= threshold
        )

        confidence = probs[0, pred_class].item()

    class_names = ["Non-Glaucoma", "Glaucoma"]

    print(f"Model: {architecture}")
    print(f"Image: {os.path.basename(image_path)}")
    print(f"Optic-disc cropping: {crop_enabled}")

    print(
        f"Prediction: {class_names[pred_class]} "
        f"({confidence:.2%})"
    )

    # 5. Integrated Gradients
    ig = IntegratedGradients(model)

    baseline = torch.zeros_like(input_tensor)

    attr_ig = ig.attribute(
        input_tensor,
        baselines=baseline,
        target=pred_class,
        n_steps=cfg["explainability"]["ig_steps"],
    )

    attr_ig_np = np.transpose(
        attr_ig.squeeze(0).detach().cpu().numpy(),
        (1, 2, 0),
    )

    # 6. Layer Grad-CAM
    # ResNet50 and DenseNet121 use different layers.
    target_layer = get_gradcam_target_layer(
        model,
        architecture,
    )

    gradcam = LayerGradCam(model, target_layer)

    attr_gc = gradcam.attribute(
        input_tensor,
        target=pred_class,
        relu_attributions=True,
    )

    upsampled_gc = LayerAttribution.interpolate(
        attr_gc,
        (img_size, img_size),
        interpolate_mode="bilinear",
    )

    attr_gc_np = np.transpose(
        upsampled_gc.squeeze(0).detach().cpu().numpy(),
        (1, 2, 0),
    )

    # 7. LIME (Superpixel perturbation)
    segments = slic(
        orig_np,
        n_segments=cfg["explainability"]["lime_segments"],
        compactness=10,
        sigma=1,
        start_label=0,
    )

    feature_mask = (
        torch.tensor(segments, dtype=torch.long)
        .unsqueeze(0)
        .unsqueeze(0)
        .to(device)
    )

    lime = Lime(
        model,
        interpretable_model=SkLearnLinearRegression(),
    )

    attr_lime = lime.attribute(
        input_tensor,
        target=pred_class,
        feature_mask=feature_mask,
        n_samples=cfg["explainability"]["lime_samples"],
        perturbations_per_eval=cfg["explainability"]["lime_batch_size"],
        baselines=0,
    )

    attr_lime_np = np.transpose(
        attr_lime.squeeze(0).detach().cpu().numpy(),
        (1, 2, 0),
    )

    # 8. Plot and save side-by-side comparison
    out_dir = cfg["explainability"]["output_dir"]
    os.makedirs(out_dir, exist_ok=True)

    base_name = os.path.splitext(
        os.path.basename(image_path)
    )[0]

    checkpoint_name = os.path.splitext(
        os.path.basename(cfg["model"]["checkpoint_path"])
    )[0]

    save_path = os.path.join(
        out_dir,
        f"{base_name}_{checkpoint_name}_captum.png",
    )

    fig, axes = plt.subplots(1, 4, figsize=(20, 5))

    axes[0].imshow(orig_np)
    axes[0].set_title(
        f"{'Optic Disc Crop' if crop_enabled else 'Original'} "
        f"({architecture})\n"
        f"Pred: {class_names[pred_class]} ({confidence:.1%})"
    )
    axes[0].axis("off")

    viz.visualize_image_attr(
        attr_ig_np,
        orig_np,
        method="heat_map",
        sign="positive",
        plt_fig_axis=(fig, axes[1]),
        use_pyplot=False,
        title="Integrated Gradients",
    )

    viz.visualize_image_attr(
        attr_gc_np,
        orig_np,
        method="blended_heat_map",
        sign="positive",
        plt_fig_axis=(fig, axes[2]),
        use_pyplot=False,
        title=f"Grad-CAM ({architecture})",
    )

    viz.visualize_image_attr(
        attr_lime_np,
        orig_np,
        method="blended_heat_map",
        sign="positive",
        plt_fig_axis=(fig, axes[3]),
        use_pyplot=False,
        title="LIME (Superpixels)",
    )

    plt.tight_layout()

    plt.savefig(
        save_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Saved explanation heatmap to {save_path}")

    return save_path
