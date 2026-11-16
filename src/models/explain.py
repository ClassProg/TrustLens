import os
import numpy as np
import torch
from PIL import Image
import matplotlib.pyplot as plt
from skimage.segmentation import slic

from captum.attr import IntegratedGradients, LayerGradCam, Lime, LayerAttribution
from captum.attr import visualization as viz
from captum._utils.models.linear_model import SkLearnLinearRegression

from models.dataset import get_transforms


def explain_image(model, image_path, cfg, device):
    model.eval()
    img_size = cfg["data"]["image_size"]
    _, eval_tf = get_transforms(img_size)

    raw_img = Image.open(image_path).convert("RGB").resize((img_size, img_size))
    orig_np = np.array(raw_img)
    input_tensor = eval_tf(raw_img).unsqueeze(0).to(device)
    input_tensor.requires_grad = True

    # 1. Classification inference
    with torch.no_grad():
        logits = model(input_tensor)
        probs = torch.softmax(logits, dim=1)
        pred_class = torch.argmax(probs, dim=1).item()
        confidence = probs[0, pred_class].item()

    class_names = ["Non-Glaucoma", "Glaucoma"]
    print(f"Image: {os.path.basename(image_path)}")
    print(f"Prediction: {class_names[pred_class]} ({confidence:.2%})")

    # 2. Integrated Gradients
    ig = IntegratedGradients(model)
    baseline = torch.zeros_like(input_tensor)
    attr_ig = ig.attribute(
        input_tensor,
        baselines=baseline,
        target=pred_class,
        n_steps=cfg["explainability"]["ig_steps"],
    )
    attr_ig_np = np.transpose(attr_ig.squeeze().cpu().detach().numpy(), (1, 2, 0))

    # 3. Layer Grad-CAM (final ResNet50 bottleneck block)
    gradcam = LayerGradCam(model, model.layer4[-1])
    attr_gc = gradcam.attribute(input_tensor, target=pred_class)
    upsampled_gc = LayerAttribution.interpolate(attr_gc, (img_size, img_size), interpolate_mode="bilinear")
    attr_gc_np = np.transpose(upsampled_gc.squeeze(0).cpu().detach().numpy(), (1, 2, 0))

    # 4. LIME (Superpixel perturbation)
    segments = slic(
        orig_np,
        n_segments=cfg["explainability"]["lime_segments"],
        compactness=10,
        sigma=1,
        start_label=0,
    )
    feature_mask = torch.tensor(segments, dtype=torch.long).unsqueeze(0).unsqueeze(0).to(device)

    lime = Lime(model, interpretable_model=SkLearnLinearRegression())
    attr_lime = lime.attribute(
        input_tensor,
        target=pred_class,
        feature_mask=feature_mask,
        n_samples=cfg["explainability"]["lime_samples"],
        perturbations_per_eval=cfg["explainability"]["lime_batch_size"],
        baselines=0,
    )
    attr_lime_np = np.transpose(attr_lime.squeeze().cpu().detach().numpy(), (1, 2, 0))

    # 5. Plot & Save Side-by-Side Comparison
    out_dir = cfg["explainability"]["output_dir"]
    os.makedirs(out_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    save_path = os.path.join(out_dir, f"{base_name}_captum.png")

    fig, axes = plt.subplots(1, 4, figsize=(20, 5))

    axes[0].imshow(orig_np)
    axes[0].set_title(f"Original\nPred: {class_names[pred_class]} ({confidence:.1%})")
    axes[0].axis("off")

    viz.visualize_image_attr(
        attr_ig_np, orig_np, method="heat_map", sign="positive",
        plt_fig_axis=(fig, axes[1]), use_pyplot=False, title="Integrated Gradients"
    )
    viz.visualize_image_attr(
        attr_gc_np, orig_np, method="blended_heat_map", sign="positive",
        plt_fig_axis=(fig, axes[2]), use_pyplot=False, title="Grad-CAM (Layer 4)"
    )
    viz.visualize_image_attr(
        attr_lime_np, orig_np, method="blended_heat_map", sign="positive",
        plt_fig_axis=(fig, axes[3]), use_pyplot=False, title="LIME (Superpixels)"
    )

    plt.tight_layout()
    if os.path.exists(save_path):
        os.remove(save_path)
    plt.savefig(save_path, dpi=200)
    plt.close(fig)
    print(f"Saved explanation heatmap to {save_path}")
