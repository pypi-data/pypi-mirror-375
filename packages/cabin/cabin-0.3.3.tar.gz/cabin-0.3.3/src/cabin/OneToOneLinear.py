from __future__ import annotations

import torch
import torch.nn
from torch import Tensor
from torch.nn.parameter import Parameter


class OneToOneLinear(torch.nn.Module):

    __constants__ = ["features"]
    features: int
    weight: Tensor

    def __init__(
        self,
        features: int,
        scalefactor=None,
        weights=None,
        postroot=None,
        device=None,
        dtype=None,
    ) -> None:
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.features = features
        self.trainable_weights = weights is None or len(weights) != features
        if self.trainable_weights:
            if weights is None:
                print(
                    "This network will learn weights and biases, since no weights were supplied."
                )
            elif len(weights) != features:
                print(
                    f"This network will learn weights and biases, since num weights ({len(weights)}) does not match num features ({features})."
                )
            self.weight = Parameter(torch.empty(features, **factory_kwargs))
        else:
            self.register_buffer("weight", torch.tensor(weights))
        self.bias = Parameter(torch.empty(features, **factory_kwargs))
        self.activation_scale_factor = scalefactor
        self.post_product_root = postroot if postroot is not None else 1.0
        self.reset_parameters()

    def reset_parameters(self) -> None:
        if self.trainable_weights:
            bound = 1.0 / (self.features**0.5)
            torch.nn.init.uniform_(self.weight, -bound, bound)
        torch.nn.init.zeros_(self.bias)

    def get_cuts(self) -> Tensor:
        return -self.bias / self.weight

    def apply_cuts(self, inputs: Tensor) -> Tensor:
        # need to turn the "weights" vector into a matrix with the vector
        # elements on the diagonal, and zeroes everywhere else.
        targets = torch.matmul(inputs, torch.diag(self.weight)) + self.bias
        return targets

    def pass_cuts(self, inputs: Tensor) -> Tensor:
        t = self.apply_cuts(inputs)
        return torch.all(t > 0, dim=1)

    def forward(self, inputs: Tensor) -> Tensor:
        # apply the cuts
        targets = self.apply_cuts(inputs)

        # activation function
        targets = torch.sigmoid(self.activation_scale_factor * targets)

        # optionally take the root of the targets
        # had thought this might be a good way to reduce bias introduced
        # by taking the product of so many sigmoids, but this destroys
        # the good agreement we see between the "actual" efficiency
        # and the efficiency we calculate in the loss function.
        # so, for now, make sure post_product_root remains 1.0.
        targets = targets ** (1.0 / self.post_product_root)

        # this is differentiable, unlike using torch.all(torch.gt()) or something else that yields booleans.
        # will converge to 1 for things that pass all cuts, and to zero for things that fail any single cut.
        targets = torch.prod(targets, dim=1)

        return targets

    def extra_repr(self) -> str:
        return f"in_features={self.features}, bias={self.bias}"
