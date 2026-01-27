import sys

sys.path.append("..")
import torch
from torch.nn import init
from torch.utils.data import DataLoader
from data_set import make
from net import unet
from utils import dice_loss
import matplotlib.pyplot as plt
import numpy as np

# os.environ["CUDA_VISIBLE_DEVICES"] = "1"
torch.set_num_threads(1)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.cuda.empty_cache()
res = {'epoch': [], 'loss': [], 'dice': []}


def weights_init(m):
    classname = m.__class__.__name__
    # print(classname)
    if classname.find('Conv3d') != -1:
        init.xavier_normal(m.weight.data, 0.0)
        init.constant_(m.bias.data, 0.0)
    elif classname.find('Linear') != -1:
        init.xavier_normal(m.weight.data, 0.0)
        init.constant_(m.bias.data, 0.0)


# 参数 - 正式训练配置
rate = 0.50
learn_rate = 0.001
epochs = 50  # 正式训练：50个epoch
train_dataset_path = '../../src/train'  # 使用相对路径

# 获取数据 (train, val, test)
train_dataset, val_dataset, test_dataset = make.get_d1(train_dataset_path)

# 如果想用 val_dataset 做测试集监控，可以这样赋值
# train_dataset = train_dataset
# test_dataset = val_dataset 

unet = unet.Unet(1, 1).to(device).apply(weights_init)

# 使用 Dice Loss + BCE Loss (降低BCE权重)
criterion_bce = torch.nn.BCELoss().to(device)

def dice_loss_fn(pred, target, smooth=1.0):
    """Dice Loss for segmentation"""
    pred = pred.contiguous()
    target = target.contiguous()
    intersection = (pred * target).sum(dim=2).sum(dim=2)
    loss = 1 - ((2. * intersection + smooth) / (pred.sum(dim=2).sum(dim=2) + target.sum(dim=2).sum(dim=2) + smooth))
    return loss.mean()

optimizer = torch.optim.Adam(unet.parameters(), learn_rate)


def train():
    global res
    # Batch Size设为1以适应 3050 Laptop 4GB 显存
    dataloaders = DataLoader(train_dataset, batch_size=1, shuffle=True, num_workers=0)
    print(f"训练开始... (Steps: {len(dataloaders)})")
    
    for epoch in range(epochs):
        dt_size = len(dataloaders.dataset)
        epoch_loss, epoch_dice = 0, 0
        step = 0
        unet.train()
        
        for x, y in dataloaders:
            step += 1
            x = x[0].to(device)
            # y[1] 是 mask tensor
            target = y[1].to(device)
            if len(target.shape) == 3:
                target = target.unsqueeze(1) # [B, 1, H, W]
            
            optimizer.zero_grad()
            outputs = unet(x)
            
            # 组合损失: 降低BCE权重，强调Dice
            loss_bce = criterion_bce(outputs, target)
            loss_dice = dice_loss_fn(outputs, target)
            loss = 0.1 * loss_bce + 1.0 * loss_dice
            
            loss.backward()
            optimizer.step()
            
            # 计算 dice score
            with torch.no_grad():
                pred_bin = (outputs > 0.5).float()
                # 使用 dice_loss.dice 计算 Score
                curr_dice = dice_loss.dice(pred_bin.cpu().numpy(), target.cpu().numpy())
            
            epoch_loss += loss.item()
            epoch_dice += curr_dice

            # 每20步输出一次进度
            if step % 20 == 0:
                print("\rEpoch%d Step%d/%d | Loss:%.4f | Train Dice:%.4f" % (
                    epoch + 1, step, len(dataloaders), loss.item(), curr_dice), end='')
        
        # 每个 epoch 结束后打印统计
        avg_loss = epoch_loss / step
        avg_dice = epoch_dice / step
        print(f"\n{'='*60}")
        print(f"Epoch {epoch + 1}/{epochs} Complete | Avg Loss: {avg_loss:.4f} | Avg Dice: {avg_dice:.4f}")
        print(f"{'='*60}\n")
        
        # 保存模型
        torch.save(unet.state_dict(), '../model_weights.pth')
        
        # 简单测试
        # test()


def test():
    global res, img_y, mask_arrary
    epoch_dice = 0
    with torch.no_grad():
        dataloaders = DataLoader(test_dataset, batch_size=1, shuffle=True, num_workers=0)
        for x, mask in dataloaders:
            id = x[1:]  # ('1026',), ('10018',)]先病人号后片号
            x = x[0].to(device)
            y = unet(x)
            mask_arrary = mask[1].cpu().squeeze(0).detach().numpy()
            img_y = torch.squeeze(y).cpu().numpy()
            
            # 二值化预测结果
            img_y_binary = img_y.copy()
            img_y_binary[img_y_binary >= rate] = 1
            img_y_binary[img_y_binary < rate] = 0
            
            # 计算 Dice (使用0/1的二值图)
            epoch_dice += dice_loss.dice(img_y_binary, mask_arrary)
            
            # 如需保存可视化结果，使用 0/255
            # img_y_save = img_y_binary * 255
            # cv.imwrite(f'data/out/{mask[0][0]}-result.png', img_y_save, (cv.IMWRITE_PNG_COMPRESSION, 0))
        
        print('test dice %f' % (epoch_dice / len(dataloaders)))
        res['dice'].append(epoch_dice / len(dataloaders))


if __name__ == '__main__':
    train()
    test()
