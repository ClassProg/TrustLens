import os
import glob
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


class REFUGEDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.samples = []
        self.transform = transform
        class_map = {"Non-Glaucoma": 0, "Glaucoma": 1}

        for class_name, label in class_map.items():
            folder = os.path.join(root_dir, class_name)
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
                for img_path in glob.glob(os.path.join(folder, ext)):
                    self.samples.append((img_path, label))

        if len(self.samples) == 0:
            raise RuntimeError(f"No images found in {root_dir}. Check folder structure.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
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
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    return train_transform, eval_transform


def get_dataloaders(cfg):
    train_tf, eval_tf = get_transforms(cfg["data"]["image_size"])

    train_ds = REFUGEDataset(cfg["data"]["train_dir"], transform=train_tf)
    val_ds = REFUGEDataset(cfg["data"]["val_dir"], transform=eval_tf)

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
