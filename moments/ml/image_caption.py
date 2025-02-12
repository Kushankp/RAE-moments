import torch
from PIL import Image
from lavis.models import load_model_and_preprocess

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_caption_tools(name='blip_caption', model_type='base_coco'):
    model, vis_processors, _ = load_model_and_preprocess(name=name, model_type=model_type, is_eval=True, device=device)
    return model, vis_processors


def caption_image(model, vis_processors, image_path):
    # process the image
    raw_image = Image.open(image_path).convert("RGB")
    image = vis_processors["eval"](raw_image).unsqueeze(0).to(device)
    # generate the caption
    caption = model.generate({"image": image})
    return caption[0]