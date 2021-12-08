import cv2
import os

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'static', 'uploads')


def cartoonify(filename, s):
    img_rgb = cv2.imread(os.path.join(UPLOADED_PHOTOS_DEST, filename))
    numBilateralFilters = 4
    result_file = 'result_' + filename
    result_dest = os.path.join(UPLOADED_PHOTOS_DEST, result_file)
    img_color = img_rgb
    for _ in range(numBilateralFilters):
        img_color = cv2.bilateralFilter(img_color, 15, 30, 20)
    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)
    if (s == "Black&White"):
        cv2.imwrite(result_dest, img_blur)
    img_edge = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 2)
    if (s == "Sketch"):
        cv2.imwrite(result_dest, img_edge)
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
    output = cv2.bitwise_and(img_color, img_edge)
    if (s == "Painting"):
        cv2.imwrite(result_dest, output)
    if (s == "WitchFiltered"):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        witch = cv2.imread('witch.png')
        original_witch_h, original_witch_w, witch_channels = witch.shape
        img_h, img_w, img_channels = img_rgb.shape
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        witch_gray = cv2.cvtColor(witch, cv2.COLOR_BGR2GRAY)

        ret, original_mask = cv2.threshold(witch_gray, 10, 255, cv2.THRESH_BINARY_INV)
        original_mask_inv = cv2.bitwise_not(original_mask)
        faces = face_cascade.detectMultiScale(img_gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_w = w
            face_h = h
            face_x1 = x
            face_x2 = face_x1 + face_w
            face_y1 = y
            face_y2 = face_y1 + face_h
            witch_width = int(1.5 * face_w)
            witch_height = int(witch_width * original_witch_h / original_witch_w)
            witch_x1 = face_x2 - int(face_w / 2) - int(witch_width / 2)
            witch_x2 = witch_x1 + witch_width
            witch_y1 = face_y1 - int(face_h * 1.25)
            witch_y2 = witch_y1 + witch_height
            if witch_x1 < 0:
                witch_x1 = 0
            if witch_y1 < 0:
                witch_y1 = 0
            if witch_x2 > img_w:
                witch_x2 = img_w
            if witch_y2 > img_h:
                witch_y2 = img_h
            witch_width = witch_x2 - witch_x1
            witch_height = witch_y2 - witch_y1
            witch = cv2.resize(witch, (witch_width, witch_height), interpolation=cv2.INTER_AREA)
            mask = cv2.resize(original_mask, (witch_width, witch_height), interpolation=cv2.INTER_AREA)
            mask_inv = cv2.resize(original_mask_inv, (witch_width, witch_height), interpolation=cv2.INTER_AREA)

            roi = img_rgb[witch_y1:witch_y2, witch_x1:witch_x2]
            roi_bg = cv2.bitwise_and(roi, roi, mask=mask)
            roi_fg = cv2.bitwise_and(witch, witch, mask=mask_inv)
            dst = cv2.add(roi_bg, roi_fg)

            img_rgb[witch_y1:witch_y2, witch_x1:witch_x2] = dst
        cv2.imwrite(result_dest, img_rgb)
