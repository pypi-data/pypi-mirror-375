import os 
import torch
from PIL import Image
from pycocotools.coco import COCO
from torch.utils.data import Dataset
import json

class CocoDataset(Dataset):
    def __init__(self, img_dir, ann_file, transform=None):
        self.img_dir = img_dir
        self.transform = transform
        
        # Load COCO annotations
        with open(ann_file, 'r') as f:
            self.coco_data = json.load(f)
        
        self.coco = COCO(ann_file)
        self.img_ids = list(self.coco.imgs.keys())
        
    def __len__(self):
        return len(self.img_ids)

    def __getitem__(self, idx):
        img_id = self.img_ids[idx]
        img_info = self.coco.imgs[img_id]
        img_path = os.path.join(self.img_dir, img_info['file_name'])
        
        # Load image
        image = Image.open(img_path).convert("RGB")
        
        # Get annotations for the image
        ann_ids = self.coco.getAnnIds(imgIds=img_id)
        anns = self.coco.loadAnns(ann_ids)
        
        boxes = []
        labels = []
        for ann in anns:
            x, y, w, h = ann['bbox']
            boxes.append([x, y, x + w, y + h])  # COCO format: [x, y, x+w, y+h]
            # If your annotations are just the background (0), change them to 1 for object class
            labels.append(1)  # Object class label set to 1
        
        boxes = torch.tensor(boxes, dtype=torch.float32)
        labels = torch.tensor(labels, dtype=torch.int64)
        
        target = {'boxes': boxes, 'labels': labels}
        
        if self.transform:
            image = self.transform(image)
        
        return image, target
