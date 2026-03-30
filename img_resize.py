from PIL import Image
import os

input_folder = "imgs"
output_folder = "imgs_resized"
os.makedirs(output_folder, exist_ok=True)

# ターゲットサイズ（例：高さを 300px に統一）
target_height = 300

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
        path = os.path.join(input_folder, filename)
        img = Image.open(path)
        
        # 縦横比を維持してリサイズ
        w, h = img.size
        ratio = target_height / float(h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        
        save_path = os.path.join(output_folder, filename)
        img_resized.save(save_path)
        print(f"Resized {filename} to {new_w}x{new_h}")