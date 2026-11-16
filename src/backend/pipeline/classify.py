import torch
from PIL import Image
from torchvision import transforms, models

DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES=[]#<-dataset classes

def load_model(model_name):
    if model_name=="resnet50":
        model=models.resnet50(weights=None)#<-replace with model weights
        model.fc=torch.nn.Linear(model.fc.in_features,len(CLASS_NAMES))
        model_path=""
    elif model_name=="densenet121":
        model=models.densenet121(weights=None)#<-replace with model weights
        model.fc=torch.nn.Linear(model.fc.in_features,len(CLASS_NAMES))
        model_path=""
    else:
        raise ValueError("Unknown Model: How did you get this error?")
    checkpoint=torch.load(torch.load(model_path,map_location=device))
    model.load_state_dict(checkpoint)
    model.to(DEVICE)
    model.eval
    return model

def predict(image, model_name):
    # TODO: load fine-tuned checkpoints once; use training-time transforms.
    model = MODELS[model_name]
    image = Image.open(image).convert("RGB")
    with torch.no_grad():
        outputs = model(image)
        probs = torch.softmax(outputs, dim=1)
        pred_idx = probs.argmax(dim=1).item()
        confidence = probs[0][pred_idx].item()
    return{}
    #raise NotImplementedError("Real PyTorch inference is not integrated yet.")
