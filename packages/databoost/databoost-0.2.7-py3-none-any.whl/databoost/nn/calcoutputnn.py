def calculate_output_nn(input_layer, hidden_layers, output_layer):
  """
    Computes the output of a very simplified feedforward neural network.

    Parameters
    ----------
    input_layer : list of float
        Numerical values for the input neurons.
    
    hidden_layers : list of [layer_index, weight, bias]
        Each element represents one hidden neuron.
        - layer_index : int
            Indicates which hidden layer the neuron belongs to (0 = first hidden layer).
        - weight : float
            Weight applied to inputs from the previous layer.
        - bias : float
            Bias of the neuron.
        During processing, the computed value will also be appended as a fourth element.

    output_layer : list of [weight, bias]
        Defines the neurons in the output layer.
        - weight : float
            Weight applied to inputs from the last hidden layer.
        - bias : float
            Bias of the neuron.
        During processing, the computed value will also be appended as a third element.


    Returns
    -------
    output : list of float
        A list containing the final computed values of the output neurons.


    Example:
    --------
    >>> calculate_output_nn(
            input_layer=[2, 5], # input values
            hidden_layers=[[0, 1, 1], [0, 2, 3], # layer, weight, bias
                          [1, 2, 4], [1, 4, 2], # layer, weight, bias
                          [2, 1, 1], [2, 4, 2]], # layer, weight, bias
            output_layer=[[1, 2], [6, 2], [0, 1]] # weight, bias
        )
    """

  layers_list = []
  for elem in hidden_layers:
    layers_list.append(elem[0])
  layer_count = max(layers_list) - min(layers_list) + 1
  layers_list = [i for i in range(layer_count)]

  for i in layers_list:
    picked_layer = [t for t in hidden_layers if t[0] == i]

    if i == layers_list[0]: # è il primo
      previous_layer = input_layer
      for elem in picked_layer:
        values = [value*elem[1] for value in previous_layer]
        elem.append(sum(values)+elem[2])
        
    else:
      previous_layer = [t for t in hidden_layers if t[0] == i-1]
      for elem in picked_layer:
        values = [value[-1]*elem[1] for value in previous_layer]
        elem.append(sum(values)+elem[2])


  output = []
  for elem in output_layer:
    previous_layer = [t for t in hidden_layers if t[0] == max(layers_list)]
    values = [value[-1]*elem[0] for value in previous_layer]
    elem.append(sum(values)+elem[1])
    output.append(sum(values)+elem[1])


  return output
