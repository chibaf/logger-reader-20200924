import serial, sys, queue
import re, time
#from pylab import *
from threading import (Event, Thread)

S_200913="""
read_serial02d_x200815_1（Tcを読む、木下が変更）から
HNGN90_chibaf_4ced3_200517_copy.py（千葉さん）から
改造
"""


s1="""
ls /dev/usb*  でM5のつながっているポートを探して同定。
Python (出力ファイル名)　（port名）　で起動
>>


{200815_1}
（threadingを使用）
read_serial02d_x200815_1.py
read_serial02d_x200814_6.py

Threadで読み込みの並列化をして
Eventの、wait,   set/clear
Queueの、put/get
などが少し使えるようになった。
event.clear()　#フラグを false にして止める
これで両方のthreadからアウトプットが連続的に出るようになった。



>>
{200812}
UARTのバッファA=ser.in_waitingを監視した。
200812_2ではf.write(",".join(line_s))に異常が見られない
しかし、print(A,B,line_s)では
800を越えると、
UARTのバッファに92が出てくる。たまに^[[B92とか雑音？が入る
>>
{200812-2}
バッファに溜まっている数：in_waitingを監視している。
92 or 0 に留まる処まで持ってこれた。

>>
{200813}
Thread間のデータのやり取りに、
Queueを使ってみたい。

"""
s2="""set()
内部フラグの値を true にセットします。フラグの値が true になるのを待っている全てのスレッドを起こします。一旦フラグが true になると、スレッドが wait() を呼び出しても全くブロックしなくなります。

clear()
内部フラグの値を false にリセットします。以降は、 set() を呼び出して再び内部フラグの値を true にセットするまで、 wait() を呼び出したスレッドはブロックするようになります。

wait(timeout=None)
内部フラグの値が true になるまでブロックします。 wait() 処理に入った時点で内部フラグの値が true であれば、直ちに処理を戻します。そうでない場合、他のスレッドが set() を呼び出してフラグの値を true にセットするか、オプションのタイムアウトが発生するまでブロックします。
"""

itime=0


def port_read():
  ser.reset_input_buffer
  line_byte = ser.readline()  #一回、読み飛ばしをかける
  #一回バッファークリアしないといけない？？？
  ser.reset_input_buffer
  time.sleep(0.2)
  while True:
    try:
      A=ser.in_waiting
      if (ser.in_waiting)>0:
        line_byte = ser.readline()
        q.put(line_byte)
        if False :
          print(A,q.qsize(),line_byte)
          #(q.qsize(),"=queue_size")
        event.wait()
    except KeyboardInterrupt:
      print ('exiting thread-1 in port_read')
      sys.exit

def PID():
  itime=0
  time.sleep(0.2)
  event.set()#フラグを true にして起動
  time.sleep(3)
  if False :      #debug
    event.clear() #フラグを false にして止める
  time.sleep(1)
  print("plotting now")
  while True:
    itime=itime+0.1
    line_byte=q.get()
    #print(q.qsize(),"line_byte",line_byte)
    line=line_byte.decode(encoding='utf-8')
     #line=line.replace("\x000","")
    line_s=line.split(',')  # list of numbers(character) separated by "," 
    line_s.insert(0,str(itime))
    f.write(",".join(line_s))
    line_p=str(line).replace("\r\n","")
    T_meas=float(line_s[2])  # temperature is from float(line_s[2]).  coreresponds to Tc-1.
    print(float(line_s[2]))   
    s_work="""
    T_measは、Tc-1なので、これをPIDの計測値としてPID制御をする。
    """
    itime=itime+0.1

    

#     time.sleep(1)

event=Event()
q = queue.Queue()

strPort = sys.argv[2]   # serial port
ser=serial.Serial(strPort,115200,timeout=0) #20200627 115200->19200
ser.send_break()
ser.reset_input_buffer
ser.reset_input_buffer
ser.reset_input_buffer
ser.reset_input_buffer
#何回もリセットするとin_waitingの数が減る。
#スリープさせるとin_waitingの数が増えてくる。
print("connected to: " + ser.portstr)

file=sys.argv[1]  # file name
regex = re.compile('\d+')  # for extracting number from strings
f=open(file,"w+")
y=[0]*100
data=[];

thread1 = Thread(target=port_read)
thread2 = Thread(target=PID)

thread1.start()
time.sleep(3)
thread2.start()


thread1.join()
print ('exiting at thread1.join')
ser.close()
f.close()

#thread2.start()

ser.reset_input_buffer
ser.close()
f.close()
