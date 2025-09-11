from torch.optim.optimizer import Optimizer
from .dsgd import DSgd
from .lscaffold import LScaffold


def load_optimizer(key: str, path: str, org_optimizer: Optimizer, parameters, inner_loop: int = 10, eta: float=0.1):
    if key == "lscaffold":
        optimizer = LScaffold(path, org_optimizer, parameters, inner_loop)
    else:
        optimizer = DSgd(path, org_optimizer, parameters, inner_loop)
    return optimizer


__all__ = [
    "load_optimizer",
    "DSgd",
    "LScaffold",
]
