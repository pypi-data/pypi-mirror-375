import torch
import torch.nn as nn
from sklearn.base import BaseEstimator, OutlierMixin
from mtsa.models.transformer_components.transformer_base import TransformerBase
from sklearn.pipeline import FeatureUnion, Pipeline
from mtsa.features.mel import Array2Mfcc
from mtsa.features.stats import StatisticalSignalDescriptors
from mtsa.utils import Wav2Array
import numpy as np

class Transformer(nn.Module, BaseEstimator, OutlierMixin):
  def __init__(self, 
               input_dim=20,
               d_model=512,
               nhead=8,
               num_layers=3,
               d_ff=2048,
               max_seq_length=15,
               dropout=0.1,
               sampling_rate=16000,
               mono=True,
               use_array2mfcc=True,
               use_array2melspec=None,
               use_features_union=None,
               is_for_wave_data=True,
               device="cuda",
               n_fft=1024,
               hop_length=512,
               n_mels=64,
               frames=5,
               power=2.0,
               logger=None,
               ):
    super().__init__()
    self.input_dim=input_dim
    self.d_model=d_model
    self.nhead=nhead
    self.num_layers=num_layers
    self.d_ff=d_ff
    self.max_seq_length=max_seq_length
    self.dropout=dropout
    self.sampling_rate=sampling_rate
    self.mono=mono
    self.use_array2mfcc=use_array2mfcc
    self.use_array2melspec=use_array2melspec
    self.use_features_union=use_features_union
    self.is_for_wave_data=is_for_wave_data
    self.device=device
    self.n_fft=n_fft
    self.hop_length=hop_length
    self.n_mels=n_mels
    self.frames=frames
    self.power=power

    self.final_model = TransformerBase(
      input_dim=self.input_dim, d_model=self.d_model, nhead=self.nhead, 
      num_layers=self.num_layers, d_ff=self.d_ff, max_seq_length=self.max_seq_length,
      dropout=self.dropout, logger=logger, device=self.device
    ).to(device)

    self.model=self._build_model()

  def fit(self, X, y=None, batch_size=32, epochs=30, learning_rate=0.0001):
    return self.model.fit(
      X,
      y,
      final_model__batch_size=batch_size,
      final_model__epochs=epochs,
      final_model__learning_rate=learning_rate,
    )
  
  def score_samples(self, X):
    return np.array(
      list(
        map(
          self.model.score_samples, 
          [[x] for x in X])
        )
      )
  
  def predict(self, X):
    return np.array(
      list(
        map(
          self.model.score_samples, 
          [[x] for x in X])
        )
      )

  def _build_model(self):
    wav2array = Wav2Array(sampling_rate=self.sampling_rate, mono=self.mono)

    steps = [("wav2array", wav2array)]
    
    if self.use_array2mfcc:
      steps.append(("array2mfcc", Array2Mfcc(sampling_rate=self.sampling_rate)))
    
    if self.use_features_union:
      steps.append(("features", FeatureUnion(StatisticalSignalDescriptors)))

    steps.append(("final_model", self.final_model))

    return Pipeline(steps=steps)

    