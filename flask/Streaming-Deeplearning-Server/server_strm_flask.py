# Flask 기반 영상 분석 및 스트리밍 서버 
# - cctv에서 영상을 받아서 이상행동 분석 
# - 웹으로부터 영상 전송 요청이 오면 영상 전송
# - 이상행동이 검출되면 구독 토큰이 생성된 곳으로 푸시 알림 및 videoRestServer로 검출된 영상 전송
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from imutils.video import VideoStream
import cv2
import sys
import imagezmq
import imutils
import numpy as np
import threading
import os
from two_stream_final_model import twostream_FinalModel
import argparse

#for push
from pywebpush import webpush, WebPushException
import logging
import json, os

from flask_cors import CORS


os.environ["CUDA_VISIBLE_DEVICES"]="0"


Flag = False
app = Flask(__name__)

#for push
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

#for CORS
CORS(app)

#for push
DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(os.getcwd(),"private_key.txt")
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(os.getcwd(),"public_key.txt")

VAPID_PRIVATE_KEY = open(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, "r+").readline().strip("\n")
VAPID_PUBLIC_KEY = open(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, "r+").read().strip("\n")

VAPID_CLAIMS = {
"sub": "mailto:help@finder.com"
}

#push를 위한 global token
global_token = None

#push 알림 함수
# subscription_information : global_token
# message_body : 보낼 메세지
def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )


@app.route('/')
def index():
    return render_template("index.html")

#push notification 구독 신청 및 토큰 저장
#GET : 푸시 알림을 보내는데 사용하기 위한 공개키 전달
#POST : 생성된 토큰을 global_token에 저장
@app.route("/subscription/", methods=["GET", "POST"])
def subscription():

    global global_token
    #GET    
    if request.method == "GET":
        return Response(response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
            headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")
    #POST
    subscription_token = request.get_json("subscription_token")
    global_token = json.loads(subscription_token["subscription_token"])
    return jsonify({'success':1})


def sendImagesToWeb():
    global global_token

    #라즈베리파이에서 전해주는 이미지를 받을 리시버 생성
    # receiver = imagezmq.ImageHub(open_port='tcp://0.0.0.0:5566', REQ_REP = Flse)
    receiver = imagezmq.ImageHub()

    while True:
        #receive image
        (camName, frame) = receiver.recv_image()
        receiver.send_reply(b'OK')

        #recognition using deep learning
        jpg, alarm, action = model.predict(frame)

        if alarm is True:
          # send alarm
          word = "상황 발생"
        	if action == "Assault":
        		word = "폭행 "+ word
        		send_web_push(global_token, word)
        	elif action == "Swoon":
        		word = "실신 " + word
        		send_web_push(global_token, word)

        #encoding image    
        (flag, jpg) = cv2.imencode('.jpg', jpg)
        
        if not flag:
            continue

        #send image to web
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(jpg) + b'\r\n')
   
@app.route('/video_feed')
def video_feed():
    return Response(sendImagesToWeb(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    #실행 시 명령어
    parser = argparse.ArgumentParser(description="default usage : python server_strm_flask.py --rgb_model Final_weights/weights_i3d_RGB_no_softmax.hdf5")
    parser.add_argument('--rgb_model', required=True, help="RGB model weights")
    parser.add_argument('--opt_model', default=None, required=False, help="opt_model weights")
    args = parser.parse_args()

    #서버 실행
    if Flag is False:
        model = twostream_FinalModel(args.rgb_model, args.opt_model)
        Flag = True
    app.run(host="0.0.0.0", debug = True, use_reloader=False)


