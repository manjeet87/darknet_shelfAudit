import time
import os
import psycopg2
import uuid
from psycopg2.extensions import AsIs
import re
import json
from bson.objectid import ObjectId
import urllib
import google.cloud.storage
from os.path import isfile, join
import os
import glob
import numpy as np
from shutil import copy
height = []

conn = psycopg2.connect("dbname=postgres user=postgres password=fortuner123 host='35.224.223.126'")
cur = conn.cursor()

"""**********************************************************************************"""
"""Function to Generated unSorted Shelf from detected boxes data"""
def generate_Shelf(brands_dict):
    brands_dict2 = {}
    for item in brands_dict:
        for box in brands_dict[item]:
            item_box = item + '_box'
            if item_box not in brands_dict2:
                brands_dict2[item_box] = []
            left = float(box.split(',')[0].split('=')[1])
            right = float(box.split(',')[2].split('=')[1])
            top = float(box.split(',')[1].split('=')[1])
            bottom = float(box.split(',')[3].split('=')[1])
            box_size = {'left': left, 'right': right, 'top': top, 'bottom': bottom}
            brands_dict2[item_box].append(box_size)

    sorted_shelf = {}
    for item in brands_dict2:
        levels = {}
        ilist = []
        shelf = {}
        w = abs(brands_dict2[item][0]['right'] - brands_dict2[item][0]['left'])
        h = abs(brands_dict2[item][0]['top'] - brands_dict2[item][0]['bottom'])

        for i in range(len(brands_dict2[item])):
            box = brands_dict2[item][i]
            ilist.append(box['bottom'])
        ilist = np.array(ilist)
        for l in range(len(ilist)):
            for l2 in range(l, len(ilist)):
                if abs(ilist[l] - ilist[l2]) < 0.4 * h:
                    ilist[l2] = round(ilist[l], 2)

        for i in range(len(ilist)):
            if str(ilist[i]) not in levels:
                # levels[ilist[i]] = [ilist[i],2]
                levels[str(ilist[i])] = [brands_dict2[item][i]]
            else:
                levels[str(ilist[i])].append(brands_dict2[item][i])

        sorted_shelf[item] = levels

    return sorted_shelf,w,h
"""**************************************************************************"""

"""**************************************************************************"""
"""Function to genrate final sorted shelf from unsorted shelf"""
def generate_SortedShelf(unsorted_shelf,w,h):
    sorted_shelf = unsorted_shelf.copy()
    shelf = []
    for itemSKU in unsorted_shelf:
        for sku in list(unsorted_shelf[itemSKU]):
            if float(sku) not in shelf:
                if len(shelf) == 0:
                    shelf.append(float(sku))
                else:
                    for level in shelf:
                        if abs(level-float(sku)) < 0.5*h:
                            pos = level
                            break
                        else: pos = None

                    if pos is None:
                            shelf.append(float(sku))
                    else:
                        sorted_shelf[itemSKU][str(pos)] = sorted_shelf[itemSKU][sku]
                        del sorted_shelf[itemSKU][sku]

    return sorted_shelf,shelf
"""*********************************************************************************"""

ctr = 0
while(True):
    sql1 = """ UPDATE image_data
                SET Status = %s
                WHERE Image_Db_Id = %s"""
    
    sql = """ UPDATE image_data_shelf
                SET found = %s,
                brand_sku_id = %s,
                sku_count = %s,
                sku_shelfspace = %s
                WHERE image_id = %s"""
    
   # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/manjeet_nsit2/darknet2/My Project 60776-1c396619b946.json'
   #  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'MyProject_60776-1c396619b946.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'MyProject_60776-1c396619b946.json'
    storage_client = google.cloud.storage.Client()
    bucket_name = 'shelf_images'
    bucket = storage_client.get_bucket(bucket_name)
    # img_input_list = glob.glob('/home/manjeet_nsit2/darknet2/inputs/*.jpeg')
    # img_input_list2 = glob.glob('/home/manjeet_nsit2/darknet2/inputs/*.jpg')

    img_input_list = glob.glob('inputs/*.jpg')
    img_input_list2 = glob.glob('inputs/*.jpeg')
    img_input_list = glob.glob('inputs/*.jpeg')
    img_input_list2 = glob.glob('inputs/*.jpg')
    inputlst = len(img_input_list) + len(img_input_list2)
    # output_files = glob.glob('/home/manjeet_nsit2/darknet2/output/*.*')
    # output_files = glob.glob('output/*.*')
    output_files = glob.glob('outputs/*.*')

    if inputlst == 0 and len(output_files)<=1:
        if ctr<=1: print("Reading Database..")
        ctr +=1
        cur.execute(""" SELECT * FROM image_data_shelf where status = 'UNPROCESSED' """)
        records = cur.fetchone()
        if records != None:
            print(records)
            image_id = records[0]
            print(image_id)
            img_url = records[2]
            print("**",img_url)
            #cur.execute(sql1, ('UnderProcess', image_id))
            #conn.commit()
            #file_name = '/home/prizmatics91/testing_darknet/darknet/inputs/{}'.format(records[13])
            file_name = 'inputs/{}.jpg'.format(records[0])
            #file_name = 'inputs/ID-{0}_{1}_{2}_{3}_unprocess.jpg'.format(records[8],records[10], records[9],records[3])
            print(file_name)
            urllib.request.urlretrieve(img_url, file_name)
    
    if len(output_files):
        ctr = 0
        output_path = 'outputs/'
        output_path2 = 'output/'
        textfile = ''
        for file in os.listdir(output_path):
            print(file)
            file_path = os.path.join(output_path, file)
            LevelOfIdentification = ''
            if '.jpg' in file:
                print('Image file found..{}'.format(file))
                blob = bucket.blob('unprocessed/'+ os.path.basename(file_path))
                blob.upload_from_filename(file_path)
                image_new_url = blob.public_url
                image_id2 = file.split('_')[0]
                flag = 'Found'
                textfileName = '{}_textData.txt'.format(image_id2)
                textfilePath = os.path.join(output_path,textfileName)

                if textfileName in os.listdir(output_path):  #Looking for corresponding text_file
                   # with open('/home/prizmatics91/testing_darknet/darknet/output/text_1.txt', 'r') as textfile:
                    with open(textfilePath, 'r') as textfile:
                        textfileread = textfile.read()
                        if len(textfileread) == 0:
                            flag = 'NotFound'

                            cur.execute(""" INSERT INTO image_shelf_processed(image_id,found)
                                                                        VALUES(%s,%s)""",
                                        (image_id2, "No"))
                            conn.commit()

                        else:
                            brands_list = []
                            brands_dict = {}
                            comp = re.compile(r'([A-Za-z_0-9]*:\s[0-9]*%)')
                            lines= textfileread.split('\n')
                            for i in range(len(lines)):
                                brand = comp.search(lines[i])
                                if brand is not None:
                                    flag = 'Found'
                                    brandVal = brand.group().split(':')[0]

                                    if brandVal not in brands_list:
                                        brands_list.append(brandVal)
                                    print(brands_list)
                                    if brandVal not in brands_dict:
                                        brands_dict[brandVal] = []
                                        brands_dict[brandVal].append(lines[i+1])
                                    else:
                                        brands_dict[brandVal].append(lines[i + 1])

                                LevelOfIdentification = ', '.join(brands_list)

                            unsorted_shelf,w,h = generate_Shelf(brands_dict)

                            sorted_shelf, shelf_level = generate_SortedShelf(unsorted_shelf,w,h)

                                    #vert_diff = item[i]['top'] - item[i+1]['top']
                                    #if vert_diff > 0.5 * h
                            final_shelf = {}
                            shelf_level.sort(reverse= True)
                            for level in shelf_level:
                                final_shelf[str(level)] = {}
                                for item in sorted_shelf:

                                    for pos in sorted_shelf[item]:
                                        if str(level) == pos:
                                            if item not in final_shelf[str(level)]:
                                                final_shelf[str(level)][item] = {'box':[],'count':0}

                                            final_shelf[str(level)][item]['box'] = sorted_shelf[item][pos]
                                            final_shelf[str(level)][item]['count'] = len(sorted_shelf[item][pos])


                            brand_table = []
                            sku_table = {}
                            shelf_space_table = {}
                            found = 'No'
                            for shelf in final_shelf:
                                level = str(shelf_level.index(float(shelf)))
                                for sku in final_shelf[shelf]:
                                    sku = sku.replace('_box','')
                                    found = 'Yes'
                                    if sku not in brand_table:
                                        brand_table.append(sku)
                                    if level not in sku_table:
                                        sku_table[level] = {}
                                    if level not in shelf_space_table:
                                        shelf_space_table[level] = {}

                                    sku_table[level][sku] = final_shelf[shelf][sku+'_box']['count']
                                    width = abs(final_shelf[shelf][sku+'_box']['box'][0]['right'] - final_shelf[shelf][sku+'_box']['box'][0]['left'])
                                    shelf_space_table[level][sku] = round(100*width* final_shelf[shelf][sku+'_box']['count'],1)



                            data_skutable = json.dumps(sku_table)
                            data_brand = json.dumps(brand_table)
                            data_shelfspace = json.dumps(shelf_space_table)

                            cur.execute(""" INSERT INTO image_shelf_processed(image_id,found,brand_ids,brand_sku_id,sku_count,sku_shelfspace)
                                            VALUES(%s,%s,%s,%s,%s,%s)""",(image_id2,"Yes","b",data_brand,data_skutable,data_shelfspace))
                            conn.commit()

                        cur.execute(""" UPDATE image_data_shelf SET status = 'PROCESSED' WHERE image_id = %s""",
                                    (image_id2,))
                        conn.commit()

                    try:
                        os.remove(file_path)
                        os.remove(textfilePath)
                    except:
                        break            
                                
                                    
