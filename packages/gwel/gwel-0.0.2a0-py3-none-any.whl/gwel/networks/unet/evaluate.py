import torch
import numpy as np
import matplotlib.pyplot as plt
from unet import UNet  # Import your UNet model
from data_loader import CustomDataset  # Import your custom dataset class
from torch.utils.data import DataLoader
from torchvision import transforms
from sklearn.metrics import jaccard_score  # For IoU score

# Hyperparameters
batch_size = 8

# Prepare the dataset and DataLoader for validation
image_dir = 'path/to/val_images'
label_dir = 'path/to/val_labels'
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_dataset = CustomDataset(image_dir, label_dir, transform)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# Load the trained model
model = UNet(in_channels=3, out_channels=1).cuda()
model.load_state_dict(torch.load('unet_epoch_50.pth'))  # Load the model checkpoint
model.eval()  # Set the model to evaluation mode

# Evaluation loop
all_preds = []
all_labels = []

with torch.no_grad():  # No need to compute gradients for evaluation
    for images, labels in val_loader:
        images, labels = images.cuda(), labels.cuda()
        
        # Forward pass
        outputs = model(images)
        
        # Convert logits to binary predictions
        preds = torch.sigmoid(outputs) > 0.5
        
        all_preds.append(preds.cpu().numpy())
        all_labels.append(labels.cpu().numpy())

# Convert lists to numpy arrays
all_preds = np.concatenate(all_preds, axis=0)
all_labels = np.concatenate(all_labels, axis=0)

# Calculate the Jaccard Index (IoU)
iou = jaccard_score(all_labels.flatten(), all_preds.flatten(), average='binary')
print(f"Validation IoU: {iou:.4f}")

# Visualize some of the results
def visualize(image, label, pred):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(image.permute(1, 2, 0).cpu().numpy())
    axes[0].set_title("Image")
    axes[1].imshow(label.squeeze(), cmap='gray')
    axes[1].set_title("Ground Truth")
    axes[2].imshow(pred.squeeze(), cmap='gray')
    axes[2].set_title("Prediction")
    plt.show()

# Visualizing a few random examples
for i in range(3):
    idx = np.random.randint(0, len(val_dataset))
    image, label = val_dataset[idx]
    pred = torch.sigmoid(model(image.unsqueeze(0).cuda())).squeeze().cpu().detach() > 0.5
    visualize(image, label, pred)

