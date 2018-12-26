from PIL import Image
import imagehash
import os


def validation_code_recognition(v_code_image):
    """
    http://enet.10000.gd.cn:10001/common/image.jsp
    验证码识别
    v_code 验证码图片文件流
    返回验证码字符串
    """
    y = 2
    w = 9
    h = 14
    # 切割参数
    cut_u = (
        (7, y, 7+w, y+h),
        (20, y, 20+w, y+h),
        (33, y, 33+w, y+h),
        (46, y, 46+w, y+h),
    )
    v_code = Image.open(v_code_image)
    # 基准图片
    image_file = ('./code/'+name for root, dirs, files in os.walk('./code') for name in files)
    # 基准图片hash
    number_hash = [imagehash.phash(Image.open(i)) for i in image_file]
    # 分割验证码图片计算hash
    v_code_hash = [ imagehash.phash(v_code.crop(c)) for c in cut_u ]
    # 计算最接近验证码的数字
    res = str()
    for i in v_code_hash:
        min = 9999
        min_point = 0
        for nm in number_hash:
            if i - nm < min:
                min = i - nm
                min_point = number_hash.index(nm)
        res += str(min_point)
    return res

if __name__ == '__main__':
    print(validation_code_recognition('test.jpg'))
