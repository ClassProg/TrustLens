
import os
import glob
import pandas as pd

from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from models.preprocessing.optic_disc import crop_optic_disc


class REFUGEDataset(Dataset):
    def __init__(
        self,
        root_dir,
        transform=None,
        labels_file=None,
        crop_disc=True,
        crop_fraction=0.45,
    ):
        self.samples = []
        self.transform = transform
        self.crop_disc = crop_disc
        self.crop_fraction = crop_fraction

        if labels_file is not None:
            df = pd.read_excel(labels_file)

            required = {"ImgName", "Glaucoma Label"}

            if not required.issubset(df.columns):
                raise ValueError(
                    f"Missing required columns: "
                    f"{required - set(df.columns)}"
                )

            for _, row in df.iterrows():
                filename = str(row["ImgName"]).strip()
                label = int(row["Glaucoma Label"])

                img_path = os.path.join(root_dir, filename)

                if label not in (0, 1):
                    raise ValueError(
                        f"Invalid label for {filename}: {label}"
                    )

                if not os.path.isfile(img_path):
                    raise FileNotFoundError(
                        f"Image listed in Excel not found: {img_path}"
                    )

                self.samples.append((img_path, label))

        else:
            class_map = {
                "Non-Glaucoma": 0,
                "Glaucoma": 1,
            }

            for class_name, label in class_map.items():
                folder = os.path.join(root_dir, class_name)

                for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
                    for img_path in glob.glob(
                        os.path.join(folder, ext)
                    ):
                        self.samples.append((img_path, label))

        if len(self.samples) == 0:
            raise RuntimeError(
                f"No images found in {root_dir}. "
                "Check dataset paths."
            )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]

        with Image.open(img_path) as img:
            image = img.convert("RGB")

        # Crop around the automatically detected optic disc.
        # No segmentation masks or labels are used for cropping.
        if self.crop_disc:
            image = crop_optic_disc(
                image,
                crop_fraction=self.crop_fraction,
            )

        if self.transform:
            image = self.transform(image)

        return image, label, img_path


def get_transforms(image_size=224):
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]

    train_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),

        # Keep existing color augmentation
        transforms.ColorJitter(
            brightness=0.10,
            contrast=0.10,
            saturation=0.05,
        ),

        transforms.ToTensor(),
        transforms.Normalize(
            mean=imagenet_mean,
            std=imagenet_std,
        ),
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=imagenet_mean,
            std=imagenet_std,
        ),
    ])

    return train_transform, eval_transform


def get_dataloaders(cfg):
    train_tf, eval_tf = get_transforms(
        cfg["data"]["image_size"]
    )

    crop_disc = cfg["data"].get(
        "crop_optic_disc", True
    )

    crop_fraction = cfg["data"].get(
        "crop_fraction", 0.45
    )

    train_ds = REFUGEDataset(
        cfg["data"]["train_dir"],
        transform=train_tf,
        crop_disc=crop_disc,
        crop_fraction=crop_fraction,
    )

    val_ds = REFUGEDataset(
        cfg["data"]["val_dir"],
        transform=eval_tf,
        labels_file=cfg["data"]["val_labels"],
        crop_disc=crop_disc,
        crop_fraction=crop_fraction,
    )

    train_loader = DataLoader(
        train_ds,
        batch_size=cfg["data"]["batch_size"],
        shuffle=True,
        num_workers=cfg["data"]["num_workers"],
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=cfg["data"]["batch_size"],
        shuffle=False,
        num_workers=cfg["data"]["num_workers"],
    )

    return train_loader, val_loader
