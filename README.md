import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
import segmentation_models_pytorch as smp
from torch.utils.data import Dataset, DataLoader

# 1. إعداد الجهاز (GPU أو CPU)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

# 2. إنشاء Dataset مخصص لقراءة الصور والأقنعة الحقيقية من المجلدات
class ISICRealDataset(Dataset):
    def __init__(self, csv_file, img_dir, mask_dir, max_samples=32):  # تم زيادة عدد العينات هنا
        self.df = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.mask_dir = mask_dir
        self.samples = []
        
        # البحث الفعلي عن العينات التي تمتلك صورة وماسك حقيقيين في المجلدات
        for idx, row in self.df.iterrows():
            img_id = row['image_id']
            img_path = self.find_file(self.img_dir, img_id)
            mask_path = self.find_file(self.mask_dir, img_id)
            
            if img_path and mask_path:
                self.samples.append((img_path, mask_path, img_id))
                if len(self.samples) >= max_samples:
                    break
        print(f"[✔] تم العثور على {len(self.samples)} عينة حقيقية مطابقة للصور والأقنعة في المجلدات.")

    def find_file(self, base_dir, target_id):
        if not os.path.exists(base_dir):
            return None
        target_lower = target_id.lower()
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if target_lower in file.lower():
                    return os.path.join(root, file)
        return None

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, mask_path, img_id = self.samples[idx]
        
        # قراءة وتجهيز الصورة الأصلية (256x256)
        img = Image.open(img_path).convert("RGB").resize((256, 256))
        img_arr = np.array(img, dtype=np.float32) / 255.0
        # تحويل من HWC إلى CHW لـ PyTorch
        img_tensor = torch.tensor(img_arr).permute(2, 0, 1)
        
        # قراءة وتجهيز الماسك الحقيقي (256x256)
        mask = Image.open(mask_path).convert("L").resize((256, 256), Image.NEAREST)
        mask_arr = np.array(mask, dtype=np.float32)
        if mask_arr.max() > 1.0:
            mask_arr = mask_arr / 255.0
        mask_binary = (mask_arr > 0.5).astype(np.float32)
        mask_tensor = torch.tensor(mask_binary).unsqueeze(0) # شكل [1, 256, 256]
        
        return img_tensor, mask_tensor, img_id

# 3. تحميل البيانات الحقيقية عبر DataLoader
dataset = ISICRealDataset("HAM10000_metadata.csv", "images", "masks", max_samples=32)
if len(dataset) == 0:
    print("[خطأ تنبيهي] لم يتم العثور على أي ملفات مطابقة في مجلدي images و masks. تأكد من وضعهما في نفس المسار.")
    exit()

loader = DataLoader(dataset, batch_size=4, shuffle=True)

# 4. بناء نماذج التجزئة الحقيقية
model_unet = smp.Unet(encoder_name="resnet34", encoder_weights="imagenet", in_channels=3, classes=1).to(DEVICE)
model_unet_plus = smp.UnetPlusPlus(encoder_name="resnet34", encoder_weights="imagenet", in_channels=3, classes=1).to(DEVICE)

# 5. دالة الخسارة والمحسنات
criterion = smp.losses.DiceLoss(smp.losses.BINARY_MODE, from_logits=True)
opt_unet = optim.Adam(model_unet.parameters(), lr=0.001)
opt_plus = optim.Adam(model_unet_plus.parameters(), lr=0.001)

# 6. حساب مقاييس الأداء بدقة رياضية
def evaluate_metrics(outputs, masks):
    preds = (torch.sigmoid(outputs) > 0.5).float()
    intersection = (preds * masks).sum()
    dice = (2. * intersection + 1e-6) / (preds.sum() + masks.sum() + 1e-6)
    union = preds.sum() + masks.sum() - intersection
    iou = (intersection + 1e-6) / (union + 1e-6)
    return dice.item(), iou.item()

# 7. دالة التدريب الحقيقي على عيناتك
def train_model(model, optimizer, model_name):
    model.train()
    epochs = 15  # تم زيادة عدد دورات التدريب هنا للحصول على دقة عالية
    final_dice, final_iou = 0, 0
    
    for epoch in range(epochs):
        ep_d, ep_i = 0, 0
        for images, masks, _ in loader:
            images, masks = images.to(DEVICE), masks.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()
            
            d, i = evaluate_metrics(outputs, masks)
            ep_d += d
            ep_i += i
            
        final_dice = ep_d / len(loader)
        final_iou = ep_i / len(loader)
        print(f"[{model_name}] Epoch [{epoch+1}/{epochs}] -> Dice: {final_dice:.4f}, IoU: {final_iou:.4f}")
        
    return final_dice, final_iou

print("\n--- بدء التدريب والتقييم على العينات والأقنعة الحقيقية الخاصة بك ---")
dice_standard, iou_standard = train_model(model_unet, opt_unet, "Standard U-Net")
dice_attention, iou_attention = train_model(model_unet_plus, opt_plus, "Attention/Nested U-Net")

# 8. حفظ النتائج البيانية للسمنار
models = ['Standard U-Net', 'Attention/Nested U-Net']
dice_scores = [dice_standard, dice_attention]
iou_scores = [iou_standard, iou_attention]

x = range(len(models))
plt.figure(figsize=(8, 5))
plt.bar([i - 0.2 for i in x], dice_scores, width=0.4, label='Dice Coefficient', color='skyblue')
plt.bar([i + 0.2 for i in x], iou_scores, width=0.4, label='IoU Score', color='salmon')

plt.xlabel('Model Architectures', fontsize=12)
plt.ylabel('Score Value', fontsize=12)
plt.title('Real Data Comparison: U-Net vs Attention/Nested U-Net', fontsize=14)
plt.xticks(x, models)
plt.ylim(0, 1.0)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('comparison_results.png', dpi=300, bbox_inches='tight')
plt.close()
print("\n[✔] تم حفظ الرسم البياني الحقيقي بنجاح باسم 'comparison_results.png'")

# 9. توليد وعرض المقارنة البصرية الحقيقية للعينات
model_unet.eval()
model_unet_plus.eval()

with torch.no_grad():
    for sample_images, sample_masks, sample_ids in loader:
        sample_img = sample_images[0:1].to(DEVICE)
        sample_mask = sample_masks[0:1].to(DEVICE)
        img_id = sample_ids[0]
        
        pred_standard = (torch.sigmoid(model_unet(sample_img)) > 0.5).float()
        pred_attention = (torch.sigmoid(model_unet_plus(sample_img)) > 0.5).float()
        
        d_std, i_std = evaluate_metrics(model_unet(sample_img), sample_mask)
        d_att, i_att = evaluate_metrics(model_unet_plus(sample_img), sample_mask)
        
        img_np = sample_images[0].cpu().numpy().transpose(1, 2, 0)
        mask_np = sample_mask[0, 0].cpu().numpy()
        pred_std_np = pred_standard[0, 0].cpu().numpy()
        pred_att_np = pred_attention[0, 0].cpu().numpy()
        
        fig, axes = plt.subplots(1, 4, figsize=(14, 4))
        plt.suptitle(f"Real ISIC ID: {img_id}", fontsize=12, fontweight='bold')
        
        axes[0].imshow(img_np)
        axes[0].set_title("Original Image")
        axes[0].axis('off')
        
        axes[1].imshow(mask_np, cmap='gray')
        axes[1].set_title("Ground Truth Mask")
        axes[1].axis('off')
        
        axes[2].imshow(pred_std_np, cmap='gray')
        axes[2].set_title(f"Standard U-Net\nDice: {d_std:.2f}")
        axes[2].axis('off')
        
        axes[3].imshow(pred_att_np, cmap='gray')
        axes[3].set_title(f"Attention/Nested U-Net\nDice: {d_att:.2f}")
        axes[3].axis('off')
        
        plt.tight_layout()
        plt.savefig('segmentation_visual_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        print(f"[✔] تم استعراض وحفظ المقارنة البصرية الحقيقية للـ ID: {img_id}")
        break
