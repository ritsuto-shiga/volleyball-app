
from roboflow import Roboflow
rf = Roboflow(api_key="IQMqLCnUUlLWkcqeZPpY")
project = rf.workspace("inoues-workspace").project("ball-player_detection")
version = project.version(3)
dataset = version.download("yolov8")
                

                