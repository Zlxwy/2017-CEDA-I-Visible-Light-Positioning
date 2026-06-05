import sensor,image,lcd
import math
import time
from machine import Timer
from Maix import GPIO
from board import board_info
from fpioa_manager import fm

#exposure_time = 70 #曝光时间，曝光时间越短，快门速度越快，单位us70

my_threshold   = [92, 100, 101, -49, -41, 127]#白色块的LAB值[95, 100, -74, 59, -6, 127]

my_limit = [15,15,15,15,15,15]#lab偏差值设定
area = [155,115,10,10]#中心10*10的方块

Time = 0
Time2 = 0

flag=1

Time_Achanges = 0
Time_Bchanges = 0
Time_Cchanges = 0

def maymax(array1,array2):
    uu = [0,0,0]
    sorted(array1)
    if len(array1)>=3:
        for num in range(0,3):
            for u in range(0,len(array1)):
                if array1[len(array1)-num-1]==array2[u]:
                    uu[num] = u
                    break
    return uu

def on_timer(timer):
    global Time
    Time = Time + 1
    #print((Time))

def on_timer2(timer):
    global Time2
    Time2 = 1



def Area(x,y):
    if x>(-20) and x<20 and y>(-20) and y<20:
        return 'A'
    if  y>20 and y<40 and x>(-y) and x<y:
        return 'B'
    if x>20 and x<40 and y<x and y>(-x):
        return 'C'
    if  y>(-40) and y<(-20) and x>y and x<(-y):
        return 'D'
    if x>(-40) and x<(-20) and y<(-x) and y>x:
        return 'E'

tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PERIODIC, period=100, unit=Timer.UNIT_MS, callback=on_timer, arg=on_timer, start=False, priority=1, div=0)
tim1 = Timer(Timer.TIMER1, Timer.CHANNEL1, mode=Timer.MODE_PERIODIC, period=500, unit=Timer.UNIT_MS, callback=on_timer2, arg=on_timer2, start=True, priority=1, div=0)

c=0
s={}
ss={}
x={}
y={}
AS = 0.01
BS = 0.01
CS = 0.01
AS2 = 0
BS2 = 0
CS2 = 0

lcd.init()
lcd.rotation(0)#针对bit做的画面调整
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)#设置为VGA图像异常，可能为缓存不足

#sensor.set_brightness(2)
#sensor.set_contrast(2)

#sensor.set_auto_gain(False)
#sensor.set_auto_whitebal(False)
#sensor.set_auto_exposure(False,exposure_us = exposure_time)

#sensor.set_windowing((224,224))
#sensor.set_hmirror(0)#摄像头是否镜像

sensor.run(1)#启用摄像头
sensor.skip_frames(30)#跳过部分帧数


while(True):

    img = sensor.snapshot()
    #a = img.binary([((10,15))],invert = 1)#二值化，便于观察结果

    blobs = img.find_blobs([my_threshold])#寻找色块，并建立blob对象
    if blobs:

        for b in blobs:
            tmp=img.draw_rectangle(b[0:4],color=(255,255,0))#画一个框

            x[c]=b[5]
            y[c]=b[6]

            s[c]=b[4]
            ss[c]=b[4]
            c=c+1

        if len(ss)==1:
            x1 = x[0]
            y1 = y[0]
            xx=(x1-160)/5+3.3
            yy=-(y1-120)/5+9
            tmp=img.draw_cross(x1,y1,color=(255,255,0))#画一个十字

            tmp=img.draw_string(3,3,("(%.1f,%.1f)" %(xx,yy)), color=(0,0,255), scale=2)
            tmp=img.draw_string(3,30,("area=%s"%Area(xx,yy)), color=(0,0,255), scale=2)

        if len(ss)==2:
            x1 = x[0]
            y1 = y[0]
            x2 = x[1]
            y2 = y[1]
            x4=(x1+x2)/2
            y4=(y1+y2)/2

            xx=(x4-160)/4.8
            yy=-(y4-120)/5-5

            tmp=img.draw_cross(x1,y1,color=(255,0,0))#画一个十字
            tmp=img.draw_cross(x2,y2,color=(255,0,0))#画一个十字
            tmp=img.draw_string(3,3,("(%.1f,%.1f)" %(xx,yy)), color=(0,0,255), scale=2)
            tmp=img.draw_string(3,30,("area=%s"%Area(xx,yy)), color=(0,0,255), scale=2)


        if len(ss)>=3:

            x1 = x[maymax(s,ss)[0]]
            y1 = y[maymax(s,ss)[0]]
            S1 = ss[maymax(s,ss)[0]]

            x2 = x[maymax(s,ss)[1]]
            y2 = y[maymax(s,ss)[1]]
            S2 = ss[maymax(s,ss)[1]]

            x3 = x[maymax(s,ss)[2]]
            y3 = y[maymax(s,ss)[2]]
            S3 = ss[maymax(s,ss)[2]]

            d12 = math.pow((x1 - x2)*(x1 - x2)+(y1 - y2)*(y1 - y2) , 0.5)
            d13 = math.pow((x1 - x3)*(x1 - x3)+(y1 - y3)*(y1 - y3) , 0.5)
            d23 = math.pow((x2 - x3)*(x2 - x3)+(y2 - y3)*(y2 - y3) , 0.5)

            if d12<d13 and d13<d23:#情况1
                Ax = x1
                Ay = y1
                AS = S1
                Bx = x2
                By = y2
                BS = S2
                Cx = x3
                Cy = y3
                CS = S3
            if d13<d12 and d12<d23:#情况2
                Ax = x1
                Ay = y1
                AS = S1
                Bx = x3
                By = y3
                BS = S3
                Cx = x2
                Cy = y2
                CS = S2
            if d12<d23 and d23<d13:#情况3
                Ax = x2
                Ay = y2
                AS = S2
                Bx = x1
                By = y1
                BS = S1
                Cx = x3
                Cy = y3
                CS = S3
            if d13<d23 and d23<d12:#情况4
                Ax = x3
                Ay = y3
                AS = S3
                Bx = x1
                By = y1
                BS = S1
                Cx = x2
                Cy = y2
                CS = S2
            if d23<d13 and d13<d12:#情况5
                Ax = x3
                Ay = y3
                AS = S3
                Bx = x2
                By = y2
                BS = S2
                Cx = x1
                Cy = y1
                CS = S1
            if d23<d12 and d12<d13:#情况6
                Ax = x2
                Ay = y2
                AS = S2
                Bx = x3
                By = y3
                BS = S3
                Cx = x1
                Cy = y1
                CS = S1



                AS_changes = abs(AS-AS2)/AS
                BS_changes = abs(BS-BS2)/BS
                CS_changes = abs(CS-CS2)/CS
                AS2 = AS
                BS2 = BS
                CS2 = CS

                #AS_changes
                #BS_changes
                #CS_changes

                #print(666)


                if AS_changes>0.15 and flag==1:
                    tim.start()
                    flag = 0
                if AS_changes>0.15 and flag==0 and Time>=5:
                    tim.stop()
                    flag=1
                    Time_Achanges=Time*0.1
                    Time_Bchanges=0
                    Time_Cchanges=0
                    #print(round(Time_Achanges))#四舍五入取整
                    Time = 0


                if BS_changes>0.15 and flag==1:
                    tim.start()
                    flag = 0
                if BS_changes>0.15 and flag==0 and Time>=5:
                    tim.stop()
                    flag=1
                    Time_Bchanges=Time*0.1
                    Time_Achanges=0
                    Time_Cchanges=0
                    #print(round(Time_Bchanges))#四舍五入取整
                    Time = 0


                if CS_changes>0.15 and flag==1:
                    tim.start()
                    flag = 0
                if CS_changes>0.15 and flag==0 and Time>=5:
                    tim.stop()
                    flag=1
                    Time_Cchanges=Time*0.1
                    Time_Achanges=0
                    Time_Bchanges=0
                    #print(round(Time_Cchanges))#四舍五入取整
                    Time = 0

            tmp=img.draw_string(3,150, ("A Time=%d" %(round(Time_Achanges))), color=(0,0,255), scale=2)
            tmp=img.draw_string(3,180, ("B Time=%d" %(round(Time_Bchanges))), color=(0,0,255), scale=2)
            tmp=img.draw_string(3,210, ("C Time=%d" %(round(Time_Cchanges))), color=(0,0,255), scale=2)

            tmp=img.draw_cross(x1, y1,color=(255,0,0))#画一个十字
            tmp=img.draw_cross(x2, y2,color=(255,0,0))#画一个十字
            tmp=img.draw_cross(x3, y3,color=(255,0,0))#画一个十字

            tmp=img.draw_string(Ax,Ay, "A", color=(255,0,0), scale=2)
            tmp=img.draw_string(Bx,By, "B", color=(255,0,0), scale=2)
            tmp=img.draw_string(Cx,Cy, "C", color=(255,0,0), scale=2)




            x0=(Cx+Bx)/2
            y0=(Cy+By)/2

            xx=(x0-160)/4.9
            yy=-(y0-120)/4.9
            Xab = Bx-Ax
            Yab = By-Ay
            if Xab==0:
                angle=90
            if Xab>0:
                angle = -(math.atan(Yab/Xab)*180)/3.1415

            if Xab<0:
                angle = -(math.atan(Yab/Xab)*180)/3.1415+180
            if angle>180:
                angle = angle-360
            angle2=angle*3.1415/180

            tmp=img.draw_string(160,30,("angle=%d"%angle), color=(0,0,255), scale=2)

            #tmp=img.draw_string(3,3,("(%d,%d)" %(x0,y0)), color=(0,0,255), scale=2)
            tmp=img.draw_cross(round((Cx+Bx)/2), round((Cy+By)/2),color=(255,255,0))#画一个十字

            if Time2==1:
                Time2=0
                if yy!=0:

                    XX=-math.pow(xx*xx+yy*yy , 0.5)*math.sin(angle2 + math.atan(xx/yy))
                    YY=-math.pow(xx*xx+yy*yy , 0.5)*math.cos(angle2 + math.atan(xx/yy))
            YY
            if y0>120:

                if YY>=6:

                    tmp=img.draw_string(3,3,("(%.1f,%.1f)" %(XX,YY+3)), color=(0,0,255), scale=2)
                    tmp=img.draw_string(3,30,("area=%s"%Area(XX,YY+3)), color=(0,0,255), scale=2)
                else:
                    tmp=img.draw_string(3,3,("(%.1f,%.1f)" %(XX,YY+1)), color=(0,0,255), scale=2)
                    tmp=img.draw_string(3,30,("area=%s"%Area(XX,YY+1)), color=(0,0,255), scale=2)
            if y0<=120:
                if YY<-6:

                    tmp=img.draw_string(3,3,("(%.1f,%.1f)" %(-XX,-YY+3)), color=(0,0,255), scale=2)
                    tmp=img.draw_string(3,30,("area=%s"%Area(-XX,-YY+3)), color=(0,0,255), scale=2)

                else:
                    tmp=img.draw_string(3,3,("(%.1f,%.1f)" %(-XX,-YY+1)), color=(0,0,255), scale=2)
                    tmp=img.draw_string(3,30,("area=%s"%Area(-XX,-YY+1)), color=(0,0,255), scale=2)
            #if yy!=0:
                #tmp=img.draw_string(160,30,("jiao2=%d"%(math.atan(xx/yy)*180/3.14)), color=(0,0,255), scale=2)
                #tmp=img.draw_string(160,60,("jiao3=%d"%(math.atan(xx/yy)*180/3.14+angle)), color=(0,0,255), scale=2)
            #tmp=img.draw_string(3,30,("(%.1f,%.1f)" %(xx,yy)), color=(0,0,255), scale=2)

        c=0
        s={}
        ss={}


        tmp=img.draw_cross(160, 120,color=(255,100,0))#画一个十字
    lcd.display(img)


