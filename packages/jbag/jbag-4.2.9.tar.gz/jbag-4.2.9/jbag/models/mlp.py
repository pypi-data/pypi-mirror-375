from typing import Union, Sequence, Type

from torch import nn


class MLP(nn.Sequential):
    def __init__(self, in_dims, hidden_dims: Union[int, Sequence[int]], out_dims: int = None,
                 norm_op: Union[None, Type[nn.Module]] = None,
                 norm_op_kwargs: dict = None,
                 non_linear: Union[None, Type[nn.Module]] = None,
                 non_linear_kwargs: dict = None,
                 p_dropout: float = 0.1):
        if isinstance(hidden_dims, int):
            hidden_dims = [hidden_dims]

        if norm_op_kwargs is None:
            norm_op_kwargs = {}
        if non_linear_kwargs is None:
            non_linear_kwargs = {}

        dims = [in_dims] + hidden_dims + ([] if out_dims is None else [out_dims])
        layers = []

        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            if i < len(dims) - 2 or out_dims is None:
                if norm_op is not None:
                    layers.append(norm_op(dims[i + 1], **norm_op_kwargs))
                if non_linear is not None:
                    layers.append(non_linear(**non_linear_kwargs))
                if p_dropout > 0:
                    layers.append(nn.Dropout(p=p_dropout))
        super().__init__(*layers)
