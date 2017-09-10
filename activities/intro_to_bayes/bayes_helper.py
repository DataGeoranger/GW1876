import numpy as np
import matplotlib.pyplot as plt
import pyemu

def gaussian_multiply(mu1,std1,mu2,std2):
    var1,var2 = std1**2,std2**2
    mean = (var1*mu2 + var2*mu1) / (var1 + var2)
    variance = (var1 * var2) / (var1 + var2)
    return mean, np.sqrt(variance)


def plot_posterior(prior_mean, prior_std, likeli_mean, likeli_std, legend=True):
    plt.figure()

    post_mean, post_std = gaussian_multiply(prior_mean, prior_std, likeli_mean, likeli_std)

    xs, ys = pyemu.helpers.gaussian_distribution(prior_mean, prior_std)
    plt.plot(xs, ys, color='k', ls='--', lw=2.0, label='prior')

    xs, ys = pyemu.helpers.gaussian_distribution(likeli_mean, likeli_std)
    plt.plot(xs, ys, color='g', ls='--', lw=2.0, label='likelihood')

    xs, ys = pyemu.helpers.gaussian_distribution(post_mean, post_std)
    plt.fill_between(xs, 0, ys, label='posterior', color='b', alpha=0.25)
    if legend:
        plt.legend();
    ax = plt.gca()
    ax.set_xlabel("hk ($\\frac{m}{d}$)")
    plt.show()