import torch
import torchvision
from torchvision import transforms
from PIL import Image

# Function to preprocess the image
def process_image(image_path):
    image = Image.open(image_path).convert("RGB")

    transform = transforms.Compose([
        transforms.ToTensor(),  # Convert the image to a tensor
    ])

    image_tensor = transform(image)
    return image_tensor

# Function to extract bounding boxes from the predictions
def get_bboxes(model, image_path, threshold=0.5, device="cpu"):
    # Preprocess the image
    image_tensor = process_image(image_path)

    # Add batch dimension (model expects a batch of images)
    image_tensor = image_tensor.unsqueeze(0).to(device)

    # Run inference
    with torch.no_grad():
        predictions = model(image_tensor)

    # Get predicted bounding boxes and scores
    pred_boxes = predictions[0]['boxes'].cpu().numpy()  # Bounding boxes
    pred_scores = predictions[0]['scores'].cpu().numpy()  # Prediction scores

    # Filter bounding boxes by confidence score
    filtered_boxes = []
    for box, score in zip(pred_boxes, pred_scores):
        if score > threshold:  # Only include boxes with score above the threshold
            filtered_boxes.append(box)

    return filtered_boxes
