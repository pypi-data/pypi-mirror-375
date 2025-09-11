# This file is part of the pyMOR project (https://www.pymor.org).
# Copyright pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (https://opensource.org/licenses/BSD-2-Clause)

from pymor.core.config import config

config.require('TORCH')


import numpy as np
import torch
import torch.nn as nn

from pymor.core.base import BasicObject
from pymor.models.interface import Model
from pymor.operators.constructions import ZeroOperator
from pymor.vectorarrays.numpy import NumpyVectorSpace


class BaseNeuralNetworkModel(Model):
    """Base class for models that use artificial neural networks.

    This class implements the scaling methods for inputs and outputs/targets of
    neural networks.
    """

    def _scale_input(self, i):
        if (self.scaling_parameters.get('min_inputs') is not None
           and self.scaling_parameters.get('max_inputs') is not None):
            return ((torch.DoubleTensor(i) - self.scaling_parameters['min_inputs'])
                    / (self.scaling_parameters['max_inputs'] - self.scaling_parameters['min_inputs']))
        return i

    def _scale_target(self, i):
        if (self.scaling_parameters.get('min_targets') is not None
           and self.scaling_parameters.get('max_targets') is not None):
            return (torch.DoubleTensor(i) * (self.scaling_parameters['max_targets']
                                             - self.scaling_parameters['min_targets'])
                    + self.scaling_parameters['min_targets'])
        return i


class NeuralNetworkModel(BaseNeuralNetworkModel):
    """Class for models of stationary problems that use artificial neural networks.

    This class implements a |Model| that uses a neural network for solving.

    Parameters
    ----------
    neural_network
        The neural network that approximates the mapping from parameter space
        to solution space. Should be an instance of
        :class:`~pymor.models.neural_network.FullyConnectedNN` with input size that
        matches the (total) number of parameters and output size equal to the
        dimension of the reduced space.
    parameters
        |Parameters| of the reduced order model (the same as used in the full-order
        model).
    scaling_parameters
        Dict of tensors that determine how to scale inputs before passing them
        through the neural network and outputs after obtaining them from the
        neural network. If not provided or each entry is `None`, no scaling is
        applied. Required keys are `'min_inputs'`, `'max_inputs'`, `'min_targets'`,
        and `'max_targets'`.
    output_functional
        |Operator| mapping a given solution to the model output. In many applications,
        this will be a |Functional|, i.e. an |Operator| mapping to scalars.
        This is not required, however.
    products
        A dict of inner product |Operators| defined on the discrete space the
        problem is posed on. For each product with key `'x'` a corresponding
        attribute `x_product`, as well as a norm method `x_norm` is added to
        the model.
    error_estimator
        An error estimator for the problem. This can be any object with
        an `estimate_error(U, mu, m)` method. If `error_estimator` is
        not `None`, an `estimate_error(U, mu)` method is added to the
        model which will call `error_estimator.estimate_error(U, mu, self)`.
    visualizer
        A visualizer for the problem. This can be any object with
        a `visualize(U, m, ...)` method. If `visualizer`
        is not `None`, a `visualize(U, *args, **kwargs)` method is added
        to the model which forwards its arguments to the
        visualizer's `visualize` method.
    name
        Name of the model.
    """

    def __init__(self, neural_network, parameters={}, scaling_parameters={},
                 output_functional=None, products=None, error_estimator=None,
                 visualizer=None, name=None):

        super().__init__(products=products, error_estimator=error_estimator,
                         visualizer=visualizer, name=name)

        self.__auto_init(locals())
        self.solution_space = NumpyVectorSpace(neural_network.output_dimension)
        self.output_functional = output_functional or ZeroOperator(NumpyVectorSpace(0), self.solution_space)
        assert self.output_functional.source == self.solution_space
        self.dim_output = self.output_functional.range.dim

    def _compute(self, quantities, data, mu):
        if 'solution' in quantities:
            # convert the parameter `mu` into a form that is usable in PyTorch
            converted_input = torch.DoubleTensor(mu.to_numpy())
            converted_input = self._scale_input(converted_input)
            # obtain (reduced) coordinates by forward pass of the parameter values
            # through the neural network
            U = self.neural_network(converted_input).detach().numpy()
            U = self._scale_target(U)
            # convert plain numpy array to element of the actual solution space
            U = self.solution_space.make_array(U)
            data['solution'] = U
            quantities.remove('solution')

        super()._compute(quantities, data, mu=mu)


class NeuralNetworkStatefreeOutputModel(BaseNeuralNetworkModel):
    """Class for models of the output of stationary problems that use ANNs.

    This class implements a |Model| that uses a neural network for solving for the output
    quantity.

    Parameters
    ----------
    neural_network
        The neural network that approximates the mapping from parameter space
        to output space. Should be an instance of
        :class:`~pymor.models.neural_network.FullyConnectedNN` with input size that
        matches the (total) number of parameters and output size equal to the
        dimension of the output space.
    parameters
        |Parameters| of the reduced order model (the same as used in the full-order
        model).
    scaling_parameters
        Dict of tensors that determine how to scale inputs before passing them
        through the neural network and outputs after obtaining them from the
        neural network. If not provided or each entry is `None`, no scaling is
        applied. Required keys are `'min_inputs'`, `'max_inputs'`, `'min_targets'`,
        and `'max_targets'`.
    error_estimator
        An error estimator for the problem. This can be any object with
        an `estimate_error(U, mu, m)` method. If `error_estimator` is
        not `None`, an `estimate_error(U, mu)` method is added to the
        model which will call `error_estimator.estimate_error(U, mu, self)`.
    name
        Name of the model.
    """

    def __init__(self, neural_network, parameters={}, scaling_parameters={},
                 error_estimator=None, name=None):

        super().__init__(error_estimator=error_estimator, name=name)

        self.__auto_init(locals())

    def _compute(self, quantities, data, mu):
        if 'output' in quantities:
            converted_input = torch.from_numpy(mu.to_numpy()).double()
            converted_input = self._scale_input(converted_input)
            output = self.neural_network(converted_input).detach().numpy()
            output = self._scale_target(output)
            if isinstance(output, torch.Tensor):
                output = output.numpy()
            data['output'] = output.reshape((self.neural_network.output_dimension, 1))
            quantities.remove('output')

        super()._compute(quantities, data, mu=mu)


class NeuralNetworkInstationaryModel(BaseNeuralNetworkModel):
    """Class for models of instationary problems that use artificial neural networks.

    This class implements a |Model| that uses a neural network for solving.

    Parameters
    ----------
    T
        The final time T.
    nt
        The number of time steps.
    neural_network
        The neural network that approximates the mapping from parameter space
        to solution space. Should be an instance of
        :class:`~pymor.models.neural_network.FullyConnectedNN` with input size that
        matches the (total) number of parameters and output size equal to the
        dimension of the reduced space.
    parameters
        |Parameters| of the reduced order model (the same as used in the full-order
        model).
    scaling_parameters
        Dict of tensors that determine how to scale inputs before passing them
        through the neural network and outputs after obtaining them from the
        neural network. If not provided or each entry is `None`, no scaling is
        applied. Required keys are `'min_inputs'`, `'max_inputs'`, `'min_targets'`,
        and `'max_targets'`.
    output_functional
        |Operator| mapping a given solution to the model output. In many applications,
        this will be a |Functional|, i.e. an |Operator| mapping to scalars.
        This is not required, however.
    products
        A dict of inner product |Operators| defined on the discrete space the
        problem is posed on. For each product with key `'x'` a corresponding
        attribute `x_product`, as well as a norm method `x_norm` is added to
        the model.
    error_estimator
        An error estimator for the problem. This can be any object with
        an `estimate_error(U, mu, m)` method. If `error_estimator` is
        not `None`, an `estimate_error(U, mu)` method is added to the
        model which will call `error_estimator.estimate_error(U, mu, self)`.
    visualizer
        A visualizer for the problem. This can be any object with
        a `visualize(U, m, ...)` method. If `visualizer`
        is not `None`, a `visualize(U, *args, **kwargs)` method is added
        to the model which forwards its arguments to the
        visualizer's `visualize` method.
    name
        Name of the model.
    """

    def __init__(self, T, nt, neural_network, parameters={}, scaling_parameters={},
                 output_functional=None, products=None, error_estimator=None,
                 visualizer=None, name=None):

        super().__init__(products=products, error_estimator=error_estimator,
                         visualizer=visualizer, name=name)

        self.__auto_init(locals())
        self.solution_space = NumpyVectorSpace(neural_network.output_dimension)
        output_functional = output_functional or ZeroOperator(NumpyVectorSpace(0), self.solution_space)
        assert output_functional.source == self.solution_space
        self.dim_output = output_functional.range.dim

    def _compute(self, quantities, data, mu):
        if 'solution' in quantities:
            # collect all inputs in a single tensor
            inputs = self._scale_input(torch.DoubleTensor(np.array([mu.at_time(t).to_numpy()
                                                                    for t in np.linspace(0., self.T, self.nt)])))
            # pass batch of inputs to neural network
            result = self.neural_network(inputs).detach().numpy()
            result = self._scale_target(result)
            # convert result into element from solution space
            data['solution'] = self.solution_space.make_array(result.T)
            quantities.remove('solution')

        super()._compute(quantities, data, mu=mu)


class NeuralNetworkInstationaryStatefreeOutputModel(BaseNeuralNetworkModel):
    """Class for models of the output of instationary problems that use ANNs.

    This class implements a |Model| that uses a neural network for solving for the output
    quantity in the instationary case.

    Parameters
    ----------
    T
        The final time T.
    nt
        The number of time steps.
    neural_network
        The neural network that approximates the mapping from parameter space
        to output space. Should be an instance of
        :class:`~pymor.models.neural_network.FullyConnectedNN` with input size that
        matches the (total) number of parameters and output size equal to the
        dimension of the output space.
    parameters
        |Parameters| of the reduced order model (the same as used in the full-order
        model).
    scaling_parameters
        Dict of tensors that determine how to scale inputs before passing them
        through the neural network and outputs after obtaining them from the
        neural network. If not provided or each entry is `None`, no scaling is
        applied. Required keys are `'min_inputs'`, `'max_inputs'`, `'min_targets'`,
        and `'max_targets'`.
    error_estimator
        An error estimator for the problem. This can be any object with
        an `estimate_error(U, mu, m)` method. If `error_estimator` is
        not `None`, an `estimate_error(U, mu)` method is added to the
        model which will call `error_estimator.estimate_error(U, mu, self)`.
    name
        Name of the model.
    """

    def __init__(self, T, nt, neural_network, parameters={}, scaling_parameters={},
                 error_estimator=None, name=None):

        super().__init__(error_estimator=error_estimator, name=name)

        self.__auto_init(locals())

    def _compute(self, quantities, data, mu):
        if 'output' in quantities:
            inputs = self._scale_input(torch.DoubleTensor(np.array([mu.at_time(t).to_numpy()
                                                                    for t in np.linspace(0., self.T, self.nt)])))
            outputs = self.neural_network(inputs).detach().numpy()
            outputs = self._scale_target(outputs)
            if isinstance(outputs, torch.Tensor):
                outputs = outputs.numpy()
            assert outputs.shape == (self.nt, self.neural_network.output_dimension)
            data['output'] = outputs.T
            quantities.remove('output')

        super()._compute(quantities, data, mu=mu)


class FullyConnectedNN(nn.Module, BasicObject):
    """Class for neural networks with fully connected layers.

    This class implements neural networks consisting of linear and fully connected layers.
    Furthermore, the same activation function is used between each layer, except for the
    last one where no activation function is applied.

    Parameters
    ----------
    layer_sizes
        List of sizes (i.e. number of neurons) for the layers of the neural network.
    activation_function
        Function to use as activation function between the single layers.
    """

    def __init__(self, layer_sizes, activation_function=torch.tanh):
        super().__init__()

        if layer_sizes is None or not len(layer_sizes) > 1 or not all(size >= 1 for size in layer_sizes):
            raise ValueError

        self.input_dimension = layer_sizes[0]
        self.output_dimension = layer_sizes[-1]

        self.layers = nn.ModuleList()
        self.layers.extend([nn.Linear(int(layer_sizes[i]), int(layer_sizes[i+1]))
                            for i in range(len(layer_sizes) - 1)])

        self.activation_function = activation_function

        if not self.logging_disabled:
            self.logger.info(f'Architecture of the neural network:\n{self}')

    def forward(self, x):
        """Performs the forward pass through the neural network.

        Applies the weights in the linear layers and passes the outcomes to the
        activation function.

        Parameters
        ----------
        x
            Input for the neural network.

        Returns
        -------
        The output of the neural network for the input x.
        """
        for i in range(len(self.layers) - 1):
            x = self.activation_function(self.layers[i](x))
        return self.layers[len(self.layers)-1](x)


class LongShortTermMemoryNN(nn.Module, BasicObject):
    """Class for Long Short-Term Memory neural networks (LSTMs).

    This class implements neural networks for time series of input data of arbitrary length.
    The same LSTMCell is applied in each timestep and the hidden state of the former LSTMCell
    is used as input hidden state for the next cell.

    Parameters
    ----------
    input_dimension
        Dimension of the input (at a fixed time instance) of the LSTM.
    hidden_dimension
        Dimension of the hidden state of the LSTM.
    output_dimension
        Dimension of the output of the LSTM (must be smaller than `hidden_dimension`).
    number_layers
        Number of layers in the LSTM (if greater than 1, a stacked LSTM is used).
    """

    def __init__(self, input_dimension, hidden_dimension=10, output_dimension=1, number_layers=1):
        assert input_dimension > 0
        assert hidden_dimension > 0
        assert output_dimension > 0
        assert hidden_dimension > output_dimension
        assert number_layers > 0

        super().__init__()
        self.__auto_init(locals())

        self.lstm = nn.LSTM(input_dimension, hidden_dimension, num_layers=number_layers,
                            proj_size=output_dimension, batch_first=True).double()

        self.logger.info(f'Architecture of the neural network:\n{self}')

    def forward(self, x):
        """Performs the forward pass through the neural network.

        Initializes the hidden and cell states and applies the weights of the LSTM layers
        followed by the output layer that maps from the hidden state to the output state.

        Parameters
        ----------
        x
            Input for the neural network.

        Returns
        -------
        The output of the neural network for the input x.
        """
        # perform forward pass through LSTM and return the result
        output, _ = self.lstm(x)
        return output
