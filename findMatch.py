import cv2
import numpy as np
import math
import sys

from Graph import Graph, Node
from tracker import *


def buildGraph(stars: list, filename: str, dir: str = ''):
    if dir != '':
        filename = f'{dir}/{filename}'
    g = Graph()
    for i, _, _, _, _ in stars:
        if i == len(stars):
            break
        pos = (stars[i][1], stars[i][2])
        r = stars[i][3]
        b = stars[i][4]
        p = Node(i, pos, r, b)
        g.add_node(p)

    for i in g.nodes:
        for j in g.nodes:
            if i == j:
                continue
            g.add_edge(i, j)

    g.save_to_json(filename.split('.')[0])
    return g


def drawLine(g, l, filename, dir_src, dir_dest):
    print(filename)
    print(dir_src)
    try:
        img = cv2.imread(f'{dir_src}/detected_{filename}')
        img_copy = img.copy()  # Make a copy of the original image
    except:
        print(f"cant open file {filename}")
        return
    for i in l:
        pos1 = tuple(map(int, g.nodes[i[0]].getLocation()))
        pos2 = tuple(map(int, g.nodes[i[1]].getLocation()))
        cv2.line(img_copy, pos1, pos2, (0, 255, 0), 1)

    cv2.imwrite(f'{dir_dest}/{filename}', img_copy)


# p1b = g1.nodes[edge1.getP1()].getB() / g1.avgB
# p2b = g1.nodes[edge1.getP2()].getB() / g1.avgB
# p3b = g2.nodes[edge2.getP1()].getB() / g2.avgB
# p4b = g2.nodes[edge2.getP2()].getB() / g2.avgB
def is_similar_triangle(triangle1, triangle2,eps):
    if len(triangle1) != 3 or len(triangle2) != 3:
        return False

    # Calculate the lengths of the sides of both triangles
    sides1 = [((triangle1[i][0] - triangle1[j][0]) ** 2 + (triangle1[i][1] - triangle1[j][1]) ** 2) ** 0.5
              for i, j in [(0, 1), (1, 2), (2, 0)]]

    sides2 = [((triangle2[i][0] - triangle2[j][0]) ** 2 + (triangle2[i][1] - triangle2[j][1]) ** 2) ** 0.5
              for i, j in [(0, 1), (1, 2), (2, 0)]]

    # Check if the ratios of corresponding sides are equal
    ratios = [sides1[i] / sides2[i] for i in range(3)]

    if all(abs(ratios[i] - ratios[j])<eps for i, j in [(0, 1), (1, 2), (2, 0)]):
        return True
    else:
        return False


def match_stars(g1, g2, file1, file2, dir_detected, dir_matched, dir_log):
    # eps = 0.00009 / min(g1.get_min_dist(), g2.get_min_dist())
    print("min dist: ",g1.maxR/g1.avgR," ",g2.maxR/g1.avgR)
    name1 = file1.split('.')[0]
    name2 = file2.split('.')[0]
    toCsv = [[name1, name2]]
    eps = 0.09
    print(f'mistake epsilon: {eps}')
    def g1_sort_key(node):
        return -(node.getB()+node.getR()*(g1.maxR/g1.avgR*1.4))
    def g2_sort_key(node):
        return -(node.getB()+node.getR()*(g2.maxR/g2.avgR*1.4))
    g1_v = g1.get_all_nodes()
    g1_v.sort(key=g1_sort_key)
    g2_v = g2.get_all_nodes()
    g2_v.sort(key=g2_sort_key)
    l1 = [(g1_v[0].getId(),g1_v[1].getId())]
    l2 = [(g2_v[0].getId(),g2_v[1].getId())]
    toCsv.append([g1_v[0].getId(),g2_v[0].getId()])
    print(f'Star {g1_v[0].getId()} in {name1} EQUALS to Star {g2_v[0].getId()} in {name2}')
    toCsv.append([g1_v[1].getId(), g2_v[1].getId()])
    print(f'Star {g1_v[1].getId()} in {name1} EQUALS to Star {g2_v[1].getId()} in {name2}')
    if len(g1_v)>2 and len(g2_v)>2:
        triangle1=(g1_v[0].getLocation(),g1_v[1].getLocation(),g1_v[2].getLocation())
        triangle2=(g2_v[0].getLocation(),g2_v[1].getLocation(),g2_v[2].getLocation())
        flags = []
        for i1 in range(2,len(g1_v)):
            for i2 in range(2,len(g2_v)):
                triangle1 = (triangle1[0], triangle1[1], g1_v[i1].getLocation())
                triangle2 = (triangle2[0], triangle2[1], g2_v[i2].getLocation())
                if i2 not in flags and is_similar_triangle(triangle1, triangle2,eps):
                    l1.append((l1[-1][1], g1_v[i1].getId()))
                    l2.append((l2[-1][1], g2_v[i2].getId()))
                    toCsv.append([g1_v[i1].getId(), g2_v[i2].getId()])
                    print(f'Star {g1_v[i1].getId()} in {name1} EQUALS to Star {g2_v[i2].getId()} in {name2}')
                    flags.append(i2)
                    break
    l1.append((l1[-1][1], l1[0][0]))
    l2.append((l2[-1][1],l2[0][0]))
    drawLine(g1, l1, filename=file1, dir_src=dir_detected, dir_dest=dir_matched)
    drawLine(g2, l2, filename=file2, dir_src=dir_detected, dir_dest=dir_matched)
    makeCsv(l=toCsv,filename=f"matches_{name1}_{name2}",folder=dir_log)

def match_stars2(g1, g2, file1, file2, dir_detected, dir_matched,dir_log):
    # eps = 0.00009 / min(g1.get_min_dist(), g2.get_min_dist())
    eps = 0.009
    eps2 = 5
    print(eps)
    tups = []
    l1 = []
    l2 = []
    name1 = file1.split('.')[0]
    name2 = file2.split('.')[0]
    toCsv = [[name1, name2]]
    for edge1 in g1.get_all_edges():
        for edge2 in g2.get_all_edges():
            if abs(edge1.getDist() - edge2.getDist()) < eps:
                tups.append((edge1, edge2))
    for tup1, tup2 in zip(tups[::2], tups[1::2]):
        if tup1[0].m / tup2[0].m - tup1[1].m / tup2[1].m < eps2:
            print(
                f'Star {tup1[0].getP1()} and star {tup1[0].getP2()} in image1 EQUALS to Star {tup1[1].getP1()} and star {tup1[1].getP2()} in image2')
            l1.append((tup1[0].getP1(), tup1[0].getP2()))
            l2.append((tup1[1].getP1(), tup1[1].getP2()))
            toCsv.append([l1[-1], l2[-1]])

            print(
                f'Star {tup2[0].getP1()} and star {tup2[0].getP2()} in image1 EQUALS to Star {tup2[1].getP1()} and star {tup2[1].getP2()} in image2')
            l1.append((tup2[0].getP1(), tup2[0].getP2()))
            l2.append((tup2[1].getP1(), tup2[1].getP2()))
            toCsv.append([l1[-1],l2[-1]])

    drawLine(g1, l1, filename=file1, dir_src=dir_detected, dir_dest=dir_matched)
    drawLine(g2, l2, filename=file2, dir_src=dir_detected, dir_dest=dir_matched)
    makeCsv(l=toCsv, filename=f"matches2_{name1}_{name2}", folder=dir_log)


def run_all(img1, img2, dir_src):
    dir_images = dir_src
    dir_detected = 'detected_stars'
    dir_matched = 'matched_stars'
    dir_log = 'logs'
    dir_json = 'graphs'
    make_dirs([dir_images, dir_detected, dir_matched, dir_log, dir_json])
    dataset = os.listdir(dir_json)
    j1 = img1.split('.')[0] + '.json'
    j2 = img2.split('.')[0] + '.json'
    if j1 in dataset:
        g1 = Graph(file_name=j1, dir=dir_json)
    else:
        stars1 = detect_img(img1, dir_images, dir_detected, dir_log)
        g1 = buildGraph(stars1, filename=img1, dir=dir_json)
    if j2 in dataset:
        g2 = Graph(file_name=j2, dir=dir_json)
    else:
        stars2 = detect_img(img2, dir_images, dir_detected, dir_log)
        g2 = buildGraph(stars2, filename=img2, dir=dir_json)
    match_stars(g1, g2, file1=img1, file2=img2, dir_detected=dir_detected, dir_matched=dir_matched, dir_log=dir_log)


if __name__ == '__main__':
    dir_src = 'images'
    make_dirs([dir_src])
    dataset = os.listdir(dir_src)
    file1 = 'fr1.jpg'
    file2 = 'fr2.jpg'
    if len(sys.argv) > 1:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        run_all(file1, file2, dir_src)
    else:
        print("images:")
        for i in range(len(dataset)):
            print(f"{i + 1}: {dataset[i]}")
        input1 = input("input the number of the first image\n")
        if int(input1) - 1 in range(len(dataset)):
            input2 = input("input the number of the second image\n")
            if int(input2) - 1 in range(len(dataset)):
                run_all(img1=dataset[int(input1) - 1], img2=dataset[int(input2) - 1], dir_src=dir_src)
