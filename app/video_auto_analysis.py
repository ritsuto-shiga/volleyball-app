import cv2
import os

# 解析したい動画のパス（あとでこの場所に動画を置いてください）
video_path = 'data/raw_videos/test_video.mp4'

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"クリック座標: (x={x}, y={y})")
        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('Court Mapping', img)

# 動画の読み込み
cap = cv2.VideoCapture(video_path)
success, img = cap.read()

if not success:
    print(f"\n[!] エラー: {video_path} が見つかりません。")
    print("data/raw_videos/ フォルダに 'test_video.mp4' という名前で動画を置くか、")
    print("コード内の video_path を書き換えてください。")
else:
    cv2.imshow('Court Mapping', img)
    cv2.setMouseCallback('Court Mapping', click_event)
    print("コートの四隅をクリックしてください。終了は何かキーを押してください。")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cap.release()