from roboflow import Roboflow

# セットアップ
rf = Roboflow(api_key="IQMqLCnUUlLWkcqeZPpY")
project = rf.workspace("inoues-workspace").project("ball-player_detection")

# 今回の学習成果を「Version 5」に紐付けます
version = project.version(5)

model_path = "C:/Users/USER/OneDrive/デスクトップ/volleyball_project/runs/detect/runs/detect/train2"

print("最新モデルを Roboflow にデプロイ中...")
version.deploy(model_type="yolov8", model_path=model_path)
print("デプロイ完了！")