from .modules import *
from .VampPrior.vampprior import VampEncoder
from torch import nn
import torch.nn.functional as F
import torch
import numpy as np
import torch.optim as optim
from torch.utils.data import DataLoader

class IMCVAE(nn.Module):
    def __init__(self, **args):
        super(IMCVAE, self).__init__()

        for key, value in args.items():
            setattr(self, key, value)

        self.bio_encoder = BaseEncoder(self.in_sz, self.bio_encoder_hidden_layers, self.latent_sz)
        self.batch_encoder = BaseEncoder(self.in_sz, self.batch_encoder_hidden_layers, self.latent_sz)
        self.decoder = BaseDecoder(2 * self.latent_sz, self.decoder_hidden_layers, self.out_sz)
        self.bio_classifier = BaseClassifier(self.latent_sz, self.batch_classifier_layers_power, self.num_batch)
        self.batch_classifier = BaseClassifier(self.latent_sz, self.batch_classifier_layers_weak, self.num_batch)
        
        self.alpha = 1
        self.grl = GRL(alpha=self.alpha)

    def forward(self, x):  
        # bio information 
        bio_z, mu1, logvar1 = self.bio_encoder(x)

        # batch information
        batch_z, batch_mu, batch_logvar = self.batch_encoder(x)

        # combine information
        z_combine = torch.cat([bio_z, batch_z.detach()], dim=1)

        # adversarial
        bio_z_grl = self.grl(bio_z)
        bio_batch_pred = self.bio_classifier(bio_z_grl)

        # classifier
        batch_batch_pred = self.batch_classifier(batch_z)

        # reconstruction
        reconstruction = self.decoder(z_combine)

        return bio_z, mu1, logvar1, batch_z, batch_mu, batch_logvar, bio_batch_pred, batch_batch_pred, reconstruction
    
    def fit(self, data, batch_info, epochs=100, lr=1e-3, batch_size=256, loss_weights=None):
        """Train model using full Trainer with all losses"""
        from ..utils.trainer import Trainer
        from ..parse_config import ConfigParser
        from torch.utils.data import DataLoader, TensorDataset
        
        # Create dataset
        data_tensor = torch.FloatTensor(data) if not isinstance(data, torch.Tensor) else data
        batch_tensor = torch.LongTensor(batch_info) if not isinstance(batch_info, torch.Tensor) else batch_info
        dataset = TensorDataset(data_tensor, batch_tensor)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Create minimal config for Trainer
        config = {
            'name': 'api_training',
            'eval_sampling_seed': [42],
            'trainer': {
                'epochs': epochs,
                'save_dir': './temp_training',
                'save_period': 100,
                'verbosity': 1,
                'early_stop': 100,
                'if_imc': True,
                'skip_intermediate_eval': True,
                'sampling_fraction': {'api_training': 1.0}
            },
            'loss_weights': loss_weights or {
                'recon_loss': 10,
                'discriminator': 0.3,
                'classifier': 1,
                'mmd_loss_1': 0,
                'kl_loss_1': 0.005,
                'kl_loss_2': 0.1,
                'ortho_loss': 0.01
            }
        }
        
        config_parser = ConfigParser(config)
        optimizer = optim.Adam(self.parameters(), lr=lr)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.1)
        
        trainer = Trainer(
            config=config_parser,
            model=self,
            optimizer=optimizer,
            train_dataloader=dataloader,
            eval_dataloader=dataloader,
            scheduler=scheduler,
            device=next(self.parameters()).device,
            seed=42
        )
        
        trainer.train()
        
    def get_bio_embeddings(self, data):
        self.eval()
        with torch.no_grad():
            if isinstance(data, np.ndarray):
                data = torch.FloatTensor(data)
            bio_z, _, _ = self.bio_encoder(data)
            return bio_z.cpu().numpy()
            
    def correct_batch_effects(self, data):
        self.eval()
        with torch.no_grad():
            if isinstance(data, np.ndarray):
                data = torch.FloatTensor(data)
            bio_z, _, _ = self.bio_encoder(data)
            batch_z, _, _ = self.batch_encoder(data)
            z_combine = torch.cat([bio_z, batch_z.detach()], dim=1)
            reconstruction = self.decoder(z_combine)
            return reconstruction.cpu().numpy()
        
class GeneVAE(nn.Module):
    def __init__(self, **args):
        super(GeneVAE, self).__init__()

        for key, value in args.items():
            setattr(self, key, value)

        self.bio_encoder = BaseEncoder(self.in_sz, self.bio_encoder_hidden_layers, self.latent_sz)
        self.batch_encoder = BaseEncoder(self.in_sz, self.batch_encoder_hidden_layers, self.latent_sz)
        self.size_encoder = BaseEncoder(self.in_sz, self.bio_encoder_hidden_layers, 1)
        
        self.decoder = BaseDecoder(2 * self.latent_sz, self.decoder_hidden_layers, out_sz=1000)
        self.mean_decoder = nn.Sequential(nn.Linear(1000,  self.out_sz), MeanAct())  
        self.dispersion_decoder = nn.Sequential(nn.Linear(1000,  self.out_sz), DispAct())
        self.dropout_decoder = nn.Sequential(nn.Linear(1000,  self.out_sz), nn.Sigmoid())

        self.bio_classifier = BaseClassifier(self.latent_sz, self.batch_classifier_layers_power, self.num_batch)
        self.batch_classifier = BaseClassifier(self.latent_sz, self.batch_classifier_layers_weak, self.num_batch)

        self.alpha = 1
        self.grl = GRL(alpha=self.alpha)

    def forward(self, x): 
        # bio information 
        bio_z, mu1, logvar1 = self.bio_encoder(x)
        logvar1 = torch.clamp(logvar1, min=-5, max=5)
        size_factor, size_mu, size_logvar = self.size_encoder(x)
        # clamp size_logvar to avoid extremely large values that could lead to numerical overflow / NaNs
        size_logvar = torch.clamp(size_logvar, min=-5, max=5)

        # batch information
        batch_z, batch_mu, batch_logvar = self.batch_encoder(x)
        # clamp batch_logvar as well
        batch_logvar = torch.clamp(batch_logvar, min=-5, max=5)

        # combine information
        z_combine = torch.cat([bio_z, batch_z.detach()], dim=1)

        # adversarial
        bio_z_grl = self.grl(bio_z)
        bio_batch_pred = self.bio_classifier(bio_z_grl)
        
        # classifier
        batch_batch_pred = self.batch_classifier(batch_z)

        # zinb 
        h = self.decoder(z_combine)
        size_factor = torch.clamp(size_factor, min=-5, max=5)
        _mean = self.mean_decoder(h) * torch.exp(size_factor)
        _mean = torch.clamp(_mean, 1e-6, 1e8)

        _disp = self.dispersion_decoder(h)
        _pi = self.dropout_decoder(h)
        _pi = torch.clamp(_pi, 1e-6, 1.0 - 1e-6)

        return bio_z, mu1, logvar1, batch_z, batch_mu, batch_logvar, bio_batch_pred, batch_batch_pred, _mean, _disp, _pi, size_factor, size_mu, size_logvar
        
class MeanAct(nn.Module):
    def __init__(self):
        super(MeanAct, self).__init__()

    def forward(self, x):
        return torch.clamp(torch.exp(x), min=1e-3, max=1e3)

class DispAct(nn.Module):
    def __init__(self):
        super(DispAct, self).__init__()

    def forward(self, x):
        return torch.clamp(F.softplus(x), min=1e-3, max=1e3)