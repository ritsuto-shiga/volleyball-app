import cv2
import numpy as np

# --- 井上さんが取得した座標 (左奥, 右奥, 右手前, 左手前) ---
src_pts = np.float32([
    [444, 476],   # 左奥
    [1370, 472],  # 右奥
    [1880, 1046], # 右手前
    [198, 1068]   # 左手前
])

# --- 変換後のサイズ設定 (9m x 9m のコート半面を 500x500px に投影) ---
side = 500
dst_pts = np.float32([
    [0, 0],       # 左奥を(0,0)へ
    [side, 0],    # 右奥を(500,0)へ
    [side, side], # 右手前を(500,500)へ
    [0, side]     # 左手前を(0,500)へ
])

# 変換行列の計算
matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)

def get_zone(x, y):
    """変換後の座標(x, y)からバレーのゾーン(1-9)を判定する関数"""
    # 3x3のグリッドに分割
    col = int(x / (side / 3)) # 0, 1, 2
    row = int(y / (side / 3)) # 0, 1, 2
    
    # バレーの一般的なゾーン番号（エンド側から見て）
    # 1 6 5
    # 8 3 4
    # 9 2 7  (※チームのルールに合わせて書き換え可能です)
    zones = [
        [1, 6, 5],
        [8, 3, 4],
        [9, 2, 7]
    ]
    # 範囲外エラー防止
    col = max(0, min(2, col))
    row = max(0, min(2, row))
    return zones[row][col]

# --- 動作確認 ---
# 適当な座標（例：コートの真ん中あたり）がどのゾーンになるかテスト
test_point = np.array([[[1000, 700]]], dtype=np.float32) # 元の動画の座標
transformed_pt = cv2.perspectiveTransform(test_point, matrix)
tx, ty = transformed_pt[0][0]
zone = get_zone(tx, ty)

print(f"テスト座標 (1000, 700) は、変換後 ({tx:.1f}, {ty:.1f}) になり、ゾーンは 【 {zone} 】 です。")