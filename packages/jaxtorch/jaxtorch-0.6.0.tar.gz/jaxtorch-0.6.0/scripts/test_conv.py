import jax
import jax.numpy as jnp

def calc(image, x, y):
    (h, w) = image.shape
    def forward(image):
        out = jax.image.resize(image, (2*h, 2*w), method='lanczos3')
        return out[y, x]
    return jax.grad(forward)(image)

def calc_jac(image):
    (h, w) = image.shape
    def forward(image):
        out = jax.image.resize(image, (2*h, 2*w), method='lanczos3')
        return out
    return jax.jacrev(forward)(image)

def calc2(image, x, y, kernel):
    kernel = kernel.reshape(12,1) * kernel.reshape(1,12)
    (h, w) = image.shape
    def forward(image, kernel):
        out = jax.lax.conv_general_dilated(image.reshape(1,1,h,w), kernel.reshape(1,1,12,12),
                                           [1,1], padding=[(6,6),(6,6)], lhs_dilation=[2,2], rhs_dilation=None,
                                           dimension_numbers=('NCHW', 'IOHW', 'NCHW'))
        print(out.shape)
        return out[0,0,y,x]
    return jax.grad(forward)(image, kernel)

def calc2_jac(image, kernel):
    kernel = kernel.reshape(12,1) * kernel.reshape(1,12)
    (h, w) = image.shape
    def forward(image):
        out = jax.lax.conv_general_dilated(image.reshape(1,1,h,w), kernel.reshape(1,1,12,12),
                                           [1,1], padding=[(6,6),(6,6)], lhs_dilation=[2,2], rhs_dilation=None,
                                           dimension_numbers=('NCHW', 'IOHW', 'NCHW'))
        return out.reshape(2*h,2*w)
    return jax.jacrev(forward)(image)


def main():
    # extracted from grads of jax.image.resize
    even_filter = jnp.array([0.0073782638646662235, -0.06799723953008652, 0.2710106074810028, 0.8927707672119141, -0.13327467441558838, 0.03011229634284973])
    odd_filter = jnp.array([0.030112292617559433, -0.13327467441558838, 0.8927707076072693, 0.2710106074810028, -0.06799724698066711, 0.007378263399004936])
    combined = jnp.stack([even_filter, odd_filter], axis=1).reshape(12)

    image = jax.random.normal(jax.random.PRNGKey(0), [9,9])
    for y in range(18):
        for x in range(18):
            print(jnp.sum(calc2(image, x, y, combined)**2))

if __name__ == '__main__':
    main()