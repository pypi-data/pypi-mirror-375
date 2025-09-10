import jax
import jax.numpy as jnp
import random

import jaxtorch

def compute_upscale_filter(method, h=9,w=9):
    image = jax.random.normal(jax.random.PRNGKey(0), (h,w))
    def forward(image):
        out = jax.image.resize(image, (2*h, 2*w), method=method)
        return out
    even = jax.jacfwd(forward)(image)[8,8].sum(axis=0)
    odd = jax.jacfwd(forward)(image)[9,9].sum(axis=0)
    even = even[even!=0]
    odd = odd[odd!=0]
    combined = jnp.stack([even, odd], axis=1).reshape(2*even.shape[0])
    print(even, odd)
    return combined

def trim(x):
    return x[x!=0]

def compute_downscale_filter(method, h=40,w=40):
    image = jax.random.normal(jax.random.PRNGKey(0), (h,w))
    def forward(image):
        out = jax.image.resize(image, (h//2, w//2), method=method)
        return out
    jacobian = jax.jacfwd(forward)(image)
    kernel = trim(jacobian[10,10].sum(axis=0))
    return kernel

def main():
    print(compute_downscale_filter('lanczos3').tolist())
    exit()

    [n,c,h,w] = [1,1,10,10]
    image = jax.random.normal(jax.random.PRNGKey(0), [n,c,h,w])
    print(jax.image.resize(image, (1, c, h//2, w//2), method='linear') - jaxtorch.image.downsample2x(image, method='linear'))

if __name__ == '__main__':
    main()