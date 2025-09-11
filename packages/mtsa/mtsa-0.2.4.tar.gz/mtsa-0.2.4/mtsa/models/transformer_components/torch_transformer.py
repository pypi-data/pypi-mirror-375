import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from mtsa.models.transformer_components.transformer_layout_data import TransformerData
from torch.utils.data import DataLoader
import time


class TorchTransformerModel(nn.Module):
  def __init__(self, 
               input_dim=20, 
               d_model=512, 
               nhead=8, 
               max_seq_length=20, 
               num_encoder_layers=3, 
               num_decoder_layers=3, 
               d_ff=2048, 
               dropout=0.2, 
               device="cuda",
               logger=None
               ):
    super(TorchTransformerModel, self).__init__()
    self.logger=logger
    self.max_seq_length=max_seq_length
    self.device=device
    self.linear_input = nn.Linear(input_dim, d_model).to(device)
    self.tgt_linear_input = nn.Linear(input_dim, d_model).to(device)

    self.model_output = nn.Linear(d_model, input_dim).to(device)

    self.pos_encoder_src = PositionalEncoding(d_model, dropout, max_seq_length)
    self.pos_encoder_tgt = PositionalEncoding(d_model, dropout, max_seq_length)
    self.dropout1 = nn.Dropout(dropout).to(device)
    self.dropout2 = nn.Dropout(dropout).to(device)
    
    self.transformer = nn.Transformer(
      d_model=d_model, 
      nhead=nhead, 
      num_encoder_layers=num_encoder_layers, 
      num_decoder_layers=num_decoder_layers,
      dim_feedforward=d_ff,
      dropout=dropout,
      batch_first=True
    ).to(device)

  def forward(self, X):
    X = self.linear_input(X)
    X = self.pos_encoder_src(X)
    X = self.dropout1(X)
    transformer_output = self.transformer(X, X)
    output = self.model_output(transformer_output)
    return output
  
  def fit(self, X, y=None, batch_size=32, epochs=15, learning_rate=0.0001, shuffle=False):
    self.batch_size=batch_size
    self.epochs=epochs
    self.learning_rate=learning_rate
    self.shuffle=shuffle

    self.train_criterion_reconstruction = nn.MSELoss()
    self.train_optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)

    dataset = TransformerData(X, device=self.device)
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

    self._train_loop(train_loader, epochs)
  
  def _train_loop(self, train_loader, epochs):
    for epoch in range(epochs):
      self.train()
      total_loss = 0.0
      start_time = time.time()

      for inputs in train_loader:
        inputs = inputs.to(self.device)
        outputs = self(inputs)
        loss = self.train_criterion_reconstruction(inputs, outputs)

        self.train_optimizer.zero_grad()
        loss.backward()
        self.train_optimizer.step()

        total_loss += loss.item()

      avg_loss = total_loss / len(train_loader)
      elapsed_time = time.time() - start_time
      print(f"Epoch {epoch + 1}/{epochs} | avg_loss: {avg_loss:.4f} | Time: {elapsed_time:.2f}s")

      if self.logger is not None:
        self.logger.log("train_loss", avg_loss)
        
  def score_samples(self, X):
    return self.__score_wave_data(X=X)

  def __score_wave_data(self, X):
    self.eval()
    dataset = TransformerData(X, device=self.device)
    # Usar batch_size = windows_per_file para processar todas as janelas de uma vez
    batch_size = dataset.windows_per_file  
    val_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    scores = []
    with torch.no_grad():
      for inputs in val_loader:
        outputs = self(inputs) 
        mse = torch.mean(torch.square(inputs - outputs), dim=(1, 2)) 
        scores.append(mse)
    
    # Concatenar e calcular média
    scores = torch.cat(scores, dim=0)  
    score = torch.mean(scores).item()  # Float
    print(-score)
    return -score  



class PositionalEncoding(nn.Module):
  def __init__(self, d_model, dropout=0.1, max_len=5000):
    super(PositionalEncoding, self).__init__()
    self.dropout = nn.Dropout(p=dropout)

    pe = torch.zeros(max_len, d_model)
    position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
    div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-torch.log(torch.tensor(10000.0)) / d_model))
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    pe = pe.unsqueeze(0)
    self.register_buffer('pe', pe)

  def forward(self, x):
    x = x + self.pe[:, :x.size(1), :]
    return self.dropout(x)

