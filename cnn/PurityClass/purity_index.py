import cv2
from PIL import Image, ImageDraw
import numpy as np
import json

class PurityIndex:

    SAVE_FILE_PATH = './save/total.txt'

    TOTAL_AVERAGE_IMAGE = './save/average_photo.png'

    MASK_PATH = './save/mask.png'

    def __init__(self, tooth_dir):
        self.tooth_dir = tooth_dir
        self.contrast = 200
        self.S_Cof = 1
        self.M_Cof = 1
        self.H_Cof = 1


    def get_tooth_dir(self):
        return self.tooth_dir


    def get_index(self):
        preview_image = self.get_prview_image()
        self.makeAveregePhoto(preview_image)

        return self.updatePersentTable()


    def get_prview_image(self):
        img = cv2.imread(self.tooth_dir)
        average_weight = self.get_average_wights()
        contrast_img = cv2.addWeighted(img, self.contrast / average_weight, np.zeros(img.shape, img.dtype), 0, 0)

        return contrast_img


    def get_average_wights(self):
        image = Image.open(self.tooth_dir)
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

    def makeAveregePhoto(self, preview_image):
        # MAIN
        image = Image.open(self.tooth_dir)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        newImage = Image.new('RGB', (width, height), color='white')

        for x in range(width):
            for y in range(height):
                if (pix[x, y] != (0, 255, 0, 0)):
                    newImage.putpixel((x, y), (255, 229, 204))


        mask_image_S = self.makeMaskImage('S', preview_image)

        image = Image.fromarray(mask_image_S)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        for x in range(width):
            for y in range(height):
                if (pix[x, y] != (0, 0, 0)):
                    newImage.putpixel((x, y), (217, 102, 255))

        mask_image_M = self.makeMaskImage('M', preview_image)

        image = Image.fromarray(mask_image_M)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        for x in range(width):
            for y in range(height):
                if (pix[x, y] != (0, 0, 0)):
                    newImage.putpixel((x, y), (26, 26, 255))

        mask_image_H = self.makeMaskImage('H', preview_image)

        image = Image.fromarray(mask_image_H)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        for x in range(width):
            for y in range(height):
                if (pix[x, y] != (0, 0, 0)):
                    newImage.putpixel((x, y), (255, 26, 26))

        newImage.save(self.TOTAL_AVERAGE_IMAGE)


    def makeMaskImage(self, step, preview_image):

        dataStep = self.getSavedData(step)

        hsv = cv2.cvtColor(preview_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (dataStep[step]['h_min'] / 2, dataStep[step]['s_min'], dataStep[step]['v_min']),
                           (dataStep[step]['h_max'] / 2, dataStep[step]['s_max'], dataStep[step]['v_max']))

        cv2.imwrite(self.MASK_PATH, mask)
        image = cv2.imread(self.MASK_PATH)
        gray = cv2.GaussianBlur(mask, (3, 3), 0)
        edged = cv2.Canny(gray, 10, 250)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

        cnts, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # цикл по контурам
        for c in cnts:
            cv2.fillPoly(image, [c], (255, 255, 255))

        return image


    def getSavedData(self, step):
        with open(self.SAVE_FILE_PATH) as json_file:
            data = json.load(json_file)
            self.contrast = data['view_item']
            self.S_Cof = data['S_Cof']
            self.M_Cof = data['M_Cof']
            self.H_Cof = data['H_Cof']

            return data

    def updatePersentTable(self):
        image = Image.open(self.TOTAL_AVERAGE_IMAGE)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        total = 0
        clear_pix = 0
        s_pix = 0
        m_pix = 0
        h_pix = 0

        for x in range(width):
            for y in range(height):
                if (pix[x, y] != (255, 255, 255)):
                    total = total + 1

                if (pix[x, y] == (255, 229, 204)):
                    clear_pix = clear_pix + 1
                elif (pix[x, y] == (217, 102, 255)):
                    s_pix = s_pix + 1
                elif (pix[x, y] == (26, 26, 255)):
                    m_pix = m_pix + 1
                elif (pix[x, y] == (255, 26, 26)):
                    h_pix = h_pix + 1

        total_persent = (1 - (total -  s_pix * self.S_Cof  - m_pix * self.M_Cof - h_pix *  self.H_Cof)/ total) * 100

        return round(total_persent, 1)

