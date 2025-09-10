import sys
import jax
import jax.numpy as jnp
import random
import numpy as np
from PIL import Image

import jaxtorch

def pil_to_tensor(pil_image):
  img = np.array(pil_image).astype('float32')
  img = jnp.array(img) / 255
  img = img.rearrange('h w c -> c h w')
  return img

def pil_from_tensor(image):
  image = image.rearrange('c h w -> h w c')
  image = (image * 256).clamp(0, 255)
  image = np.array(image).astype('uint8')
  return Image.fromarray(image)

def loss(image):
    return 0.5 * jaxtorch.image.downsample2x(image, method='linear').square().sum() * 4

def main():
    [infile, outfile] = sys.argv[1:]
    image = pil_to_tensor(Image.open(infile)).unsqueeze(0)
    image = jax.grad(loss)(image).squeeze(0)
    pil_from_tensor(image).save(outfile)

if __name__ == '__main__':
    main()