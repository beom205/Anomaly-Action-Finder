import numpy as np
import keras
import cv2
from datetime import datetime, timedelta
from i3d_inception import Inception_Inflated3d
import tensorflow as tf
import time
import requests
class twostream_FinalModel():
    def __init__(self, rgb_model_path, opt_model_path = None):
        self.before_IMG_WIDTH = 256
        self.before_IMG_HEIGHT = 256

        self.IMG_WIDTH = 224
        self.IMG_HEIGHT = 224

        self.img_list = None
        self.classes = ["Assault", "Normal", "Swoon"]
        self.frame_rate = 0
        self.fontScale = 0.5
        self.fontPosition_X = 0
        self.fontPosition_Y = 30
        self.nbFrame = 16
        
        self.sess = tf.Session()
        self.graph = tf.get_default_graph()


        # optical Variable
        self.prevs = None
        self.optical_img_list = None

        self.rgb_model_path = rgb_model_path
        self.opt_model_path = opt_model_path

        # prediction value
        self.prediction_length = 10
        self.predict_value_list = np.zeros((self.prediction_length, len(self.classes)))
        self.before_action = 1
        self.threshold = 0.7

        self.save_image_list = []
        
        self.video_frame_rate = 30
        self.save_video_length = 5
        self.anormaly_action = [0, 2]
        self.save_image_flag = False

        self.alarm_flag = False
        self.model = self.load_model()
        

    def define_model(self, model_type="RGB"):
        if model_type == "RGB":
            channel = 3
            model_name = "_rgb"
        elif model_type == "OPT":
            channel = 2
            model_name = "_opt"
        a = keras.layers.Input(shape=(16, 224, 224, channel))
        i3d = Inception_Inflated3d(include_top=False,
                        weights=None,
                        input_tensor=a,
                        input_shape=None,
                        dropout_prob=0.5,
                        endpoint_logit=True,
                        classes=3,
                        model_name = model_name)
        for layer in i3d.layers:
            layer.name = layer.name + model_name
        model = keras.models.Sequential()
        model.add(i3d)
        model.add(keras.layers.Flatten())
        model.add(keras.layers.Dropout(0.5))
        model.add(keras.layers.Dense(3))

        return model

    def load_model(self):
        keras.backend.set_session(self.sess)

        rgb_model = self.define_model("RGB")
        rgb_model.load_weights(self.rgb_model_path)

        if self.opt_model_path is not None:
            opt_model = self.define_model("OPT")
            opt_model.load_weights(self.opt_model_path)
        else:
            print("RGB_Model return")
            return rgb_model
        logits = keras.layers.Add()([rgb_model.output, opt_model.output])

        model = keras.models.Model(inputs=[rgb_model.input, opt_model.input], outputs=logits)
        return model

    def predict(self, input_img):
        keras.backend.set_session(self.sess)
        action = ""
        action_idx = -1
        alarm = False
        presentTime = datetime.now() 
        frame_x = cv2.resize(input_img.copy(), (self.before_IMG_WIDTH, self.before_IMG_HEIGHT))
        frame_x = cv2.cvtColor(frame_x.copy(), cv2.COLOR_BGR2RGB)
        frame_x = self.crop_center(frame_x)
        rgb_x = (frame_x - frame_x.mean()) / frame_x.std()

        ## RGB add image into list 
        if self.img_list is None:
            self.img_list = np.expand_dims(rgb_x, axis=0)
        else:
            if self.img_list.shape[0] != self.nbFrame:
                self.img_list = np.vstack((self.img_list, np.expand_dims(rgb_x, axis=0)))
            else:
                self.img_list = np.vstack((self.img_list[1:], np.expand_dims(rgb_x, axis=0)))

        ## optical 모델을 적용할 경우
        if self.opt_model_path is not None:
        ## Optical add image into list  
            if self.prevs is None:
                self.prevs = cv2.cvtColor(frame_x, cv2.COLOR_RGB2GRAY)
            else:   #이전 프레임이 있다면
                present = cv2.cvtColor(frame_x, cv2.COLOR_RGB2GRAY)
                start_time = time.time()
                flow = self.compute_TVL1(self.prevs, present)
                print("optcial calc", time.time() - start_time)
                self.prevs = present
                if self.optical_img_list is None:
                    self.optical_img_list = np.expand_dims(flow, axis=0)
                else:
                    if self.optical_img_list.shape[0] != self.nbFrame:
                        self.optical_img_list = np.vstack((self.optical_img_list, np.expand_dims(flow, axis=0)))
                    else:
                        self.optical_img_list = np.vstack((self.optical_img_list[1:], np.expand_dims(flow, axis=0)))

        ## RGB만 사용하는 경우
        if self.opt_model_path is None:
            if self.img_list is not None:
                if self.img_list.shape[0] == self.nbFrame:
                    # 딥러닝 예측 부분
                    with self.graph.as_default():
                        pred_value = self.softmax(self.model.predict(np.expand_dims(self.img_list, axis=0)))
                        self.predict_value_list = np.concatenate((self.predict_value_list[1:], pred_value), axis = 0)
                        sum_logits = np.sum(pred_value, axis = 0)
                        # print("sum_logits : ", sum_logits)
                        action_idx = np.argmax(sum_logits)
                        action_idx = self.check_threshold(sum_logits, action_idx)
                        action = self.classes[action_idx]

                    cv2.putText(input_img, str(presentTime)[:-7] +"   "+ action+ "   "+ str(sum_logits[action_idx]), (self.fontPosition_X, self.fontPosition_Y), cv2.FONT_HERSHEY_SIMPLEX,
                             self.fontScale, (0, 0, 255), 2)
        ## optical 도 같이 사용하는 경우 
        else:
            if self.optical_img_list is not None:
                if self.optical_img_list.shape[0] == self.nbFrame:
                    # 딥러닝 예측 부분
                    with self.graph.as_default():
                        start_time = time.time()
                        tmp_pred = self.model.predict([np.expand_dims(self.img_list, axis=0), np.expand_dims(self.optical_img_list, axis=0)])
                        pred_value = self.softmax(tmp_pred)
                        self.predict_value_list = np.concatenate((self.predict_value_list[1:], pred_value), axis = 0)
                        sum_logits = np.sum(pred_value, axis = 0)
                        # print("deep optcial calc", time.time() - start_time)
                        # print("sum_logits : ", sum_logits)
                        action_idx = np.argmax(sum_logits)
                        action_idx = self.check_threshold(sum_logits, action_idx)
                        action = self.classes[action_idx]

                    cv2.putText(input_img, str(presentTime)[:-7] +"   "+ action + "   "+ str(sum_logits[action_idx]), (self.fontPosition_X, self.fontPosition_Y), cv2.FONT_HERSHEY_SIMPLEX,
                             self.fontScale, (0, 0, 255), 2)


        if action_idx in self.anormaly_action:
            self.save_image_flag = True
            self.alarm_flag = True

        if self.alarm_flag is True and len(self.save_image_list) == 0:
           alarm = True
           self.alarm_flag = False
           
        if self.save_image_flag is True:
            self.save_image_list.append(input_img)

        if len(self.save_image_list) == (self.video_frame_rate * self.save_video_length):
            self.save_anormaly_video()
            print("save anormaly_video")
            self.save_image_flag = False
            self.save_image_list = []
        # if (self.frame_rate % read_fps) == 0:
        #     self.frame_rate = 0
        #     presentTime += timedelta(seconds = 1)
        self.frame_rate += 1

        return input_img, alarm, action
    
    def check_threshold(self, sum_logits, action_idx):
        # print("check_threshold ")
        if sum_logits[action_idx] >= self.threshold:
            self.before_action = action_idx
        else:
            action_idx = self.before_action
        return action_idx

    # source : https://github.com/OanaIgnat/i3d_keras/blob/e62e834f0d0ad90d4de1b067ac6dc55a33d03969/src/preprocess.py#L46
    def crop_center(self, img):
        y, x, c = img.shape

        startx = x // 2 - (self.IMG_WIDTH // 2)
        starty = y // 2 - (self.IMG_HEIGHT // 2)
        return img[starty:starty + self.IMG_HEIGHT, startx:startx + self.IMG_WIDTH]


    def compute_TVL1(self, prev, curr, bound=15):
        """Compute the TV-L1 optical flow."""
        TVL1 = cv2.optflow.DualTVL1OpticalFlow_create()
        flow = TVL1.calc(prev, curr, None)
        flow = np.clip(flow, -20,20) #default values are +20 and -20
        #print(flow)
        assert flow.dtype == np.float32

        flow = (flow + bound) * (255.0 / (2*bound))
        flow = np.round(flow).astype(int)
        flow[flow >= 255] = 255
        flow[flow <= 0] = 0

        return flow

    def save_anormaly_video(self):
        # print("save_video start")
        file_name = str(datetime.now())[:-7] + ".mp4"
        file_name = file_name.replace(" ", "_").replace(":", "_")
        # print("file_name : ", file_name)
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        # print("self.save_image_list[0].shape[0] ; ", self.save_image_list[0].shape[0])
        # print("self.save_image_list[0].shape[1] : ",self.save_image_list[0].shape[1])
        out = cv2.VideoWriter(file_name, fourcc, 25, (self.save_image_list[0].shape[1], self.save_image_list[0].shape[0]))
        for frame in self.save_image_list:
            # cv2.imwrite("XX.jpg", frame)
            out.write(frame)
        out.release()
        requestUpload(file_name)

    def softmax(self, a) :
        exp_a = np.exp(a)
        sum_exp_a = np.sum(exp_a)
        y = exp_a / sum_exp_a
        
        return y

def requestUpload(file_name):
    UPLOAD_FOLDER = file_name
    managerid = 'user0@testmail.com'
    category = 'Assault'
    params = {"managerid": {managerid}, "category": category}
    with open(UPLOAD_FOLDER , 'rb') as f:
        r = requests.post('http://70.12.229.181:5009/upload', data=params, files={'uploadedfile': f})