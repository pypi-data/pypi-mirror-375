from torch.utils.data import Dataset
import torch
import numpy as np


class TransformerData(Dataset):
  def __init__(self, X, window_size=20, stride=20, device="cuda"):
    self.X = torch.tensor(X, dtype=torch.float32).permute(0, 2, 1).to(device)  # (768, 313, 20)
    self.window_size = window_size
    self.stride = stride
    self.n_files = self.X.shape[0]  # 728
    self.n_datapoints = self.X.shape[1]  # 313
    self.n_features = self.X.shape[2]  # 20

    self.windows_per_file = 0
    start = 0
    while start + window_size <= self.n_datapoints:
      self.windows_per_file += 1
      start += stride
    self.total_windows = self.n_files * self.windows_per_file  

  def __len__(self):
    return self.total_windows 

  def __getitem__(self, idx):
    file_idx = idx // self.windows_per_file  
    window_idx = idx % self.windows_per_file 
    start = window_idx * self.stride
    end = start + self.window_size
    if end > self.n_datapoints:
      raise IndexError("Tentativa de acessar janela incompleta")
    window = self.X[file_idx, start:end, :] 
    return window