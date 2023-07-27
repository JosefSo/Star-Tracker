import csv
import os
import cv2
import numpy as np
import pandas as pd


def make_dirs(dirs=[]):
    path = os.path.join(os.getcwd())
    for dir in dirs:
        try:
            os.mkdir(f'{path}/{dir}')
        except:
            pass


def makeCsv(l, folder='logs', filename="no_name"):
    csvname = filename.split('.')[0] + '.csv'
    path = os.path.join(os.getcwd(), folder)
    try:
        os.mkdir(path)
    except:
        pass
    f = open(f'{folder}/{csvname}', 'w', newline='')
    writer = csv.writer(f)
    writer.writerows(l)
    f.close()
    print(f'{csvname} saved.')

def detect_img(filename, dir_src, dir_dest, dir_log):
    try:
        img = cv2.imread(f'{dir_src}\{filename}')
        img_copy = img.copy()  # Make a copy of the original image
    except:
        print(f"cant open file {filename}")
        return
    cv2.namedWindow(f'{filename} Stars', cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f'{filename} Stars', 1024, 768)
    cv2.imshow(f'{filename} Stars', img_copy)
    cv2.waitKey(1)
    cv2.destroyAllWindows()

    print(f"start detecting {filename}")
    stars = [['id', 'x', 'y', 'r', 'b']]
    gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    avg = np.mean(gray)
    _, thresh = cv2.threshold(blur, avg * 1.5, 255, cv2.THRESH_BINARY)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
    print(f"found {num_labels} labels")
    percents = 10
    id = 1
    for i in range(1, num_labels):
        if percents < (100 * i) / num_labels:
            print(f'{percents}% detected')
            percents += 10
        mask = (labels == i).astype(np.uint8)
        x, y = centroids[i]
        min_radius = 2  # or any other minimum value you choose
        r = int((stats[i, cv2.CC_STAT_WIDTH] + stats[i, cv2.CC_STAT_HEIGHT]) / 4)
        if r >= min_radius:
            b = cv2.mean(gray, cv2.UMat(mask))[0]
            stars.append((id, x, y, r, b))
            cv2.circle(img_copy, (int(x), int(y)), r + 5, (0, 255, 0), 2)
            cv2.putText(img_copy, f"{id}", (int(x) - 20, int(y) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            id += 1

    print(f'100% detected\n{len(stars) - 1} stars detected')
    makeCsv(stars, folder=dir_log, filename=filename)
    cv2.imwrite(f'{dir_dest}\detected_{filename}', img_copy)
    print(f'detected_{filename} saved.')
    cv2.namedWindow(f'{filename} Detected Stars', cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f'{filename} Detected Stars', 1024, 768)
    cv2.imshow(f'{filename} Detected Stars', img_copy)
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    return stars[1:]


if __name__ == '__main__':
    dir_src = 'images'
    dir_dest = 'detected_stars'
    dir_log = 'logs'
    make_dirs([dir_src, dir_dest, dir_log])
    dataset = os.listdir(dir_src)
    print("images:")
    for i in range(len(dataset)):
        print(f"{i + 1}: {dataset[i]}")
    str_in = input("input the number of the image for detecting, to detect all input <all>\n")
    if str_in == 'all':
        for i in dataset:
            detect_img(filename=i, dir_src=dir_src, dir_dest=dir_dest, dir_log=dir_log)
    elif int(str_in) - 1 in range(len(dataset)):
        detect_img(filename=dataset[int(str_in) - 1], dir_src=dir_src, dir_dest=dir_dest, dir_log=dir_log)

