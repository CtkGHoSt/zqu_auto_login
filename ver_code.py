from PIL import Image
import imagehash


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
    # image_file = ('./code/'+name for root, dirs, files in os.walk('./code') for name in files)
    # 基准图片hash
    # number_hash = [imagehash.phash(Image.open(i)) for i in image_file]
    number_hash = [
        imagehash.hex_to_hash('8aa8a880a08a808a'), # 0
        imagehash.hex_to_hash('e6b119c059c0cbdf'), # 1
        imagehash.hex_to_hash('abe11eb464ced8c2'), # …
        imagehash.hex_to_hash('ea9216da35c1dbc8'),
        imagehash.hex_to_hash('edf2c21e9c9012af'),
        imagehash.hex_to_hash('ab937ce83481d7c4'),
        imagehash.hex_to_hash('8bb8f9502197971e'),
        imagehash.hex_to_hash('fa4e3927ac8b8296'),
        imagehash.hex_to_hash('afb9e2c6a09183ce'),
        imagehash.hex_to_hash('de82adf034cbd00f'), 
    ]
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
