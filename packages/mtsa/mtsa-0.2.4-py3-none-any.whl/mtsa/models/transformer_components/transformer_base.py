import torch
import torch.nn as nn
import time
from torch.utils.data import DataLoader
from mtsa.models.transformer_components.positional_encoding import PositionalEncoding
from mtsa.models.transformer_components.encoder_layer import EncoderLayer
from mtsa.models.transformer_components.decoder_layer import DecoderLayer
from mtsa.models.transformer_components.transformer_layout_data import TransformerData

class TransformerBase(nn.Module):
  def __init__(self, input_dim, d_model, nhead, num_layers, d_ff, max_seq_length, dropout, logger, device):
    super().__init__()
    self.device = device
    self.logger = logger
    self.d_model=d_model
    self.max_seq_len=max_seq_length
    self.src_linear_input = nn.Linear(input_dim, d_model).to(device)
    self.tgt_linear_input = nn.Linear(input_dim, d_model).to(device)
    self.model_output = nn.Linear(d_model, input_dim).to(device)

    self.positional_encoding = PositionalEncoding(d_model, max_seq_length, dropout).to(device)

    self.encoder_layers = nn.ModuleList(
        [EncoderLayer(d_model, nhead, d_ff, dropout) for _ in range(num_layers)]
    ).to(device)
    self.decoder_layers = nn.ModuleList(
        [DecoderLayer(d_model, nhead, d_ff, dropout) for _ in range(num_layers)]
    ).to(device)

    self.dropout1 = nn.Dropout(dropout).to(device)
    self.dropout2 = nn.Dropout(dropout).to(device)


  def generate_mask(self, tgt, device):
    seq_length = tgt.size(1)
    nopeak_mask = (1 - torch.triu(torch.ones(1, seq_length, seq_length), diagonal=1)).bool().to(device)
    return nopeak_mask

  def forward(self, src, tgt):
    src = self.src_linear_input(src)
    tgt = self.tgt_linear_input(tgt)

    src = self.positional_encoding(src)
    tgt = self.positional_encoding(tgt)

    src = self.dropout1(src)
    tgt = self.dropout2(tgt)
    tgt_m = self.generate_mask(tgt, self.device)

    enc_output = src
    for enc_layer in self.encoder_layers:
      enc_output = enc_layer(enc_output, mask=None)

    dec_output = tgt
    for dec_layer in self.decoder_layers:
      dec_output = dec_layer(dec_output, enc_output, src_mask=None, tgt_mask=None)

    output = self.model_output(dec_output)
    return output

  def fit(self, X, y=None, batch_size=32, epochs=15, learning_rate=0.001, shuffle=True):
    self.batch_size = batch_size
    self.epochs = epochs
    self.learning_rate = learning_rate
    self.shuffle = shuffle

    dataset = TransformerData(X=X, window_size=self.max_seq_len, stride=self.max_seq_len, device=self.device)
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

    self.train_criterion_reconstruction = nn.MSELoss()
    self.train_optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate, betas=(0.9, 0.98), eps=1e-9)
    self.__train_loop(train_loader, epochs)

  def __train_loop(self, train_loader, epochs):
    for epoch in range(epochs):
      self.train()
      total_loss = 0.0
      start_time = time.time()

      for inputs in train_loader:
        outputs = self(inputs, inputs)
        loss = self.train_criterion_reconstruction(outputs, inputs)

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

  def predict(self, X):
    pass
  
  def __score_wave_data(self, X):
    self.eval()
    dataset = TransformerData(X, window_size=self.max_seq_len, stride=self.max_seq_len, device=self.device)
    batch_size = dataset.windows_per_file  
    val_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    scores = []
    with torch.no_grad():
      for inputs in val_loader:
        outputs = self(inputs, inputs) 
        mse = torch.mean(torch.square(inputs - outputs), dim=(1, 2)) 
        scores.append(mse)
    
    scores = torch.cat(scores, dim=0)  
    score = torch.mean(scores).item() 
    if self.logger is not None:
      self.logger.log("test_loss_per_file", -score)
    return -score  


