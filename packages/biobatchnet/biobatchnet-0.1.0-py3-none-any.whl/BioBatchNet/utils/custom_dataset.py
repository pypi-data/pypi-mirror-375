"""
Custom dataset for API usage
"""
import torch
from torch.utils.data import Dataset
import numpy as np

class CustomIMCDataset(Dataset):
    """Dataset for custom IMC data from API"""
    
    def __init__(self, data, batch_info):
        super().__init__()
        
        # Convert to tensors
        if isinstance(data, np.ndarray):
            self.features = torch.FloatTensor(data)
        else:
            self.features = data
            
        # Process batch info
        if isinstance(batch_info, np.ndarray) and batch_info.dtype.kind in ['U', 'S', 'O']:
            # String labels - convert to numeric
            unique_batches = np.unique(batch_info)
            batch_to_id = {b: i for i, b in enumerate(unique_batches)}
            self.batch_labels = torch.LongTensor([batch_to_id[b] for b in batch_info])
            self.num_batches = len(unique_batches)
        elif isinstance(batch_info, list):
            # List of labels
            if isinstance(batch_info[0], str):
                unique_batches = list(set(batch_info))
                batch_to_id = {b: i for i, b in enumerate(unique_batches)}
                self.batch_labels = torch.LongTensor([batch_to_id[b] for b in batch_info])
                self.num_batches = len(unique_batches)
            else:
                self.batch_labels = torch.LongTensor(batch_info)
                self.num_batches = len(torch.unique(self.batch_labels))
        else:
            # Already numeric
            self.batch_labels = torch.LongTensor(batch_info)
            self.num_batches = len(torch.unique(self.batch_labels))
        
        # Placeholder for cell types (not used in training)
        self.cell_types = torch.zeros(len(self.features), dtype=torch.long)
        
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.batch_labels[idx], self.cell_types[idx]


class CustomGeneDataset(Dataset):
    """Dataset for custom scRNA-seq data from API"""
    
    def __init__(self, data, batch_info):
        super().__init__()
        
        # Convert to tensors
        if isinstance(data, np.ndarray):
            self.features = torch.FloatTensor(data)
        else:
            self.features = data
            
        # Process batch info
        if isinstance(batch_info, (list, np.ndarray)):
            unique_batches = np.unique(batch_info)
            batch_to_id = {b: i for i, b in enumerate(unique_batches)}
            self.batch_labels = torch.LongTensor([batch_to_id[b] for b in batch_info])
            self.num_batches = len(unique_batches)
        else:
            self.batch_labels = torch.LongTensor(batch_info)
            self.num_batches = len(torch.unique(self.batch_labels))
        
        # Placeholder for cell types
        self.cell_types = torch.zeros(len(self.features), dtype=torch.long)
        
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.batch_labels[idx], self.cell_types[idx]