import itertools
from typing import List, Dict, Callable, Generator, Iterator, Tuple

import jax.numpy as tensor
from jax import grad
from tqdm import tqdm

from dnet.dataloaders import DataLoader


class Trainer:

    def __init__(self, model: Dict):
        for k, v in model.items():
            self.__dict__[k] = v
        self.data_loader: DataLoader = DataLoader(self.inputs, self.targets, self.bs)
        self.batches: Generator = self.data_loader.load_batch()
        self.opt_init, self.opt_update, self.get_params = self.optimizer(self.lr)
        self.training_cost: List[float] = []
        self.validation_cost: List[float] = []
        self.training_accuracy: List[float] = []
        self.validation_accuracy: List[float] = []

    def get_weights(self) -> List[Dict[str, tensor.array]]:
        return [layer.params for layer in self.layers]

    def compute_accuracy(self, params: List[Dict[str, tensor.array]],
                         batch: Tuple[tensor.array, tensor.array], trainable: bool = True) -> float:
        inputs, targets = batch
        outputs = self.compute_predictions(params, inputs, trainable)
        return self.evaluator(outputs, targets)

    def compute_cost(self, params: List[Dict[str, tensor.array]],
                     batch: Tuple[tensor.array, tensor.array], trainable: bool = True) -> float:
        inputs, targets = batch
        outputs: tensor.array = self.compute_predictions(params, inputs, trainable)
        return self.loss(outputs, targets)

    def compute_predictions(self, params: List[Dict[str, tensor.array]], inputs: tensor.array,
                            trainable: bool) -> tensor.array:
        for param, layer in zip(params, self.layers):
            inputs = layer.forward(param, inputs, trainable)
        return inputs

    def opt_update_params(self, i: int, opt_state: Callable, batch: Tuple[tensor.array, tensor.array]) -> Callable:
        params: List[Dict[str, tensor.array]] = self.get_params(opt_state)
        return self.opt_update(i, grad(self.compute_cost)(params, batch), opt_state)

    def update_layer_params(self, params: List[Dict[str, tensor.array]]) -> None:
        for param, layer in zip(params, self.layers): layer.update_params(param)

    def train(self) -> None:
        parameters: List[Dict[str, tensor.array]]
        self.opt_state: Callable = self.opt_init(self.get_weights())
        count: Iterator[int] = itertools.count()
        for epoch in range(self.epochs):
            for _ in tqdm(range(self.data_loader.num_batches), desc=f"Epoch {epoch + 1} : "):
                self.opt_state = self.opt_update_params(next(count), self.opt_state, next(self.batches))
            parameters = self.get_params(self.opt_state)
            self.update_training_metrics(parameters)
            self.update_validation_metrics(parameters)
        self.update_layer_params(parameters)

    def update_validation_metrics(self, parameters):
        self.validation_cost.append(
            self.compute_cost(params=parameters, batch=(self.val_inputs, self.val_targets), trainable=False))
        self.validation_accuracy.append(
            self.compute_accuracy(parameters, (self.val_inputs, self.val_targets), trainable=False))

    def update_training_metrics(self, parameters):
        self.training_cost.append(self.compute_cost(params=parameters, batch=(self.inputs, self.targets)))
        self.training_accuracy.append(self.compute_accuracy(params=parameters, batch=(self.inputs, self.targets)))
