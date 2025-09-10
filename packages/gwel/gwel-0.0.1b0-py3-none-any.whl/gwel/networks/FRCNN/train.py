import os
from tqdm import tqdm
import torch
import torchvision
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from pycocotools.coco import COCO
import numpy as np
from torch.utils.data import Dataset
import json
from PIL import Image
from gwel.FRCNN.dataset import CocoDataset

import torch
import numpy as np

def iou(box1, box2):
    """Calculate the Intersection over Union (IoU) of two bounding boxes."""
    x1, y1, x2, y2 = box1
    x1_gt, y1_gt, x2_gt, y2_gt = box2

    # Compute the area of intersection
    inter_x1 = max(x1, x1_gt)
    inter_y1 = max(y1, y1_gt)
    inter_x2 = min(x2, x2_gt)
    inter_y2 = min(y2, y2_gt)
    
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    
    # Compute the area of both boxes
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2_gt - x1_gt) * (y2_gt - y1_gt)
    
    # Compute IoU
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0

def compute_precision_recall(pred_boxes, gt_boxes, pred_labels, gt_labels, iou_threshold=0.5):
    """
    Compute Precision and Recall based on bounding box predictions and ground truth boxes.

    Arguments:
    - pred_boxes: List of tensors of predicted bounding boxes for each image [N, 4]
    - gt_boxes: List of tensors of ground truth bounding boxes for each image [M, 4]
    - pred_labels: List of tensors of predicted labels for each image [N]
    - gt_labels: List of tensors of ground truth labels for each image [M]
    - iou_threshold: IoU threshold to classify true positives

    Returns:
    - precision: Precision score
    - recall: Recall score
    """
    tp = 0
    fp = 0
    fn = 0

    for image_pred_boxes, image_gt_boxes, image_pred_labels, image_gt_labels in zip(pred_boxes, gt_boxes, pred_labels, gt_labels):
        # Match predicted boxes to ground truth boxes
        matched_gt_boxes = set()  # Keep track of matched ground truth boxes
        
        for i, pred_box in enumerate(image_pred_boxes):
            pred_label = image_pred_labels[i]
            
            best_iou = 0
            best_gt_idx = -1
            
            # Find the best matching ground truth box
            for j, gt_box in enumerate(image_gt_boxes):
                gt_label = image_gt_labels[j]
                
                if pred_label == gt_label:  # Only match boxes of the same class
                    iou_score = iou(pred_box, gt_box)
                    if iou_score > best_iou:
                        best_iou = iou_score
                        best_gt_idx = j

            # If the IoU is above the threshold, it's a true positive
            if best_iou >= iou_threshold:
                tp += 1  # True positive: valid match
                matched_gt_boxes.add(best_gt_idx)  # Mark this ground truth box as matched
            else:
                fp += 1  # False positive: no valid match
        
        # False negatives are the unmatched ground truth boxes
        fn += len(image_gt_boxes) - len(matched_gt_boxes)

    # Compute precision and recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    return precision, recall




def FRCNNtrain(images_dir, annotations_file, batch_size=1, num_epochs = 10):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load pre-trained Faster R-CNN model with ResNet-50 backbone and FPN
    model = fasterrcnn_resnet50_fpn(pretrained=True)

    # Update the model's classifier to fit the number of classes in your dataset
    num_classes = 2  # Change this according to your dataset (including background as class 0)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = torchvision.models.detection.faster_rcnn.FastRCNNPredictor(in_features, num_classes)

    model.to(device)

    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.Adam(params, lr=0.0001)

    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)


    ## dataloader change this depending on the dataset
    img_dir = images_dir
    ann_file = annotations_file

    transform = transforms.Compose([
        transforms.ToTensor(),  # Converts the image to a tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalizes the image
    ])

    dataset = CocoDataset(img_dir=img_dir, ann_file=ann_file, transform=transform)
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=lambda x: tuple(zip(*x)))



    for epoch in range(num_epochs):
        model.train()
        
        total_loss = 0.0
        total_precision = 0.0
        total_recall = 0.0
        total_samples = 0

        # Wrap your DataLoader in tqdm to show a progress bar
        for images, targets in tqdm(data_loader, desc=f"Training Epoch {epoch + 1}/{num_epochs}", total=len(data_loader)):
            images = [image.to(device) for image in images]
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
            
            optimizer.zero_grad()
            
            # Forward pass
            loss_dict = model(images, targets)
            
            # Compute total loss
            losses = sum(loss for loss in loss_dict.values())
            total_loss += losses.item()

            # Backward pass and optimization
            losses.backward()
            optimizer.step()

            # Get predictions
            with torch.no_grad():
                model.eval()
                predictions = model(images)
                model.train()

            # Collect predicted boxes and labels
            pred_boxes = [prediction['boxes'] for prediction in predictions]
            pred_labels = [prediction['labels'] for prediction in predictions]

            # Collect ground truth boxes and labels
            gt_boxes = [target['boxes'] for target in targets]
            gt_labels = [target['labels'] for target in targets]

            # Compute Precision and Recall
            precision, recall = compute_precision_recall(pred_boxes, gt_boxes, pred_labels, gt_labels, iou_threshold=0.5)
            
            total_precision += precision
            total_recall += recall
            total_samples += 1
            
        # Average Precision and Recall for the epoch
        avg_loss = total_loss / len(data_loader)
        avg_precision = total_precision / total_samples
        avg_recall = total_recall / total_samples

        # Print epoch metrics
        print(f"Epoch [{epoch + 1}/{num_epochs}] - Loss: {avg_loss:.4f}, Precision: {avg_precision:.4f}, Recall: {avg_recall:.4f}")
        
    return model 


