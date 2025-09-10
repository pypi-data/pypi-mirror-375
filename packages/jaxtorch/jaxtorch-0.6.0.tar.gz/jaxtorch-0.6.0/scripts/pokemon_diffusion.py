import random
import math
import os
from tqdm import tqdm, trange
from matplotlib import pyplot as plt
from PIL import Image
import traceback

import numpy as np
import jax
import jax.numpy as jnp
import optax

import jaxtorch
from jaxtorch import Module, PRNG, Context, ParamState
from jaxtorch import nn, init
import wandb

# For data loading.
from torchvision import datasets, transforms, utils
from torchvision.transforms import functional as TF
import torch.utils.data
import torch

# Define the model (a residual U-Net)

class ResidualBlock(nn.Module):
    def __init__(self, main, skip=None):
        super().__init__()
        self.main = nn.Sequential(*main)
        self.skip = skip if skip else nn.Identity()

    def forward(self, cx, input):
        return self.main(cx, input) + self.skip(cx, input)


class ResConvBlock(ResidualBlock):
    def __init__(self, c_in, c_mid, c_out):
        skip = None if c_in == c_out else nn.Conv2d(c_in, c_out, 1, bias=False)
        super().__init__([
            nn.Conv2d(c_in, c_mid, 3, padding=1),
            nn.Dropout2d(p=0.1),
            nn.ReLU(),
            nn.Conv2d(c_mid, c_out, 3, padding=1),
            nn.ReLU(),
        ], skip)


class SkipBlock(nn.Module):
    def __init__(self, main, skip=None):
        super().__init__()
        self.main = nn.Sequential(*main)
        self.skip = skip if skip else nn.Identity()

    def forward(self, cx, input):
        return jnp.concatenate([self.main(cx, input), self.skip(cx, input)], axis=1)


class FourierFeatures(nn.Module):
    def __init__(self, in_features, out_features, std=1.):
        super().__init__()
        assert out_features % 2 == 0
        self.weight = init.normal(out_features // 2, in_features, stddev=std)

    def forward(self, cx, input):
        f = 2 * math.pi * input @ cx[self.weight].T
        return jnp.concatenate([f.cos(), f.sin()], axis=-1)


def expand_to_planes(input, shape):
    return input[..., None, None].broadcast_to(input.shape[:2] + shape[2:])


class Diffusion(nn.Module):
    def __init__(self):
        super().__init__()
        c = 64  # The base channel count

        # The inputs to timestep_embed will approximately fall into the range
        # -10 to 10, so use std 0.2 for the Fourier Features.
        self.timestep_embed = FourierFeatures(1, 16, std=0.2)
        self.class_embed = nn.Embedding(10, 4)

        self.net = nn.Sequential(
            ResConvBlock(3 + 16 + 4, c, c),
            ResConvBlock(c, c, c),
            SkipBlock([
                nn.image.Downsample2d(),  # 64x64 -> 32x32
                ResConvBlock(c, c * 2, c * 2),
                ResConvBlock(c * 2, c * 2, c * 2),
                SkipBlock([
                    nn.image.Downsample2d(),  # 32x32 -> 16x16
                    ResConvBlock(c * 2, c * 2, c * 2),
                    ResConvBlock(c * 2, c * 2, c * 2),
                    SkipBlock([
                        nn.image.Downsample2d(),  # 16x16 -> 8x8
                        ResConvBlock(c * 2, c * 2, c * 2),
                        ResConvBlock(c * 2, c * 2, c * 2),
                        ResConvBlock(c * 2, c * 2, c * 2),
                        ResConvBlock(c * 2, c * 2, c * 2),
                        nn.image.Upsample2d(),
                    ]),
                    ResConvBlock(c * 4, c * 2, c * 2),
                    ResConvBlock(c * 2, c * 2, c * 2),
                    nn.image.Upsample2d(),
                ]),
                ResConvBlock(c * 4, c * 2, c * 2),
                ResConvBlock(c * 2, c * 2, c),
                nn.image.Upsample2d(),            # Haven't implemented ConvTranpose2d yet.
            ]),
            ResConvBlock(c * 2, c, c),
            ResConvBlock(c, c, 3),
        )

    def forward(self, cx, input, log_snrs, cond):
        timestep_embed = expand_to_planes(self.timestep_embed(cx, log_snrs[:, None]), input.shape)
        class_embed = expand_to_planes(self.class_embed(cx, cond), input.shape)
        return self.net(cx, jnp.concatenate([input, class_embed, timestep_embed], axis=1))

# Define the noise schedule

def get_ddpm_schedule(t):
    """Returns log SNRs for the noise schedule from the DDPM paper."""
    return -jnp.expm1(1e-4 + 10 * t**2).log()


def get_alphas_sigmas(log_snrs):
    """Returns the scaling factors for the clean image and for the noise, given
    the log SNR for a timestep."""
    alphas_squared = jax.nn.sigmoid(log_snrs)
    sigmas_squared = jax.nn.sigmoid(-log_snrs)
    return alphas_squared.sqrt(), sigmas_squared.sqrt()

# Visualize the noise schedule

def visualize():
    plt.rcParams['figure.dpi'] = 100

    t_vis = jnp.linspace(0, 1, 1000)
    log_snrs_vis = get_ddpm_schedule(t_vis)
    alphas_vis, sigmas_vis = get_alphas_sigmas(log_snrs_vis)

    print('The noise schedule:')

    plt.plot(t_vis, alphas_vis, label='alpha (signal level)')
    plt.plot(t_vis, sigmas_vis, label='sigma (noise level)')
    plt.legend()
    plt.xlabel('timestep')
    plt.grid()
    plt.show()

    plt.plot(t_vis, log_snrs_vis, label='log SNR')
    plt.legend()
    plt.xlabel('timestep')
    plt.grid()
    plt.show()

# visualize()

# Prepare the dataset

batch_size = 50

tf = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5]),
])

class PokemonDataset(torch.utils.data.Dataset):
    def __init__(self):
        import glob
        self.filenames = glob.glob('/mnt/data2/data/pokemon/gen3/flipped/*.png')
        self.filenames.sort()
        # self.filenames = self.filenames[:10] * 500

    def __len__(self):
        return len(self.filenames)
    def __getitem__(self, i):
        filename = self.filenames[i]
        image = Image.open(filename).convert('RGB')
        image = tf(image)
        return (image, torch.tensor(0))

# train_set = datasets.MNIST('data', download=True, transform=tf)
train_set = PokemonDataset()
train_dl = torch.utils.data.DataLoader(train_set, batch_size, shuffle=True, num_workers=4)


# Create the model and optimizer

# Seed for grid sampling
seed = 0
train_seed = 1

print('Using device:', jax.devices())
rng = PRNG(jax.random.PRNGKey(train_seed))

model = Diffusion()
params = model.init_weights(rng.split())
params_ema = params.clone()
print('Model parameters:', sum(np.prod(p.shape) for p in params.values.values()))

optimizer = optax.adam(1e-4)
opt_state = optimizer.init(params)
epoch = 0

# Saving the optimizer state is kind of annoying...  opt_state is some
# sort of arbitrary object containing pytrees of the same kind as
# `params`, that is ParamState objects containing the per-parameter
# states, like momentum. We need to convert each ParamState in the opt
# state to the portable named parameter dictionary, then convert it
# back when loading.  Maybe there's a better design where ParamState
# is indexed by the portable parameter names all along and hence
# doesn't need conversion?
class StateDict(dict):
    pass

def opt_state_dict(model, opt_state):
    def todict(x):
        if isinstance(x, ParamState):
            return StateDict(model.state_dict(x))
        return x
    return jax.tree_util.tree_map(todict, opt_state, is_leaf=lambda c: isinstance(c, ParamState))

def load_opt_state_dict(model, state_dict, opt_state):
    def load(x, base):
        if isinstance(x, StateDict):
            px = base.clone()
            model.load_state_dict(px, x, strict=False)
            return px
        return x
    return jax.tree_util.tree_map(load, state_dict, opt_state, is_leaf=lambda x: isinstance(x, StateDict))

# Load checkpoint
if os.path.exists('pokemon_diffusion.pth'):
    state_dict = jaxtorch.pt.load('pokemon_diffusion.pth')
    model.load_state_dict(params, state_dict['model'], strict=False)
    model.load_state_dict(params_ema, state_dict['model_ema'], strict=False)
    opt_state = load_opt_state_dict(model, state_dict['opt'], opt_state)
    epoch = state_dict['epoch']


# Actually train the model

ema_decay = 0.998

# The number of timesteps to use when sampling
steps = 250

# The amount of noise to add each timestep when sampling
# 0 = no noise (DDIM)
# 1 = full noise (DDPM)
eta = 1.

def compute_loss(params, reals, classes, key):
    rng = PRNG(key)
    # Draw uniformly distributed continuous timesteps
    t = jax.random.uniform(rng.split(), [reals.shape[0]])

    # Calculate the noise schedule parameters for those timesteps
    log_snrs = get_ddpm_schedule(t)
    alphas, sigmas = get_alphas_sigmas(log_snrs)

    # Combine the ground truth images and the noise
    alphas = alphas[:, None, None, None]
    sigmas = sigmas[:, None, None, None]
    noise = jax.random.normal(rng.split(), reals.shape)
    noised_reals = reals * alphas + noise * sigmas

    cx = Context(params, rng.split()).train_mode_()
    # Compute the model output and the loss. The model outputs the predicted
    # Gaussian noise. It is conditioned on the noise level parameterized
    # as log SNR, which is independent of the specific schedule.
    eps = model(cx, noised_reals, log_snrs, classes)
    loss = (eps - noise).square().mean()
    return loss
compute_grads = jax.jit(jax.value_and_grad(compute_loss))

@jax.jit
def eval_model(params, xs, ts, classes, key):
    cx = Context(params, key).eval_mode_()
    return model(cx, xs, ts, classes)

def train():
    global params, params_ema, opt_state
    for i, (reals, classes) in enumerate(tqdm(train_dl)):
        reals = jnp.array(reals)
        classes = jnp.array(classes)

        loss, grads = compute_grads(params, reals, classes, rng.split())

        updates, opt_state = optimizer.update(grads, opt_state)
        params = optax.apply_updates(params, updates)

        this_decay = 0.95 if epoch < 10 else ema_decay
        params_ema = jax.tree_util.tree_map(lambda p, m: p * (1 - this_decay) + m * this_decay, params, params_ema)

        if i % 50 == 0:
            tqdm.write(f'Epoch: {epoch}, iteration: {i}, loss: {loss}')
        wandb.log({'loss': loss.item(), 'epoch': epoch})


def demo():
    tqdm.write('Sampling...')
    rng = PRNG(jax.random.PRNGKey(seed))

    fakes = jax.random.normal(rng.split(), [100, 3, 64, 64])
    fakes_classes = jnp.array([0] * 100)#jnp.arange(10).reshape([10,1]).broadcast_to([10,10]).reshape([100])
    ts = jnp.ones([100])

    # Create the noise schedule
    t = jnp.linspace(1, 0, steps + 1)[:-1]
    log_snrs = get_ddpm_schedule(t)
    alphas, sigmas = get_alphas_sigmas(log_snrs)

    # The sampling loop
    for i in trange(steps):

        # Get the model output (eps, the predicted noise)
        eps = eval_model(params_ema, fakes, ts * log_snrs[i], fakes_classes, rng.split())

        # Predict the denoised image
        pred = (fakes - eps * sigmas[i]) / alphas[i]

        # If we are not on the last timestep, compute the noisy image for the
        # next timestep.
        if i < steps - 1:
            # If eta > 0, adjust the scaling factor for the predicted noise
            # downward according to the amount of additional noise to add
            ddim_sigma = eta * (sigmas[i + 1]**2 / sigmas[i]**2).sqrt() * (1 - alphas[i]**2 / alphas[i + 1]**2).sqrt()
            adjusted_sigma = (sigmas[i + 1]**2 - ddim_sigma**2).sqrt()

            # Recombine the predicted noise and predicted denoised image in the
            # correct proportions for the next step
            fakes = pred * alphas[i + 1] + eps * adjusted_sigma

            # Add the correct amount of fresh noise
            if eta:
                fakes += jax.random.normal(rng.split(), fakes.shape) * ddim_sigma

        # If we are on the last timestep, output the denoised image
        else:
            fakes = pred

    grid = utils.make_grid(torch.tensor(np.array(fakes)), 10).cpu()
    filename = f'demo_{epoch:05}.png'
    TF.to_pil_image(grid.add(1).div(2).clamp(0, 1)).save(filename)
    print(f'Saved {filename}')
    # display.display(display.Image(filename))
    tqdm.write('')

def save():
    filename = 'pokemon_diffusion.pth'
    obj = {
        'model': model.state_dict(params),
        'model_ema': model.state_dict(params_ema),
        'opt': opt_state_dict(model, opt_state),
        'epoch': epoch,
    }
    jaxtorch.pt.save(obj, filename + '~')
    os.rename(filename + '~', filename)


try:
    demo()
    wandb.init(project='diffusion-pokemon', entity='nshepperd') #, resume=True
    while True:
        print('Epoch', epoch)
        train()
        tqdm.write('')
        epoch += 1
        demo()
        save()
except KeyboardInterrupt:
    pass
