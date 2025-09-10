import torch
import numpy as np
import os
from torchvision import transforms
import cv2 
from gwel.UNET.unet import UNet 
from gwel.UNET.data_loader import CenterPad
from gwel.UNET.data_loader import CocoSegmentationDataset
from gwel.UNET.data_loader import DataLoader
import pandas as pd
from tqdm import tqdm

def load_model(model_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = UNet(in_channels=3, out_channels=3) 
    model.load_state_dict(torch.load(model_path, map_location=device,weights_only=True))
    model.to(device)
    model.eval()  
    return model, device

def load_image(image_path):
    image_bgr = cv2.imread(image_path)
    image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image = torch.as_tensor(image,dtype=torch.float).permute(2,0,1) / 255
    return image


def display(image):
    image = np.uint8(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cv2.imshow('image',image)

    # Wait for a key press to close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def run_inference(model, device, image, centerpad, threshold = 0.5,post_process=True):
    image_padded = centerpad(image)
    image_padded = image_padded.to(device)
    
    with torch.no_grad():  # Inference mode (no gradients)
       output = model(image_padded)
       output = torch.sigmoid(output)  # Apply sigmoid for binary segmentation
    
    output = output.cpu().numpy()
    
    masks =  np.array((output > threshold)*255,dtype=np.uint8)

    _, crop_height, crop_width = image.shape
    _, height, width = masks.shape
    
    left = (width - crop_width) // 2
    top = (height - crop_height) // 2
    right = (width + crop_width) // 2
    bottom = (height +crop_height) // 2 
    
    cropped_masks = masks[:,top:bottom, left:right]
    
    if post_process:
        cropped_masks = post_process_masks(cropped_masks)

    return cropped_masks

def post_process_masks(masks):
    mask1 = masks[0]  
    mask2 = masks[1]
    mask3 = masks[2]

    mask1 = (mask1 > 0).astype(np.uint8) * 255
    mask2 = (mask2 > 0).astype(np.uint8) * 255
    mask3 = (mask3 > 0).astype(np.uint8) * 255
    
   #num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask1, 8, cv2.CV_32S)
    #if np.max(mask1) > 0 :

    #	largest_component = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    
    #	mask1 = (labels == largest_component).astype(np.uint8) * 255

    mask2 = mask2 * (mask1 // 255)
    mask3 = mask3 * (mask1 // 255)

    combined_masks = np.stack((mask1, mask2, mask3), axis=0)

    return combined_masks


def draw_contours(image,output,threshold=0.5):
    
    masks = np.split(output,output.shape[0])
    colours = [(255,255,0),(0,255,255)]
    image_with_contour=np.uint8(np.transpose(np.array(image)*255,(1,2,0))).copy()
    
    for idx in range(output.shape[0]):
        binary_image = np.squeeze(np.uint8((masks[idx]>threshold) * 255))
        contours,_  = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image_with_contour, contours, -1, colours[idx] , 2) 
    return image_with_contour

def get_perimeter(mask,boundary=None):
    mask = np.squeeze(mask)
    mask = cv2.copyMakeBorder(mask, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=0)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    perim = sum(cv2.arcLength(contour, True) for contour in contours) 
    
    if boundary is not None:
        boundary = np.squeeze(boundary)
        boundary = np.max(boundary)-boundary
        boundary = cv2.copyMakeBorder(boundary, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
        contours, _ = cv2.findContours(boundary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        perim_boundary = sum(cv2.arcLength(contour, True) for contour in contours)
       
        mask_plus_boundary = mask | boundary
        contours, _ = cv2.findContours(mask_plus_boundary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        perim_neg = sum(cv2.arcLength(contour, True) for contour in contours) 

        perim = (perim + perim_neg - perim_boundary)/2  

    return perim


def anno_pred_comp(data_dir , data_json , model_path, csv_output,threshold):
    dataset = CocoSegmentationDataset(image_dir = data_dir, coco_json = data_json ,categories = [1,2,3])
    loader = DataLoader(dataset, batch_size=1)
    df = pd.DataFrame()
    model, device = load_model(model_path)
    for i, (inputs, targets) in enumerate(tqdm(loader)):
        with torch.no_grad():  
            masks = model(inputs)
            masks = torch.sigmoid(masks)
            masks =  np.array((masks > threshold)*255,dtype=np.uint8)
            targets = np.array((targets > threshold)*255,dtype=np.uint8)

            masks = masks.squeeze()
            targets = targets.squeeze()


            mask1,mask2,mask3 = masks[0], masks[1], masks[2]
            mask2 = mask2 * (mask1 // 255)
            mask3 = mask3 * (mask1 // 255)
            
            target1,target2,target3 = targets[0],targets[1],targets[2]
            target2 = target2 * (target1 // 255)
            mask3 = target3 * (target1 // 255)
            
            mask_area_1 = np.sum(mask1/255)
            mask_area_2 = np.sum(mask2/255)
            mask_area_3 = np.sum(mask3/255)
            
            mask_perim_1 = get_perimeter(mask1)
            mask_perim_2 = get_perimeter(mask2,mask1)
            mask_perim_3 = get_perimeter(mask3,mask1)
           
            target_area_1 = np.sum(target1/255)
            target_area_2 = np.sum(target2/255)
            target_area_3 = np.sum(target3/255)
            
            target_perim_1 = get_perimeter(target1)
            target_perim_2 = get_perimeter(target2, target1)
            target_perim_3 = get_perimeter(target3, target1)

            (height,width) = mask1.shape

            new_row = pd.DataFrame({'image_height':[height],
                                    'image_width':[width],
                                    'mask_area_1':[mask_area_1],
                                    'mask_area_2':[mask_area_2],
                                    'mask_area_3':[mask_area_3],
                                    'mask_perim_1':[mask_perim_1],
                                    'mask_perim_2':[mask_perim_2],
                                    'mask_perim_3':[mask_perim_3],
                                    'target_area_1':[target_area_1],
                                    'target_area_2':[target_area_2],
                                    'target_area_3':[target_area_3],
                                    'target_perim_1':[target_perim_1],
                                    'target_perim_2':[target_perim_2],
                                    'target_perim_3':[target_perim_3]
                                    
                                    })
            print(f'{target_area_3} and {mask_area_3} and {target_perim_3} and {mask_perim_3}')
            df = pd.concat([df,new_row],ignore_index=True)
        
    return df 


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='show model output from input image.')
    parser.add_argument('-i','--image_path', type=str, help='Path to image')
    parser.add_argument('-m','--model_path', type=str, help='Path to model')
    args = parser.parse_args()
    
    centerpad = CenterPad()

    image = load_image(args.image_path)
    
    model, device = load_model(args.model_path)

    output = run_inference(model, device, image, centerpad)

    img_with_contours = draw_contours(image,output)
    
    display(img_with_contours)




