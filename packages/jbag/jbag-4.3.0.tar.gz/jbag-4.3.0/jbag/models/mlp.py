from typing import Union, Optional, Callable, Any, Dict

from torch import nn


class MLP(nn.Sequential):
    def __init__(self, in_dims, hidden_dims: Union[int, list[int], tuple[int]], out_dims: Optional[int] = None,
                 norm_op: Optional[Callable[..., nn.Module]] = None,
                 norm_op_kwargs: Optional[Dict[str, Any]] = None,
                 non_linear: Optional[Callable[..., nn.Module]] = None,
                 non_linear_kwargs: Optional[Dict[str, Any]] = None,
                 dropout: float = 0.1,
                 dropout_kwargs: Optional[Dict[str, Any]] = None):
        if isinstance(hidden_dims, int):
            hidden_dims = [hidden_dims]

        if norm_op_kwargs is None:
            norm_op_kwargs = {}
        if non_linear_kwargs is None:
            non_linear_kwargs = {}
        if dropout_kwargs is None:
            dropout_kwargs = {}

        layers = []

        for each_hidden_dims in hidden_dims:
            layers.append(nn.Linear(in_dims, each_hidden_dims))
            if norm_op is not None:
                layers.append(norm_op(each_hidden_dims, **norm_op_kwargs))
            if non_linear is not None:
                layers.append(non_linear(**non_linear_kwargs))
            if dropout > 0:
                layers.append(nn.Dropout(p=dropout, **dropout_kwargs))
            in_dims = each_hidden_dims
        if out_dims is not None:
            layers.append(nn.Linear(in_dims, out_dims))
        super().__init__(*layers)
