import os
import glob
from os.path import expanduser
import shutil
import time

dl_path = 'retailo_allCat_backup2'
test_command0 = './darknet detect cfg/yolov3_SosAllCat.cfg retailo_allCat_backup2/'
home = expanduser('~')
input_main = 'input_main'
input_tst = 'D:\postgre training\shelf_object\inputs'
output_tst = 'D:\postgre training\shelf_object\outputs'
output_main = 'output_main'
def main():

    print("Hi!!")
    files = glob.glob(dl_path +'/*.weights')
    for file in files:
        t =0;


        if len(glob.glob('inputs/*.jpg'))==0:
            shutil.rmtree("inputs")
            shutil.copytree('input_main','inputs')


        l = len(glob.glob('inputs/*.jpg'))
        wt_file = file.split('/')[-1]
        test_command = test_command0 + str(wt_file)
        dir_name = file.split('.')[0].split('_')[-1]
        print(dir_name, test_command)
        os.system(test_command)
        #time.sleep(2)
        #shutil.rmtree('outputs')
        #shutil.copytree('inputs','outputs')
        #shutil.rmtree('inputs')
        #os.mkdir('inputs')

        while (len(glob.glob('inputs/*.jpg')) != 0):
            t = t + 0.000001
        print(t, "\n")
        if len(glob.glob('outputs/*.jpg')) == l:
            if dir_name in os.listdir('output_main'):
                shutil.rmtree('output_main/'+dir_name)    ## os.removedirs, os.rmdir delete only empty directories
            shutil.copytree('outputs','output_main/'+dir_name)
            shutil.rmtree('outputs')
            os.mkdir('outputs')     ## os.removedirs, os.rmdir delete only empty directories

if __name__ == '__main__':
    main()
