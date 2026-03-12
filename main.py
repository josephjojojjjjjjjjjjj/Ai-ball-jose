import cv2
import numpy as np
import time

from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class JosephApp(App):

    def build(self):

        self.layout = BoxLayout(orientation='vertical')

        self.img1 = Image()
        self.layout.add_widget(self.img1)

        self.info_label = Label(
            text="JosephApp Ready",
            size_hint_y=.15
        )

        self.layout.add_widget(self.info_label)

        self.cap = cv2.VideoCapture(0)

        self.ball_points=[]
        self.frame_times=[]

        self.PITCH_LENGTH=20.12
        self.CREASE_Y=450

        Clock.schedule_interval(self.update,1.0/30.0)

        return self.layout


    def detect_ball(self,frame):

        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

        lower=np.array([5,100,100])
        upper=np.array([25,255,255])

        mask=cv2.inRange(hsv,lower,upper)

        contours,_=cv2.findContours(
            mask,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for c in contours:

            area=cv2.contourArea(c)

            if area>200:

                x,y,w,h=cv2.boundingRect(c)

                center=(x+w//2,y+h//2)

                return center,(x,y,w,h)

        return None,None


    def update(self,dt):

        ret,frame=self.cap.read()

        if not ret:
            return

        h,w,_=frame.shape

        center,box=self.detect_ball(frame)

        if center:

            self.ball_points.append(center)

            self.frame_times.append(time.time())

            x,y,bw,bh=box

            cv2.rectangle(
                frame,
                (x,y),
                (x+bw,y+bh),
                (255,255,255),
                2
            )

        for i in range(1,len(self.ball_points)):

            cv2.line(
                frame,
                self.ball_points[i-1],
                self.ball_points[i],
                (0,255,255),
                2
            )

        speed_text="Speed: 0 km/h"

        if len(self.frame_times)>5:

            t=self.frame_times[-1]-self.frame_times[0]

            if t>0:

                speed=(self.PITCH_LENGTH/t)*3.6

                speed_text=f"Speed: {int(speed)} km/h"


        cv2.line(
            frame,
            (0,self.CREASE_Y),
            (w,self.CREASE_Y),
            (0,0,255),
            2
        )

        self.info_label.text=speed_text

        buf=cv2.flip(frame,0).tobytes()

        texture=Texture.create(
            size=(frame.shape[1],frame.shape[0]),
            colorfmt='bgr'
        )

        texture.blit_buffer(
            buf,
            colorfmt='bgr',
            bufferfmt='ubyte'
        )

        self.img1.texture=texture


if __name__=="__main__":
    JosephApp().run()
