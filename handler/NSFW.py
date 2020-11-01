# https://github.com/yahoo/open_nsfw
# https://github.com/devzwy/NSFW-Python
#!/usr/bin/env python
import sys
import tensorflow as tf
import io
from .model import OpenNsfwModel, InputType
from PIL import Image
import numpy as np
import skimage
import skimage.io
import os
sys.dont_write_bytecode = True

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_VISIBLE_DEVICES"]="1"
model_weights_path = 'model/open_nsfw-weights.npy'
model = OpenNsfwModel()
VGG_MEAN = [104, 117, 123]
img_width, img_height = 224, 224

# 将RGB按照BGR重新组装，然后对每一个RGB对应的值减去一定阈值
def prepare_image(image):
    H, W, _ = image.shape
    h, w = (img_width, img_height)

    h_off = max((H - h) // 2, 0)
    w_off = max((W - w) // 2, 0)
    image = image[h_off:h_off + h, w_off:w_off + w, :]

    image = image[:, :, :: -1]

    image = image.astype(np.float32, copy=False)
    image = image * 255.0
    image = image-np.array(VGG_MEAN, dtype=np.float32)

    image = np.expand_dims(image, axis=0)
    return image

# 使用TFLite文件检测
def getResultFromFilePathByTFLite(path):
    model_path = "model/nsfw.tflite"
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    # print(str(input_details))
    output_details = interpreter.get_output_details()
    # print(str(output_details))

    im = Image.open(path)
    # im = Image.open(r"./images/image1.png")
    if im.mode != "RGB":
        im = im.convert('RGB')
    imr = im.resize((256, 256), resample=Image.BILINEAR)
    fh_im = io.BytesIO()
    imr.save(fh_im, format='JPEG')
    fh_im.seek(0)

    image = (skimage.img_as_float(skimage.io.imread(fh_im, as_gray=False))
             .astype(np.float32))

    # 填装数据
    final = prepare_image(image)
    interpreter.set_tensor(input_details[0]['index'], final)

    # 调用模型
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    # 出来的结果去掉没用的维度
    result = np.squeeze(output_data)
    print('TFLite-->>result:{},path:{}'.format(result, path))
    print(
        "==========================================================================================================")
    print("")
    print("")
    return result

def getResultFromFilePathByPyModle(path):
    im = Image.open(path)

    if im.mode != "RGB":
        im = im.convert('RGB')

    # print("图片reSize：256*256")
    imr = im.resize((256, 256), resample=Image.BILINEAR)

    fh_im = io.BytesIO()
    imr.save(fh_im, format='JPEG')
    fh_im.seek(0)

    image = (skimage.img_as_float(skimage.io.imread(fh_im, as_gray=False))
             .astype(np.float32))

    final = prepare_image(image)

    tf.compat.v1.reset_default_graph()
    with tf.compat.v1.Session() as sess:
        input_type = InputType[InputType.TENSOR.name.upper()]
        model.build(weights_path=model_weights_path, input_type=input_type)
        sess.run(tf.compat.v1.global_variables_initializer())

        predictions = sess.run(model.predictions, feed_dict={model.input: final})
        # print("\tSFW score:\t{}\n\tNSFW score:\t{}".format(*predictions[0]))
        print(
            "==========================================================================================================")
        print('Python-->>result:{},path:{}'.format(predictions[0], path))
    return predictions[0]

def getResultListFromDir():
    list = os.listdir("../static/akr_R18")
    for i in range(0, len(list)):
        if (list[i] != ".DS_Store" and list[i] != ".localized"):
            getResultFromFilePathByPyModle(os.path.join("../static/akr_R18", list[i]))
            getResultFromFilePathByTFLite(os.path.join("../static/akr_R18", list[i]))

if __name__ == "__main__":
    getResultListFromDir()