import os
import glob
import shutil
import argparse
import pandas as pd


def organize_by_prefix(raw_dir, output_dir, copy_files=True):
    glaucoma_dir = os.path.join(output_dir, "Glaucoma")
    non_glaucoma_dir = os.path.join(output_dir, "Non-Glaucoma")
    os.makedirs(glaucoma_dir, exist_ok=True)
    os.makedirs(non_glaucoma_dir, exist_ok=True)

    transfer = shutil.copy2 if copy_files else shutil.move
    counts = {"Glaucoma": 0, "Non-Glaucoma": 0, "Skipped": 0}

    image_paths = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
        image_paths.extend(glob.glob(os.path.join(raw_dir, "**", ext), recursive=True))

    for path in image_paths:
        fname = os.path.basename(path)
        lower_name = fname.lower()

        # Skip segmentation mask files (typically .bmp masks in REFUGE)
        if "mask" in lower_name or lower_name.endswith(".bmp"):
            counts["Skipped"] += 1
            continue

        if lower_name.startswith("g"):
            transfer(path, os.path.join(glaucoma_dir, fname))
            counts["Glaucoma"] += 1
        elif lower_name.startswith("n"):
            transfer(path, os.path.join(non_glaucoma_dir, fname))
            counts["Non-Glaucoma"] += 1
        else:
            counts["Skipped"] += 1

    print(f"Prefix sorting complete -> {output_dir}: {counts}")


def organize_by_label_file(raw_dir, label_file, output_dir, copy_files=True):
    glaucoma_dir = os.path.join(output_dir, "Glaucoma")
    non_glaucoma_dir = os.path.join(output_dir, "Non-Glaucoma")
    os.makedirs(glaucoma_dir, exist_ok=True)
    os.makedirs(non_glaucoma_dir, exist_ok=True)

    transfer = shutil.copy2 if copy_files else shutil.move

    # Load CSV or Excel ground-truth file
    if label_file.endswith(".csv"):
        df = pd.read_csv(label_file)
    else:
        df = pd.read_excel(label_file)

    # Auto-detect image filename column and binary label column
    img_col = next(c for c in df.columns if "img" in c.lower() or "name" in c.lower() or "file" in c.lower())
    lbl_col = next(c for c in df.columns if "label" in c.lower() or "glaucoma" in c.lower())

    # Index all images in raw_dir by filename
    file_lookup = {}
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        for path in glob.glob(os.path.join(raw_dir, "**", ext), recursive=True):
            file_lookup[os.path.basename(path)] = path

    counts = {"Glaucoma": 0, "Non-Glaucoma": 0, "Missing": 0}
    for _, row in df.iterrows():
        fname = str(row[img_col]).strip()
        label = int(row[lbl_col])

        if fname not in file_lookup:
            counts["Missing"] += 1
            continue

        target_folder = glaucoma_dir if label == 1 else non_glaucoma_dir
        transfer(file_lookup[fname], os.path.join(target_folder, fname))
        counts["Glaucoma" if label == 1 else "Non-Glaucoma"] += 1

    print(f"Label-file sorting complete -> {output_dir}: {counts}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort raw REFUGE images into class folders.")
    parser.add_argument("--raw_dir", type=str, required=True, help="Folder with raw downloaded images")
    parser.add_argument("--out_dir", type=str, required=True, help="Destination split folder (e.g. models/data/REFUGE/train)")
    parser.add_argument("--labels", type=str, default=None, help="Optional path to .xlsx or .csv ground-truth file")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying them")
    args = parser.parse_args()

    if args.labels:
        organize_by_label_file(args.raw_dir, args.labels, args.out_dir, copy_files=not args.move)
    else:
        organize_by_prefix(args.raw_dir, args.out_dir, copy_files=not args.move)
