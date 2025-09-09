import importlib.resources
import torch
from dropper.model import Dropper
"""
"""
def load_dropper() -> Dropper:
    """
    Trains a dropper model with preexisting parameters.
    :return: A trained Dropper model
    """
    with  importlib.resources.path('dropper', 'dropper.pth') as path:
        model = Dropper()
        model.load_state_dict(torch.load(path))
        return model