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

        return self.count_tooth_purity_pixel(averagePhoto)

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

                # Delet green and black from index
                if (r == 0 and g == 0 and b == 0 ):
                    array0.append(sr)
                elif (r == 0 and g == 255 and b == 0 ):
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


    def count_tooth_purity_pixel(self, open_cv_image): 

        tooth_purty_pixel =  {
                    'total': 0,
                    's': 0,
                    'm': 0,
                    'h': 0, 
                    'image': open_cv_image
                } 
                    
        colours, counts = np.unique(open_cv_image.reshape(-1,3), axis=0, return_counts=1)  

        for i in range(len(colours)):           
            if (list(colours[i]) == [217, 102, 255]):
                tooth_purty_pixel['s'] = counts[i]

            elif (list(colours[i]) == [255, 26, 26]):
                tooth_purty_pixel['m'] = counts[i]

            elif (list(colours[i]) == [26, 26, 255]):
                tooth_purty_pixel['h'] = counts[i]
                
            elif(list(colours[i]) == [255, 255, 255]):
                tooth_purty_pixel['total'] =  np.sum(counts)  - counts[i]


        return tooth_purty_pixel  




    def get_purity_index(self, tooth_purty_pixel):
        if tooth_purty_pixel['total'] != 0:
            day_percentage = tooth_purty_pixel['s'] / tooth_purty_pixel['total']
            week_percentage = tooth_purty_pixel['m'] / tooth_purty_pixel['total']
            month_percentage = tooth_purty_pixel['h'] / tooth_purty_pixel['total']
        else:
            # Whatever
            day_percentage = 0
            week_percentage = 0
            month_percentage = 0
            

        day_index = self.get_day_plaque_index(day_percentage)
        week_index = self.get_week_plaque_index(week_percentage)
        month_index = self.get_month_plaque_index(month_percentage)

        matrix = [month_index, week_index, day_index]
        total = day_percentage + month_percentage + week_percentage

        return {
            'color': self.get_total_color(matrix, total),
            'matrix' : matrix,
            'day': day_percentage,
            'week': week_percentage,
            'month': month_percentage,             
        }    

    
    def get_total_color(self, total_matrix, total):

        green = [
                [3,3,3],
            ]

        red = [
                [1,1,1],
                [1,2,3],
                [1,3,2],
                [1,2,1],
                [1,1,2],
                [1,2,2],
                [1,1,3],
                [1,3,1],
                [1,3,3],
                [2,1,1],
                [2,1,2],
                [2,2,2],
                [3,1,1],
                [3,1,2],
                [2,1,3],
                [2,2,1],
                [2,3,1],
                [3,3,1],
                [3,1,3],
                [3,2,1],
            ]

        if total_matrix in green:
            risk_factor_by_matrix = 0
        elif total_matrix in red:
            risk_factor_by_matrix = 2
        else:
            risk_factor_by_matrix = 1

        if total <= 0.10:
            risk_factor_by_total = 0
        elif total <= 0.30:
            risk_factor_by_total = 1
        else:
            risk_factor_by_total = 2

        risk_factor = max(risk_factor_by_matrix, risk_factor_by_total)
        return ['green', 'yellow', 'red'][risk_factor]
        

    def get_day_plaque_index(self, percent):

        percent = round(percent*100)
        if percent <= 10:
            return 3
        elif percent <= 45:
            return 2
        else:
            return 1     


    def get_week_plaque_index(self, percent):

        percent = round(percent*100)
        if percent <= 5:
            return 3
        elif percent <= 20:
            return 2
        else:
            return 1       


    def get_month_plaque_index(self, percent):

        percent = round(percent*100)
        if (percent <= 0):
            return 3
        elif percent <= 5:
            return 2
        else:
            return 1   
