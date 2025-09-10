#!/usr/bin/env python
import torch
from torch import nn
from torch.nn import functional as F
from torch.profiler import profile, record_function, ProfilerActivity

class Downsample2d(nn.Module):
    def __init__(self):
        super().__init__()
        weight = torch.tensor([[1, 3, 3, 1]]) / 8
        self.register_buffer('weight', (weight.T @ weight)[None, None])

    def forward(self, input):
        n, c, h, w = input.shape
        input = F.pad(input, (1, 1, 1, 1), 'replicate')
        return F.conv2d(input, self.weight.repeat([c, 1, 1, 1]), stride=2, groups=c)

class Upsample2d(nn.Module):
    def __init__(self, method):
        super().__init__()
        weight = torch.tensor([[1, 3, 3, 1]]) / 4
        self.register_buffer('weight', (weight.T @ weight)[None, None])
        self.method = method

    def forward(self, input):
        n, c, h, w = input.shape
        if self.method == 'conv_transpose2d':
            input = F.pad(input, (1, 1, 1, 1), 'replicate') # F.conv_transpose2d
            return F.conv_transpose2d(input, self.weight.repeat([c, 1, 1, 1]), stride=2, padding=3, groups=c)
        elif self.method == 'conv2d_input':
            input = F.pad(input, (1, 1, 1, 1), 'replicate') # F.conv_transpose2d
            return nn.grad.conv2d_input([n, c, 2*h, 2*w], self.weight.repeat([c, 1, 1, 1]), stride=2, padding=3, groups=c, grad_output=input)
        elif self.method == 'manual':
            input = torch.stack([input, torch.zeros_like(input)], dim=4).reshape(n, c, h, 2*w)
            input = torch.stack([input, torch.zeros_like(input)], dim=3).reshape(n, c, 2*h, 2*w)
            input = F.pad(input, (1, 2, 1, 2), 'replicate')
            return F.conv2d(input, self.weight.repeat([c, 1, 1, 1]), stride=1, padding=0, groups=c)

class UpsampleWithGrad(nn.Module):
    def __init__(self):
        super().__init__()
        self.down = Downsample2d()

    def forward(self, input):
        n, c, h, w = input.shape
        dummy = torch.zeros((n, c, 2*h, 2*w), device=input.device, dtype=input.dtype)
        dummy.requires_grad_()
        out = self.down(dummy)
        return torch.autograd.grad(out, dummy, grad_outputs=input)[0]*4

if __name__ == '__main__':
    device = torch.device('cuda:0')
    # image = TF.to_tensor(Image.open('test.png')).unsqueeze(0).repeat(1,64,1,1).to(device)
    image = torch.rand(1, 512, 512, 512).to(device)

    print('Torch version:', torch.__version__)

    print('Comparison')
    out = Upsample2d(method='conv_transpose2d').to(device)(image).squeeze(0)[:1, :10, :10]
    out2 = Upsample2d(method='manual').to(device)(image).squeeze(0)[:1, :10, :10]
    print((out - out2).abs().max())
    exit()

    print('=== manual method ===')
    upsample = Upsample2d(method='manual').to(device)
    print('Initial run to warm the cache')
    out = upsample(image)
    print(out.shape)

    print('Profiling...')
    with profile(activities=[ProfilerActivity.CUDA], record_shapes=True) as prof:
        with record_function("upsample"):
            out = upsample(image)
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

    print('=== conv_transpose2d method ===')
    upsample = Upsample2d(method='conv_transpose2d').to(device)
    print('Initial run to warm the cache')
    out = upsample(image)

    print('Profiling...')
    with profile(activities=[ProfilerActivity.CUDA], record_shapes=True) as prof:
        with record_function("upsample"):
            out = upsample(image)
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

    print('=== conv2d_input method ===')
    upsample = Upsample2d(method='conv2d_input').to(device)
    print('Initial run to warm the cache')
    out = upsample(image)
    print('Profiling...')
    with profile(activities=[ProfilerActivity.CUDA], record_shapes=True) as prof:
        with record_function("upsample"):
            out = upsample(image)
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

    print('=== Downsample (gradient) ===')

    downsample = Downsample2d().to(device)
    image = torch.rand(1, 512, 1024, 1024).to(device)
    image.requires_grad_()

    print('Initial run to warm the cache')
    out = 0.5 * downsample(image).square().sum()
    grad = torch.autograd.grad(out, image)[0]
    print('Profiling downsample gradient')
    out = 0.5 * downsample(image).square().sum()
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True) as prof:
        with record_function("backward"):
            grad = torch.autograd.grad(out, image)[0]
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

    print('=== gradient method ===')
    image = torch.rand(1, 512, 512, 512).to(device)

    upsample = UpsampleWithGrad().to(device)
    print('Initial run to warm the cache')
    out = upsample(image)
    print('Profiling gradient method')
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True) as prof:
        with record_function("backward"):
            out = upsample(image)
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))
