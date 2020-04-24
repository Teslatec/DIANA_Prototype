import cv2
from PIL import Image, ImageDraw
import numpy as np
import json
from datetime import datetime
import time
import os
import pickle
import cv2
from imantics import Polygons, Mask
import configparser
 
class PurityIndex:   

    def __init__(self, config): 

        self.config = config        
        self.contrast = int(self.config.get('Settings', 'view_item'))
        self.S_Cof = int(self.config.get('Settings', 'S_Cof'))
        self.M_Cof = int(self.config.get('Settings', 'M_Cof'))
        self.H_Cof = int(self.config.get('Settings', 'H_Cof'))


    def get_index(self, image, mask):
        mask = mask.astype(np.uint8) * 255
        masked = cv2.bitwise_and(image, image, mask=mask)
        preview_image = self.get_prview_image(masked)
        averagePhoto = self.makeAveregePhoto(preview_image) 
        return self.updatePercentageTable(averagePhoto)

    def get_prview_image(self, cropped):
        
        img = cropped
        average_weight = self.get_average_wights(cropped)     
        contrast_img = cv2.addWeighted(
            img, 
            self.contrast / average_weight, np.zeros(img.shape, img.dtype), 0, 0)
        
        return contrast_img


    def get_average_wights(self, cropped):
        image = Image.fromarray(cropped)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        array = []
        array0 = []
        for x in range(width):
            for y in range(height):
                r = pix[x, y][0]
                g = pix[x, y][1]
                b = pix[x, y][2]

                sr = 0.2126 * r + 0.7152 * g + 0.0722 * b

                if (r == 0 and g == 255 and b == 0 ):
                    array0.append(sr)
                else:
                    array.append(sr)

        return  np.average(array)

    def apply_mask(self, image, mask, color):

        """Apply the given mask to the image.
        """
        for c in range(3):
            image[:, :, c] = np.where(mask != 0,
                                    color[c],
                                    image[:, :, c])
       
        return image
    

    def makeAveregePhoto(self, preview_image):
        # MAIN        
        image = Image.fromarray(preview_image) 

        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        newImage = Image.new('RGB', (width, height), color='white')

        for x in range(width):
            for y in range(height):                
                if (pix[x, y] != (0, 0, 0)):
                    newImage.putpixel((x, y), (255, 229, 204))

        open_cv_image = np.array(newImage) 
        open_cv_image = open_cv_image[:, :, ::-1].copy()                 

        
        mask_image_S = self.makeMaskImage('S', preview_image)
        open_cv_image = self.apply_mask(open_cv_image, mask_image_S, (217, 102, 255))
      
   
        mask_image_M = self.makeMaskImage('M', preview_image)
        open_cv_image = self.apply_mask(open_cv_image, mask_image_M, (255, 26, 26))

        mask_image_H = self.makeMaskImage('H', preview_image)   
        open_cv_image = self.apply_mask(open_cv_image, mask_image_H, (26, 26, 255))
     
        return open_cv_image       


    def makeMaskImage(self, step, preview_image):

        hsv = cv2.cvtColor(preview_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(
            hsv,
            (int(self.config.get(step, 'h_min')) / 2, int(self.config.get(step, 's_min')), int(self.config.get(step, 'v_min'))),
            (int(self.config.get(step, 'h_max')) / 2, int(self.config.get(step, 's_max')), int(self.config.get(step, 'v_max')))
            )   

        gray = cv2.GaussianBlur(mask, (3, 3), 0)
        edged = cv2.Canny(gray, 10, 250)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

        cnts, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)     

        # цикл по контурам
        for c in cnts:
            cv2.fillPoly(mask, [c], 255)

        return mask


    def updatePercentageTable(self, open_cv_image): 

        total, clear_pix, s_pix, m_pix, h_pix= 0,0,0,0,0
        colours, counts = np.unique(open_cv_image.reshape(-1,3), axis=0, return_counts=1)

        total = np.sum(counts) 

        for i in range(len(colours)):          
            if (list(colours[i]) == [255, 229, 204]):
                clear_pix = counts[i]
            elif (list(colours[i]) == [217, 102, 255]):
                s_pix = counts[i]
            elif (list(colours[i]) == [255, 26, 26]):
                m_pix = counts[i]
            elif (list(colours[i]) == [26, 26, 255]):
                h_pix = counts[i] 
            elif(list(colours[i]) == [255, 255, 255]):
                total = total - counts[i]
        
        x = s_pix * self.S_Cof  + m_pix * self.M_Cof + h_pix *  self.H_Cof
        total_ratio = (x / total)

        return total_ratio