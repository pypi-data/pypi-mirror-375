# sparrow/models.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from .layers import MoELayer

class DynamicMLP(nn.Module):
    """
    یک پرسپترون چندلایه دینامیک با قابلیت رد کردن لایه‌ها (layer skipping)
    و انتخاب متخصص (expert selection) در هر لایه.
    """
    def __init__(self, input_size, output_size, hidden_dim, num_hidden_layers, num_experts, expert_hidden_size):
        super().__init__()
        self.num_hidden_layers = num_hidden_layers
        
        self.input_layer = nn.Linear(input_size, hidden_dim)
        
        self.hidden_layers = nn.ModuleList()
        for _ in range(num_hidden_layers):
            self.hidden_layers.append(
                MoELayer(num_experts, hidden_dim, hidden_dim, expert_hidden_size)
            )
            
        self.layer_router = nn.Linear(hidden_dim, num_hidden_layers)
        self.output_layer = nn.Linear(hidden_dim, output_size)
        self.layer_gates_values = None

    def forward(self, x):
        x = F.relu(self.input_layer(x))
        
        layer_gates_logits = self.layer_router(x)
        layer_gates = torch.sigmoid(layer_gates_logits)
        
        if self.training:
            self.layer_gates_values = layer_gates.mean(dim=0)

        for i, layer in enumerate(self.hidden_layers):
            gate = layer_gates[:, i].unsqueeze(1)
            # استفاده از اتصال باقی‌مانده (residual connection) برای رد کردن لایه
            x = x + gate * layer(x)

        return self.output_layer(x)