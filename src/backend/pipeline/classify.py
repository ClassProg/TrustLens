import torch
from PIL import Image
from torchvision import transforms, models
from models.model import build_resnet50, load_checkpoint
from models.dataset import get_transforms

#assigns the model to use GPU resources if they are available, if not it uses CPU
DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES=[]#<-dataset classes

#checks for which model was selected and loads the correct one
#NOTE:right now there is no path for either model or any normalization/transformation logic for either model
def load_model(model_name):
    if model_name=="resnet50":
        model=build_resnet50()
        path="models/outputs/checkpoints/resnet50_best.pth"
    elif model_name=="densenet121":
        #model=build_densenet121()
        #model_path=""
        pass
    else:
        raise ValueError("Unknown Model: How did you get this error?")
    load_checkpoint(model,path,DEVICE)
    return model
    
#holds the model(s) that are loaded
MODELS = {}

#runs the loaded model with the given image and returns the classification and confidence
def predict(image, model_name):
    # TODO: load fine-tuned checkpoints once; use training-time transforms.
    model = load_model(model_name)
    transforms=get_transforms()
    image = Image.open(image).convert("RGB")
    with torch.no_grad():
        outputs = model(image)
        probs = torch.softmax(outputs, dim=1)
        pred_idx = probs.argmax(dim=1).item()
        confidence = probs[0][pred_idx].item()
    return{"class_index": pred_idx,"class_name": CLASS_NAMES[pred_idx],"confidence": confidence}
