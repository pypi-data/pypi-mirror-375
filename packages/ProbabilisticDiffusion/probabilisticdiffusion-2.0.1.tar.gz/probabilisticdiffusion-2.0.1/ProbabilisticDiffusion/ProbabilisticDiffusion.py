import torch
import torch.nn as nn
import math
from .utils import get_beta_schedule, preserve_zeros
from torch.nn.modules.loss import _Loss as tLoss
from torch.optim import Optimizer
import matplotlib.pyplot as plt
from tqdm import tqdm
from typing import Union, Tuple


class Diffusion:
    def __init__(self, data: torch.tensor, num_diffusion_timesteps: int,
                 beta_start: int, beta_end: int, schedule: str,
                 model: nn.Module, loss_fn: tLoss,
                 optimizer: Optimizer):
        """
        :param data: Torch tensor data, NxD dimension where N = number of data points, D = dimension of data
        :type data: torch.tensor
        :param num_diffusion_timesteps: Number of timesteps in diffusion model
        :type num_diffusion_timesteps: int
        :param beta_start: Starting value of the beta parameter as specified in the DDPM algorithm
        :type beta_start: int
        :param beta_end: Ending value of the beta parameter as specified in the DDPM algorithm
        :type beta_end: int
        :param schedule: Schedule type for beta, at each timestep, accepts 'linear', 'quad', 'warmup10', 'warmup50',
        'const', 'jsd'
        :type schedule: str
        :param model: PyTorch model to be trained by the DDPM training procedure to learn the reverse diffusion
        :type model: torch.nn.Module
        :param loss_fn: PyTorch loss function to be minimized, in DDPM case it is SSE but MSE will equivalently minimize
        :type loss_fn: torch.nn.modules.loss._Loss
        :param optimizer: Gradient based optimizer method used to minimize loss
        :type optimizer: torch.optim.Optimizer
        """
        self.data = data
        self.model = model
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.T = num_diffusion_timesteps
        betas = get_beta_schedule(schedule, beta_start=beta_start, beta_end=beta_end,
                                  num_diffusion_timesteps=num_diffusion_timesteps)
        self.alphas = 1-torch.tensor(betas, dtype=self.data.dtype)
        self.alpha_bar = torch.cumprod(self.alphas, 0)

    def train(self, batch_size: int, epochs: int, plot_loss: bool = True, sig_fig: int = 3):
        """
        :param batch_size: Batch size for training
        :type batch_size: int
        :param epochs: Number of training epochs
        :type epochs: int
        :param plot_loss: Flag on whether to plot loss at the end of training or not
        :type plot_loss: bool
        :param sig_fig: Number of significant figures to include in the loss displayed on TQDM progress bar
        :type sig_fig: int
        :return: None
        :rtype: None
        """
        n = len(self.data)
        batch_in_epoch = math.ceil(n/batch_size)
        if plot_loss:
            losses = []
        with tqdm(range(epochs)) as tepoch:
            for epoch in tepoch:
                possible_indx = torch.tensor(range(0, n), dtype=torch.float)
                for batch in range(batch_in_epoch):
                    self.optimizer.zero_grad()
                    # Batch Sample
                    sample_size = min(batch_size, len(possible_indx))
                    x0_ind = torch.multinomial(possible_indx, sample_size)
                    # Updating Possible Index Choices After Sampling Without Replacement
                    possible_indx = torch.tensor([i for i in possible_indx if i not in x0_ind])
                    x0 = self.data[x0_ind]
                    t = torch.randint(0, self.T, size=(sample_size // 2 + 1,))
                    t = torch.cat([t, self.T - t - 1], dim=0)[:sample_size].long()
                    alpha_t_bars = self.alpha_bar[t].reshape((-1, 1))
                    z = torch.randn_like(x0)
                    # Set Up Inputs
                    inputs = torch.sqrt(alpha_t_bars) * x0 + torch.sqrt(1 - alpha_t_bars) * z
                    model_outputs = self.model(inputs, t)
                    # Loss Calculations
                    loss = self.loss_fn(model_outputs, z)
                    tqdm_loss = preserve_zeros(loss.item(), sig_fig)
                    tepoch.set_postfix(loss=tqdm_loss)
                    if plot_loss:
                        losses.append(loss.detach().numpy())
                    # Backwards Step
                    loss.backward()
                    self.optimizer.step()
        if plot_loss:
            x_ax = range(0, len(losses))
            plt.plot(x_ax, losses)
            plt.xlabel('Batch Iteration')
            plt.ylabel('Batch Loss')
            plt.show()
            
    @torch.no_grad()
    def forward(self, t: int, plot: bool = True, plot_idx: Tuple[int, int] = (0, 1), **kwargs):
        """
        :param t: Timestep to move forward in the diffusion process to
        :type t: int
        :param plot: Plotting flag for diffused data
        :type plot: bool
        :param plot_idx: 2D Indices of desired dimensions of data to plot on x-y plot
        :type plot_idx: Tuple[int, int]
        :param kwargs: Keyword args for matplotlib plot parameters
        :type kwargs: **kwargs
        :return: Diffused data
        :rtype: torch.tensor
        """
        d = self.data.shape[1]
        if plot:
            assert len(plot_idx) == 2, 'Specified Plot Axes are not 2d, cannot plot'
        alpha_bar = self.alpha_bar[t]
        cov = (1-alpha_bar)
        samples = []
        for i in range(d):
            d_data = self.data[:, i]
            mu_t = d_data*torch.sqrt(alpha_bar)
            samples.append(torch.normal(mu_t, cov))
        data_t = torch.stack(samples, dim=1)
        if plot:
            plt.scatter(data_t[:, plot_idx[0]], data_t[:, plot_idx[1]], **kwargs)
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.title(f'Samples At Time {t}')
            plt.show()
        return data_t

    @torch.no_grad()
    def sample(self, n: int, plot_intervals: Union[None, int] = None, plot_idx: Tuple[int, int] = (0, 1),
               keep: Union[None, str, Tuple[int]] = None, **kwargs):
        """
        :param n: Number of new samples to generate
        :type n: int
        :param plot_intervals: Intervals at which to plot, can either be None to not plot, or integer
        :type plot_intervals: Union[None, int]
        :param plot_idx: 2D Indices of desired dimensions of data to plot on x-y plot
        :type plot_idx: Tuple[int, int]
        :param keep: Timesteps at which to keep the new sampled data, accepts, 'all', 'last', or a list of desired
                     timesteps to keep
        :type keep: Union[None, str, Tuple[int]]
        :param kwargs: Keyword args for matplotlib plot parameters
        :type kwargs: **kwargs
        :return: Array torch tensors containing new sampled data points at the specified timesteps to keep
        :rtype: List[torch.tensor]
        """
        if plot_intervals:
            assert plot_intervals > 0, 'Plot Intervals Must Be Greater Than 0'
            assert len(plot_idx) == 2, '2D plotting only, specify 2 columns to plot only'
        x_t = torch.randn((n, self.data.shape[1]))
        x = None
        if keep == 'all':
            x = [x_t]
        elif type(keep) is tuple or type(keep) is list:
            x = []
        for t in range(self.T-1, -1, -1):
            z = torch.randn_like(x_t)
            a_t = self.alphas[t].reshape((-1, 1))
            a_bar_t = self.alpha_bar[t].reshape((-1, 1))
            sigma_t = torch.sqrt(1-a_t)
            s_theta = self.model(x_t, torch.tensor([t]))
            mean = (1 / torch.sqrt(a_t)) *\
                   (x_t - ((1 - a_t) / torch.sqrt(1 - a_bar_t) * s_theta))
            x_t = mean + sigma_t * z
            if keep == 'all':
                x.append(x_t)
            elif type(keep) is tuple or type(keep) is list:
                if t in keep:
                    x.append(x_t)
            if plot_intervals:
                if (t % plot_intervals) == 0:
                    plt.scatter(x_t[:, plot_idx[0]], x_t[:, plot_idx[1]], **kwargs)
                    plt.xlabel('X')
                    plt.ylabel('Y')
                    plt.title('Samples At Time ' + str(t))
                    plt.show()
        if keep == 'last':
            x = x_t
        return x
