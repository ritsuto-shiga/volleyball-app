from roboflow import Roboflow
from ultralytics import YOLO

def main():
    # 1. 新しいデータ (Version 4) をダウンロード
    rf = Roboflow(api_key="IQMqLCnUUlLWkcqeZPpY")
    project = rf.workspace("inoues-workspace").project("ball-player_detection")
    # ここを 4 にすることで、練習動画のデータが反映されます！
    dataset = project.version(4).download("yolov8")

    # 2. モデルを準備（前回の成果 train7 の best.pt を読み込む）
    model = YOLO('runs/detect/runs/detect/train/weights/best.pt')

    # 3. 学習開始！ RTX 2070で火を噴かせましょう
    results = model.train(
        data=f"{dataset.location}/data.yaml",
        epochs=150,
        imgsz=640,       # ボールを認識するために大きくします
        device=0,
        workers=0,
        batch=8    
    )

if __name__ == '__main__':
    main()