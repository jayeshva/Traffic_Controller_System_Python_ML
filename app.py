import numpy as np
import time
import cv2 
from flask import Flask, jsonify, render_template, Response
largura_min=80 #Largura minima do retangulo
altura_min=80 #Altura minima do retangulo

offset=6 #Erro permitido entre pixel  
warn="WAIT 15 SECONDS !!!!!!!"
pos_linha=550 #Posição da linha de contagem 

delay= 60 #FPS do vídeo
n=0

detec = []

app = Flask(__name__)
sub = cv2.createBackgroundSubtractorMOG2()  # create background subtractor
@app.route('/update_decimal',methods=['POST'])
def update_decimal():
    global n
    global warn
    global carros
    if n==0:
       warn=""
       random_decimal="GREEN"
    else:
        carros=0
        random_decimal="RED - Wait 10 secs.."

    


    print(random_decimal)
    return jsonify('',render_template('random_decimal.html',x=random_decimal))


@app.route('/')

   
def index():
    """Video streaming home page."""
    return render_template('index.html')


def pega_centro(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx,cy
def gen():
    carros=0
    global largura_min 
    global altura_min

    global offset

    global pos_linha 

    global delay 

    global detec
    """Video streaming generator function."""
    cap = cv2.VideoCapture('video1.mp4')

    # Read until video is completed
    while(cap.isOpened()):
      # Capture frame-by-frame
        ret, frame1 = cap.read()
        if not ret: #if vid finish repeat
           frame1 = cv2.VideoCapture("video1.mp4")
           continue
        if ret:            
           image = cv2.resize(frame1, (0, 0), None, 1, 1)
           grey = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
           blur = cv2.GaussianBlur(grey,(3,3),5)
           img_sub = sub.apply(blur)
           dilat = cv2.dilate(img_sub,np.ones((5,5)))
           kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
           dilatada = cv2.morphologyEx (dilat, cv2. MORPH_CLOSE , kernel)
           dilatada = cv2.morphologyEx (dilatada, cv2. MORPH_CLOSE , kernel)
           contorno,h=cv2.findContours(dilatada,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
           
           cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (255,127,0), 3) 
           for(i,c) in enumerate(contorno):
              (x,y,w,h) = cv2.boundingRect(c)
              validar_contorno = (w >= largura_min) and (h >= altura_min)
              if not validar_contorno:
                  continue

              cv2.rectangle(frame1,(x,y),(x+w,y+h),(0,255,0),2)        
              centro = pega_centro(x, y, w, h)
              detec.append(centro)
              cv2.circle(frame1, centro, 4, (0, 0,255), -1)

              for (x,y) in detec:
                  if y<(pos_linha+offset) and y>(pos_linha-offset):
                      carros+=1
                      cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (0,127,255), 3)  
                      detec.remove((x,y))
                      

                      print("car is detected : "+str(carros))  
                    
                      
                      if carros > 10:
                        global n
                        carros=10
                        cv2.putText(frame1, "VEHICLE COUNT : 10", (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255),5)
                        
                        n=1
                        carros=0
                        
                        time.sleep(20)
                        n=0
                        
                        
                        
                        
                        
        

                   
        cv2.putText(frame1, "VEHICLE COUNT : "+str(carros), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255),5)
        cv2.imshow("Video Original" , frame1)
        cv2.imshow("Detectar",dilatada)
        
        frame1 = cv2.imencode('.jpg', frame1)[1].tobytes()
        yield (b'--frame1\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame1 + b'\r\n')
        # time.sleep(0.1)
       
        if cv2.waitKey(1) == 27:
           break    

@app.route('/video_feed')

def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
