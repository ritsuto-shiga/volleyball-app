from ultralytics import YOLO

# 150回学習した最新モデルをロード
model = YOLO('runs/detect/runs/detect/train2/weights/best.pt')

# 動画解析（自信の閾値を 0.15 まで下げて、ボールを見逃さないようにします）
results = model.predict(
    source='2026_harukou_final_1set_6play.mp4', 
    save=True, 
    conf=0.15,      # 0.25から0.15に下げて、積極的に枠を出させます
    iou=0.4
)

print("✨ 解析完了！ runs/detect/predict フォルダを見てください。")