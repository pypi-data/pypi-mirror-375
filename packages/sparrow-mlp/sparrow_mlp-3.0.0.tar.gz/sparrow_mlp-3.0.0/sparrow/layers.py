# sparrow/layers.py

import torch
import torch.nn as nn
import torch.nn.functional as F

class Expert(nn.Module):
    """یک متخصص (Expert) که یک شبکه عصبی کوچک است."""
    def __init__(self, input_size, output_size, hidden_size=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

    def forward(self, x):
        return self.net(x)

class MoELayer(nn.Module):
    """یک لایه که شامل چندین متخصص و یک مسیریاب محلی برای انتخاب بین آنهاست."""
    def __init__(self, num_experts, input_size, output_size, expert_hidden_size):
        super().__init__()
        self.num_experts = num_experts
        self.experts = nn.ModuleList([
            Expert(input_size, output_size, expert_hidden_size) for _ in range(num_experts)
        ])
        self.router = nn.Linear(input_size, num_experts)

    def forward(self, x):
        router_logits = self.router(x)
        gates = F.gumbel_softmax(router_logits, hard=True, dim=-1)
        expert_outputs = torch.stack([expert(x) for expert in self.experts], dim=1)
        gated_output = torch.bmm(gates.unsqueeze(1), expert_outputs).squeeze(1)
        return gated_output