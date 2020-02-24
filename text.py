import json
import os
import re
import textwrap
from math import sqrt

import numpy
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont, BytesIO
import requests
from scipy.spatial.distance import cdist
'''
url='https://maoyan.com/board/2'
header={
    'Host':'maoyan.com',
    'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding':'gzip, deflate, br',
    'Referer':'https://maoyan.com/',
    'Connection':'keep-alive',
    'Cookie':'__mta=146758923.1580547970941.1581832832058.1581832833639.5; uuid_n_v=v1; uuid=1608872044D211EA8D96E79737803E57E4F552C762174B62A897BA99187B1D7D; _lxsdk_cuid=170000012d5c6-0fb85ea0e04a868-74276753-100200-170000012d60; _lxsdk=1608872044D211EA8D96E79737803E57E4F552C762174B62A897BA99187B1D7D; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1580553995,1580554164,1581325207,1581832831; mojo-uuid=f84b1fa02e139a824f965b54c3166f88; __mta=146758923.1580547970941.1580554019283.1581832832058.4; _csrf=5dcea22452504411bcb90e9621d30dcbc4af650fa3086482be856102067297d6; mojo-trace-id=3; mojo-session-id={"id":"bf33665d0c2cb3590ad59ce4625da3f3","time":1581832830022}; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1581832833; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=1704c95841b-ade-d09-697%7C%7C4',
    'Upgrade-Insecure-Requests':'1',
    'Cache-Control':'max-age=0',
}
'''
url='http://www.dianping.com/shop/93008034'
header={
    'Host':'www.dianping.com',
    'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding':'gzip, deflate',
    'Referer':'http://www.dianping.com/',
    'Connection':'keep-alive',
    'Cookie':'cy=179; cye=yichang; _lxsdk_cuid=1704371219462-04579bd07ed84e-75266753-100200-17043712196c8; _lxsdk=1704371219462-04579bd07ed84e-75266753-100200-17043712196c8; _hc.v=dedeccc9-71ae-75e2-8bd1-ab16e03f1bdb.1581679453; ua=dpuser_8652606750; ctu=8f9e70cae230d26a187a44e24f419ab500a3e05a703abba8be3912accb608c37; _dp.ac.v=c3c56ab7-f0ee-4e7e-bedb-1f825aaeac1b; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=17053c7a467-e6d-150-d60%7C%7C26',
    'Upgrade-Insecure-Requests':'1',
    'Cache-Control':'max-age=0',
}

def save(data,path):
    with open(path,'wb')as f:
        f.write(data)
        print('网页保存成功')

def get_request(url,header):
    response=requests.get(url,headers=header)
    save(response.content,'猫眼票房_1.html')
    file=open('猫眼票房_1.html','r').read()
    font_url=re.findall("url\(\'(.*?woff)",file)[0]
    download_path=os.path.basename(font_url)
    if not os.path.isfile(download_path):
        response=requests.get('http:'+font_url)
        save(response.content,download_path)
    return download_path

class FontDecrypter:
    def __init__(self, dynamic=False, mode='&#x'):
        """
        :param dynamic:是动态还是静态字体库
        :param mode:包括'&#x','u'和'raw'
        """
        self.dynamic = dynamic
        self.mode = mode
        if dynamic:
            self.glyphs_seq = None  # 字形序列
            self.template_font = None  # 笔画坐标
            self.current_font = None  # 当前笔画

    def show_glyphs(self, font1):
        """
        显示字体顺序，存储笔画坐标
        :param font_url:字体地址
        :return:
        """
        current_font = TTFont(font1)
        #current_font.saveXML('basefont.html')
        glyph_map = current_font.getBestCmap()  # 代码点-字形名称映射
        print(glyph_map)
        glyph_list = list(glyph_map)  # 留下代码点
        print(glyph_list)
        text = ''
        result = dict()
        for index, code in enumerate(glyph_list):
            print('index',index)
            print('code',code)
            glyph = current_font['glyf'][glyph_map[code]]  # 字形
            end_pts = glyph.endPtsOfContours  # 端点位置
            print('端点位置',end_pts)
            coordinates = glyph.coordinates.array  # 顶底坐标
            print ('顶点坐标', coordinates)
            print('顶点坐标list',list(coordinates))
            sliced_coordinates = self.slice_coordinates(list(coordinates), end_pts)
            print('sliced_coordinates',sliced_coordinates)
            number_of_contours = glyph.numberOfContours  # 轮廓数
            print('轮廓数',number_of_contours)
            result[number_of_contours] = result.get(number_of_contours, [])  # 将具有相同轮廓数的字形放在同一列表下
            result[number_of_contours].append({
                'coord': sliced_coordinates,
                'index': index
            })
            print('result',result)
            text += ' ' + chr(code)  # 将unicode码转成对应的字符
        with open('template_font.json', 'w')as f:  # 保存坐标信息
            if self.dynamic:
                json.dump(result, f)
            else:
                json.dump(glyph_list, f)
        print('原本text',text)
        text = textwrap.fill(text, width=40)
        print ('filltext', text)

        img = Image.new("RGB", (1920, 1050), '#fff')
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font1, 40)  # 设置图片字体
        draw.text((0, 0), text, font=font, fill="#000", spacing=10)
        img.save('font.png')
        img.show()

    @staticmethod
    def slice_coordinates(_coordinates, _end_pts):
        """
        将坐标按笔画拆分。由于不同字体文件中每段笔画的坐标数可能会不同，故需分段计算；若一并计算则后面的误差极大
        :param _coordinates: 坐标
        :param _end_pts: 端点
        :return: 切分后的坐标
        """
        end_pts = [0] + _end_pts  # 为方便遍历首位添0
        sliced_coordinates = [
            _coordinates[end_pts[index]:(end_pts[index + 1]) * 2]  # 坐标包含x和y，故需*2
            for index in range(len(end_pts) - 1)
        ]
        return sliced_coordinates

    @staticmethod
    def get_cosine_sim(_vector1, _vector2):
        """
        计算余弦相似度
        :param _vector1: 输入向量1
        :param _vector2: 输入向量2
        :return: 余弦
        """
        length = min(len(_vector1), len(_vector2))
        vector1 = numpy.array(_vector1[:length])
        vector2 = numpy.array(_vector2[:length])
        product = numpy.linalg.norm(vector1) * numpy.linalg.norm(vector2)
        sim = numpy.dot(vector1, vector2) / product
        return sim

    def load_glyphs_data(self, glyphs_seq):
        """
        加载字体数据
        :param glyphs_seq:人眼识别的字体序列
        :return:
        """
        self.glyphs_seq = glyphs_seq
        with open('template_font.json')as f:
            self.template_font = json.load(f)

    def sub_all(self, encoded_string, font_path=None):
        """
        替换所有加密字符
        :param encoded_string: 加密字符串
        :param font_path: 字体地址,可以是url或文件路径,若为静态加密则参数省略
        :return: 解密字符串
        """
        if font_path:
            if font_path.startswith('http'):
                content = requests.get(font_path).content
                bytes_io = BytesIO(content)
                self.current_font = TTFont(file=bytes_io)
            else:
                self.current_font = TTFont(file=font_path)
        if self.mode == '&#x':
            results = re.sub('&#x(.+?);', self._sub_one, encoded_string)
        elif self.mode == 'u':
            results = re.sub(r'\\u(.+?);', self._sub_one, encoded_string)
        elif self.mode == 'raw':
            results = re.sub('(.)', self._sub_one, encoded_string)
        else:
            raise Exception('Mode not implemented.')
        print(results)
        return results

    def _sub_one(self, match_result):
        """
        替换一个加密字符
        :param match_result: 正则匹配结果
        :return: 计算余弦相似度后最接近的字符
        """
        matched_one = match_result.group(1)
        if self.mode == '&#x' or self.mode == 'u':
            unicode = int(matched_one, 16)
        elif self.mode == 'raw':
            unicode = ord(matched_one)
        else:
            raise Exception('Mode not implemented.')
        if not self.dynamic:
            if unicode in self.template_font:
                predicted_index = self.template_font.index(unicode)
            else:  # 若不在字体库中，则直接返回
                return matched_one
        else:
            glyph_name = self.current_font.getBestCmap().get(unicode)  # 代码点-字形名称映射
            if not glyph_name:
                return matched_one
            current_glyph = self.current_font['glyf'][glyph_name]
            if not current_glyph:
                print('Code %s not found in this font file.' % unicode)
                return '🐓# 填补空白'
            number_of_contours = current_glyph.numberOfContours
            template_glyphs = self.template_font.get(str(number_of_contours))  # 选取具有相同笔画数的字形
            if len(template_glyphs) == 1:  # 只有一个字形相匹配，无需比较相似度
                predicted_index = template_glyphs[0]['index']
            else:
                end_pts = current_glyph.endPtsOfContours
                coordinates = current_glyph.coordinates.array
                sliced_coordinates1 = self.slice_coordinates(list(coordinates), end_pts)
                predicted_index = max_sim = -1  # 预测的索引、最大相似度
                for template_glyph in template_glyphs:
                    sim_sum = 0  # 所有笔画的相似度之和
                    sliced_coordinates2 = template_glyph['coord']
                    for vector1, vector2 in zip(sliced_coordinates1, sliced_coordinates2):
                        sim = self.get_cosine_sim(vector1, vector2)
                        sim_sum += sim
                    if sim_sum > max_sim:
                        max_sim = sim_sum
                        predicted_index = template_glyph['index']
        predicted_value = self.glyphs_seq[predicted_index]
        return predicted_value

basefont='ff79d6d0(3).woff'
#targetfont='ae75346a9f884b6d7179faf89ccf646f2280.woff'
text=FontDecrypter(dynamic=True)
temp=text.show_glyphs(basefont)
#seq='.5814602973'
#text.load_glyphs_data(seq)
#text.sub_all('&#xe56f;&#xe56f;&#xeca7;&#xe443;.&#xe443;</span></span>万',\
             #font_path=targetfont)


