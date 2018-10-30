import os
import glob
import re
import cv2

global brand_dict
brand_dict = {'MaggiMG':0,'MaggiMR':1,'Heinz':2,'MaggiSR':3,'MaggiSG':4}

def get_coordinates(box_data):


    left = float(box_data.split(',')[0].split('=')[1])
    right = float(box_data.split(',')[2].split('=')[1])
    top = float(box_data.split(',')[1].split('=')[1])
    bottom = float(box_data.split(',')[3].split('=')[1])
    box_size = {'left': left, 'right': right, 'top': top, 'bottom': bottom}
    return box_size


def draw_image(im, top, left, right, bottom,brand):
    global brand_dict
    c = brand_dict[brand]
    col = tuple((0,0,0))
    if c ==0:
        col = tuple([0,255,0])
    if c ==1:
        col = tuple([0,0,255])
    if c ==2:
        col = tuple([255,0,0])
    if c ==3:
        col = tuple([255,255,0])
    if c ==4:
        col = tuple([255,255,255])

    cv2.rectangle(im,(top,left),(right,bottom),col,4)
    return im

out_main_dir = r'D:\DarknetVM_InstanceShelf\darknet2\output_main'
input_main = r'D:\DarknetVM_InstanceShelf\darknet2\input_main'
model_ver_list = os.listdir(out_main_dir)
model_ver_list = sorted([int(x) for x in model_ver_list])

for input_img in os.listdir(input_main):
    txtfile = input_img.replace('.jpg','_textData.txt')

    im = cv2.imread('download.jpg')
    cv2.imshow('window', im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    imgfile = input_main +'\\' + input_img
    im = cv2.imread(imgfile)
    print(im.shape)
    w = im.shape[1]
    h = im.shape[0]

    for model_ver in model_ver_list:
        im = cv2.imread(imgfile)
        dir_path = out_main_dir + '\\'+str(model_ver)

        txtfile_path = dir_path + '\\' + txtfile
        print(txtfile_path)

        with open(txtfile_path,'r') as f:
            lines = f.readlines()

        brands_list = []
        brands_dict = {}
        comp = re.compile(r'([A-Za-z_0-9]*:\s[0-9]*%)')

        for i in range(len(lines)):
            brand = comp.search(lines[i])
            if brand is not None:
                flag = 'Found'
                brandVal = brand.group().split(':')[0]
                brand = brandVal
                box_data = lines[i + 1]
                box_coord = get_coordinates(box_data)
                x1 = int(box_coord['left'] * w)
                y1 = int(box_coord['bottom'] * h)
                x2 = int(box_coord['right'] * w)
                y2 = int(box_coord['top'] * h)

                # print(x1,y1,x2,y2)
                im = draw_image(im, x1,y1,x2,y2,brand)

        # cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
        # cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        #im.resize(300,400)
        im3 = cv2.resize(im, (0, 0), fx=0.4, fy=0.4)
        cv2.imshow(str(model_ver),im3)

        cv2.waitKey(0)
        cv2.destroyAllWindows()