# import necessary packages
import numpy as np
import cv2
from AI_Engine.sample import modulo_general as modg
import os

# loading images
path = r"C:\Users\W8DE5P2\OneDrive-Deere&Co\OneDrive - Deere & Co\Desktop\Proveedores\CLIIENTES JOHN " \
       r"DEERE\Thyssenkrupp Campo Limpo\t15.pdf"
path = r"C:\Users\W8DE5P2\OneDrive-Deere&Co\OneDrive - Deere & Co\Desktop\Proveedores\CLIIENTES JOHN DEERE\Engine " \
       r"Power Components\t42.pdf"
path = r"C:\Users\W8DE5P2\OneDrive-Deere&Co\OneDrive - Deere & Co\Desktop\Proveedores\CLIIENTES JOHN DEERE\WorldClass " \
       r"Industries\t2.pdf"
path = r"C:\Users\W8DE5P2\OneDrive-Deere&Co\OneDrive - Deere & "\
       r"Co\Desktop\Proyectos\Pedidos-Tier-2\Proveedores\orders_history\ESP "\
       r"INTERNATIONAL_1223728_R116529\10-02-2022_09h-13m-1.jpg"

if os.path.splitext(path)[1].lower() == ".pdf":
    image1 = modg.pdf_to_img(os.path.join(path), False)[0]
else:
    image1 = cv2.imread(path)

# hardcoded assigning of output images for the 3 input images
output1_letter = image1.copy()
output1_word = image1.copy()
output1_line = image1.copy()
output1_par = image1.copy()
output1_margin = image1.copy()

gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

# clean the image using otsu method with the inversed binarized image
ret1, th1 = cv2.threshold(gray1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)


# processing letter by letter boxing
def process_letter(thresh, output):
    # assign the kernel size
    kernel = np.ones((2, 1), np.uint8)  # vertical
    # use closing morph operation then erode to narrow the image
    temp_img = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)
    # temp_img = cv2.erode(thresh,kernel,iterations=2)
    letter_img = cv2.erode(temp_img, kernel, iterations=1)

    # find contours
    (contours, _) = cv2.findContours(letter_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # loop in all the contour areas
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(output, (x - 1, y - 5), (x + w, y + h), (0, 255, 0), 1)

    return output


# processing letter by letter boxing
def process_word(thresh, output):
    # assign 2 rectangle kernel size 1 vertical and the other will be horizontal
    kernel = np.ones((2, 1), np.uint8)
    kernel2 = np.ones((1, 4), np.uint8)
    # use closing morph operation but fewer iterations than the letter then erode to narrow the image
    temp_img = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    # temp_img = cv2.erode(thresh,kernel,iterations=2)
    word_img = cv2.dilate(temp_img, kernel2, iterations=1)

    (contours, _) = cv2.findContours(word_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(output, (x - 1, y - 5), (x + w, y + h), (0, 255, 0), 1)

    return output


# processing line by line boxing
def process_line(thresh, output):
    # assign a rectangle kernel size	1 vertical and the other will be horizontal
    kernel = np.ones((1, 5), np.uint8)
    kernel2 = np.ones((2, 4), np.uint8)
    # use closing morph operation but fewer iterations than the letter then erode to narrow the image
    temp_img = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel2, iterations=2)
    # temp_img = cv2.erode(thresh,kernel,iterations=2)
    line_img = cv2.dilate(temp_img, kernel, iterations=5)

    (contours, _) = cv2.findContours(line_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(output, (x - 1, y - 5), (x + w, y + h), (0, 255, 0), 1)
    return output


# processing par by par boxing
def process_par(thresh, output):
    # assign a rectangle kernel size
    kernel = np.ones((5, 5), 'uint8')
    par_img = cv2.dilate(thresh, kernel, iterations=3)

    (contours, _) = cv2.findContours(par_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)

    return output


# processing margin with paragraph boxing
def process_margin(thresh, output):
    # assign a rectangle kernel size
    kernel = np.ones((20, 5), 'uint8')
    margin_img = cv2.dilate(thresh, kernel, iterations=5)

    (contours, _) = cv2.findContours(margin_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)

    return output


# processing and writing the output
output1_letter = process_letter(th1, output1_letter)
output1_word = process_word(th1, output1_word)
output1_line = process_line(th1, output1_line)
# special case for the 5th output because margin with paragraph is just the 4th output with margin
# cv2.imwrite("output/letter/output1_letter.jpg", output1_letter)
# cv2.imwrite("output/word/output1_word.jpg", output1_word)
# cv2.imwrite("output/line/output1_line.jpg", output1_line)
output1_par = process_par(th1, output1_par)
# cv2.imwrite("output/par/output1_par.jpg", output1_par)
output1_margin = process_margin(th1, output1_par)
# cv2.imwrite("output/margin/output1_margin.jpg", output1_par)

cv2.imshow("th1", cv2.resize(th1, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
cv2.imshow("output letter", cv2.resize(output1_letter, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
cv2.imshow("output word", cv2.resize(output1_word, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
cv2.imshow("output line", cv2.resize(output1_line, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
cv2.imshow("output par", cv2.resize(output1_par, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
cv2.imshow("output margin", cv2.resize(output1_margin, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))

cv2.waitKey(0)
