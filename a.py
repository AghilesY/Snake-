import torch
import os
# Charger les poids pré-entraînés à partir du fichier "model.pth"
model_path = "./model/model/model.pth"
if os.path.exists(model_path):
    checkpoint = torch.load(model_path)
    model_state_dict = {
        'linear1.weight': checkpoint['linear1.weight'],
        'linear1.bias': checkpoint['linear1.bias'],
        'linear2.weight': checkpoint['linear2.weight'],
        'linear2.bias': checkpoint['linear2.bias']
        }
    print(model_state_dict['linear1.weight'])