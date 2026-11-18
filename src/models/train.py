
import os
import torch
import torch.nn as nn


def train_and_evaluate(model, train_loader, val_loader, cfg, device):
    model.to(device)

    weights = torch.tensor(
        cfg["training"]["class_weights"],
        dtype=torch.float32,
        device=device,
    )
    criterion = nn.CrossEntropyLoss(weight=weights)

    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=cfg["training"]["learning_rate"],
        weight_decay=cfg["training"]["weight_decay"],
    )

    best_val_loss = float("inf")
    patience = cfg["training"].get("early_stopping_patience", 3)
    epochs_without_improvement = 0

    ckpt_path = cfg["model"]["checkpoint_path"]
    os.makedirs(os.path.dirname(ckpt_path), exist_ok=True)

    # Confirm which label represents glaucoma in dataset.py.
    positive_class = cfg["training"].get("positive_class", 1)

    for epoch in range(cfg["training"]["epochs"]):
        # Training phase
        model.train()

        # Keep BatchNorm running statistics fixed when fine-tuning
        # a pretrained ResNet backbone.
        if cfg["model"].get("freeze_backbone", False):
            for module in model.modules():
                if isinstance(module, nn.BatchNorm2d):
                    module.eval()

        train_loss = 0.0

        for images, labels, _ in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * images.size(0)

        train_loss /= len(train_loader.dataset)

        # Validation phase
        model.eval()
        val_loss = 0.0
        correct = 0

        tp = tn = fp = fn = 0

        with torch.no_grad():
            for images, labels, _ in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)

                preds = torch.argmax(outputs, dim=1)
                correct += (preds == labels).sum().item()

                tp += ((preds == positive_class) &
                       (labels == positive_class)).sum().item()
                tn += ((preds != positive_class) &
                       (labels != positive_class)).sum().item()
                fp += ((preds == positive_class) &
                       (labels != positive_class)).sum().item()
                fn += ((preds != positive_class) &
                       (labels == positive_class)).sum().item()

        val_loss /= len(val_loader.dataset)
        val_acc = correct / len(val_loader.dataset)

        sensitivity = tp / (tp + fn) if tp + fn else 0.0
        specificity = tn / (tn + fp) if tn + fp else 0.0
        balanced_acc = (sensitivity + specificity) / 2

        print(
            f"Epoch [{epoch+1}/{cfg['training']['epochs']}] | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Acc: {val_acc:.2%}"
        )

        print(
            f"  Sensitivity: {sensitivity:.2%} | "
            f"Specificity: {specificity:.2%} | "
            f"Balanced Acc: {balanced_acc:.2%}"
        )

        print(
            f"  Confusion Matrix: TP={tp}, TN={tn}, "
            f"FP={fp}, FN={fn}"
        )

        # Save best checkpoint
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_without_improvement = 0

            torch.save(model.state_dict(), ckpt_path)
            print(f"  -> Saved new best checkpoint to {ckpt_path}")
        else:
            epochs_without_improvement += 1

        # Early stopping
        if patience > 0 and epochs_without_improvement >= patience:
            print(
                f"Early stopping at epoch {epoch+1}. "
                f"Best validation loss: {best_val_loss:.4f}"
            )
            break

    return model
