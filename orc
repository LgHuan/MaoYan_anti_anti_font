import pytesseract
from PIL import Image
img = Image.open('font.png')
#pytesseract.pytesseract.tesseract_cmd = 'usr/share/tesseract-ocr/4.00/tessdata'
s = pytesseract.image_to_string(img, lang='chi_sim')  #不加lang参数的话，默认进行英文识别
with open('font.txt','w')as f:
    f.write(s)

