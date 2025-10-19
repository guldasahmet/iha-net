import collections.abc
import collections
collections.MutableMapping = collections.abc.MutableMapping
from dronekit import  Command
from PyQt5.QtCore import *
import time
from dronekit import connect ,VehicleMode

class RotaYuklemeThread(QThread):
    # Rota yükleme işlemi tamamlandığında bir sinyal gönderir
    islem_tamamlandi = pyqtSignal(list)

    def __init__(self, aFileName,vehicle):
        super().__init__()
        self.aFileName = aFileName 
        self.vehicle = vehicle
        self.waypoints = []
        

    def run(self):
        # Burada rota yükleme işleminizi gerçekleştirirsiniz
        # Bu işlem, arka planda çalışacak
        self.upload_mission()
        self.islem_tamamlandi.emit(self.waypoints)
        
        # Bu sadece bir örnek, işlem uzun süreceği için arka planda çalışıyor

    def upload_mission(self):
        
        #thread_readmission = threading.Thread(target=self.readmission(aFileName))
        #thread_readmission.start()
        self.missionlist = self.readmission()
        
        cmds = self.vehicle.commands
        cmds.clear()
        for command in self.missionlist:
            cmds.add(command)
        self.vehicle.commands.upload()

        self.vehicle.commands.next = 0 # göreve baştan başalma / yeni 

        time.sleep(1)
        self.vehicle.mode = VehicleMode("AUTO")
        #self.vehicle.mode="AUTO"

        
        
    def readmission(self):
        self.missionlist=[]
        with open(self.aFileName) as f:
            for i, line in enumerate(f):
                if i==0:
                    if not line.startswith('QGC WPL 110'):
                        raise Exception('File is not supported WP version')
                else:
                    linearray=line.split('\t')
                    ln_index=int(linearray[0])
                    ln_currentwp=int(linearray[1])
                    ln_frame=int(linearray[2])
                    ln_command=int(linearray[3])
                    ln_param1=float(linearray[4])
                    ln_param2=float(linearray[5])
                    ln_param3=float(linearray[6])
                    ln_param4=float(linearray[7])
                    ln_param5=float(linearray[8])
                    ln_param6=float(linearray[9])
                    ln_param7=float(linearray[10])
                    ln_autocontinue=int(linearray[11].strip())
                    cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                    self.missionlist.append(cmd)
                    self.waypoints.append([ln_param5,ln_param6,100])
        return self.missionlist
