import argparse
import os
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import torch.nn as nn
from tqdm import tqdm
from src.UNET.unet import UNet
from src.UNET.data_loader import CocoSegmentationDataset
import numpy as np
import ast 
import pandas as pd



def iou_score(preds, targets, threshold=0.5):
    preds = torch.sigmoid(preds) > threshold
    targets = targets > threshold

    preds = preds.view(preds.size(0), preds.size(1), -1)
    targets = targets.view(targets.size(0), targets.size(1), -1)

    intersection = torch.sum(preds & targets, dim=2).float()
    union = torch.sum(preds | targets, dim=2).float()
    union = union * (union > 10)
    iou = intersection / union
    return np.array(torch.nanmean(iou,dim=0).cpu())

def train(model, train_loader, criterion, optimizer, device, epoch, iou_threshold = 0.5):
    model.train()
    running_loss = 0.0
    running_iou = np.array([0.0,0.0,0.0])
    total_samples = 0 
    total_samples_iou_score = np.array([0.0,0.0,0.0])
  
    for i, (inputs, targets) in enumerate(tqdm(train_loader)):
        inputs, targets = inputs.to(device), targets.to(device)
     
        optimizer.zero_grad()
        outputs = model(inputs)

        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        
        iou = iou_score(outputs, targets, threshold=iou_threshold)
        running_loss += loss.item()

        running_iou = running_iou + np.nan_to_num(iou, nan=0.0)
        total_samples += 1
        total_samples_iou_score += (~np.isnan(iou)).astype(int)
        
    avg_loss = running_loss / total_samples
    avg_iou = running_iou / total_samples_iou_score
    
    print(f"Epoch {epoch}. Avg loss: {avg_loss:.3f}, Avg IoU 1: {avg_iou[0]:.3f}, Avg IoU 2: {avg_iou[1]:.3f}, Avg Iou 3: {avg_iou[2]:.3f}")
    
    df = pd.DataFrame([{
        'Epoch': epoch,
        'Avg Loss': avg_loss,
        'Avg IoU 1': avg_iou[0],
        'Avg IoU 2': avg_iou[1],
        'Avg IoU 3':avg_iou[2]
    }])

    return df

def validate(model, val_loader, criterion, device):
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            val_loss += loss.item()

    print(f"Validation loss: {val_loss / len(val_loader):.4f}")

def main(args):
    
    categories = ast.literal_eval(args.categories)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = UNet(in_channels=args.in_channels, out_channels=len(categories)).to(device)

    criterion = nn.BCEWithLogitsLoss() #if args.out_channels == 1 else nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    
    train_dataset = CocoSegmentationDataset(image_dir = args.train_images_dir, coco_json = args.train_annotations ,categories = categories)
   # val_dataset = CocoSegmentationDataset(image_dir = args.train_images_dir, coco_json = args.train_annotations ,category = args.category)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    #val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

    # Training loop
    train_data = pd.DataFrame()
    for epoch in range(args.epochs):
        new_row = train(model, train_loader, criterion, optimizer, device, epoch)
        train_data = pd.concat([train_data, new_row], ignore_index=True)
        train_data.to_csv(args.train_metrics_path,index=False)
        # Validate at the end of each epoch
     #   if (epoch + 1) % args.val_interval == 0:
      #      print("Validating...")
       #     validate(model, val_loader, criterion, device)

        # Save the model checkpoint after each epoch
        if (epoch + 1) % args.save_interval == 0:
            checkpoint_path = os.path.join(args.save_dir, f"unet_epoch_{epoch + 1}.pth")
            torch.save(model.state_dict(), checkpoint_path)
            print(f"Saved checkpoint: {checkpoint_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a U-Net model")

    parser.add_argument('-td','--train_images_dir', type=str, required=True, help="Path to directory of training images")
    parser.add_argument('-ta','--train_annotations', type=str, required=True, help="Path to training annotations")
    parser.add_argument('-vd','--val_images_dir', type=str, required=True, help="Path to directory of validation images")
    parser.add_argument('-va','--val_annotations', type=str, required=True, help="Path to validation annotations")
    parser.add_argument('-c','--categories', type=str, required=True, help="Integer tag for annotation categories")
    parser.add_argument('-s','--save_dir', type=str, required=True, help="Directory to save model checkpoints")

    parser.add_argument('--epochs', type=int, default=10, help="Number of epochs")
    parser.add_argument('--batch_size', type=int, default=16, help="Batch size")
    parser.add_argument('--lr', type=float, default=1e-4, help="Learning rate")
    parser.add_argument('--in_channels', type=int, default=1, help="Number of input channels (1 for grayscale images)")
    parser.add_argument('--out_channels', type=int, default=1, help="Number of output channels (1 for binary segmentation)")
    parser.add_argument('--save_interval', type=int, default=1, help="How often to save model checkpoints (in epochs)")
    parser.add_argument('--val_interval', type=int, default=1, help="How often to validate the model (in epochs)")
    parser.add_argument('--train_metrics_path',type=str,default="train-data.csv",help="Path to output train metrics csv")
    args = parser.parse_args()

    # Check that paths exist
    assert os.path.exists(args.train_images_dir), f"Train images path '{args.train_images_dir}' not found."
    assert os.path.exists(args.train_annotations), f"Train masks path '{args.train_annotations}' not found."
    assert os.path.exists(args.val_images_dir), f"Validation images path '{args.val_images_dir}' not found."
    assert os.path.exists(args.val_annotations), f"Validation masks path '{args.val_annotations}' not found."
    os.makedirs(args.save_dir, exist_ok=True)

    # Start training
    main(args)

