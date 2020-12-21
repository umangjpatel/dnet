from dnet.utils.tensor import Tensor
from typing import Tuple


def load_data() -> Tuple[Tensor, Tensor]:
    """Loads the binary tiny MNIST dataset (available on Google Colaboratory).
    :return: tuple consisting of training images and training labels
    """
    import pandas as pd
    import jax.numpy as jnp
    from jax import device_put
    from pathlib import Path

    path: Path = Path(__file__).parent
    train_data: pd.DataFrame = pd.read_csv(path / "train.csv", header=None)
    train_labels: Tensor = jnp.expand_dims(device_put(train_data[0].values), axis=1)
    train_images: Tensor = device_put(train_data.iloc[:, 1:].values) / 255.0
    return train_images, train_labels
