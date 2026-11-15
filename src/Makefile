VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
CONFIG = models/configs/config.yaml
DEFAULT_IMAGE = models/data/REFUGE/val/Glaucoma/g0001.jpg

.PHONY: help setup check train explain clean-venv

help:
	@echo "Available commands:"
	@echo "  make setup                     Create .venv and install requirements.txt"
	@echo "  make check                     Verify imports and GPU inside .venv"
	@echo "  make train                     Train ResNet50 using .venv"
	@echo "  make explain IMAGE=<path>      Run Captum explanations using .venv"

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@touch $(VENV)/bin/activate

setup: $(VENV)/bin/activate

check: setup
	PYTHONPATH=. $(PYTHON) -c "import torch, captum, skimage, yaml; \
	from models.model import build_resnet50; \
	print('PyTorch:', torch.__version__, '| CUDA available:', torch.cuda.is_available()); \
	print('All project modules imported successfully!')"

train: setup
	PYTHONPATH=. $(PYTHON) -m models.scripts.run_train

explain: setup
	PYTHONPATH=. $(PYTHON) -m models.scripts.run_explain --image $(or $(IMAGE),$(DEFAULT_IMAGE)) --config $(CONFIG)

clean-venv:
	rm -rf $(VENV)
