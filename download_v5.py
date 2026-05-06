from roboflow import Roboflow
from ultralytics import YOLO
import os

def main():
    # 1. Roboflowから最新の Version 5 をダウンロード
    print("Version 5 のデータをダウンロードしています...")
    rf = Roboflow(api_key="IQMqLCnUUlLWkcqeZPpY")
    project = rf.workspace("inoues-workspace").project("ball-player_detection")
    
    # ★ここが 5 になっていることを確認！
    dataset = project.version(5).download("yolov8")

    # 2. 前回の学習成果を読み込む
    # train7 もしくは train8 など、一番最新の best.pt がある場所を指定してください
    model_path = "runs/detect/runs/detect/train2/weights/best.pt"
    
    if not os.path.exists(model_path):
        print(f"エラー: {model_path} が見つかりません。")
        print("エクスプローラーで前回の学習結果のフォルダ名を確認してください。")
        return

    model = YOLO(model_path)

    # 3. 学習開始
    print("学習を開始します。RTX 2070で特訓開始！")
    results = model.train(
        data=f"{dataset.location}/data.yaml",
        epochs=150,           # 525枚あるので、150回しっかり回します
        imgsz=640,            # ボールのために高解像度を維持
        device=0,             # GPUを使用
        workers=0,
        batch=8,              # メモリ不足なら 4 に下げてください
        # 枠をスリムにするための追加設定
        close_mosaic=20,      # 最後の20エポックで画像加工を止めて精度を追い込む
    )

if __name__ == '__main__':
    main()