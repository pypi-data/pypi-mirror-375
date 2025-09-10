import matplotlib.pyplot as plt

def sign(x):
  if x >= 0:
    return 1
  else:
    return -1

def graph_nn(layer_neurons, neuron_parameters=[]):
  """
    Draws a simple diagram of a complete neural network

    Parameters:
    -----------
    layer_neurons : list of int
        Number of neurons for each layer [input, hidden1, hidden2, ..., output]

    neuron_parameters (optional) : nested lists
        Parameters for each neuron (weight, bias), divided by layer.
        Each sublist is one layer, containing tuples (weight, bias).
        First neuron is the upper one, then descending.

    Example:
    --------
    >>> graph_nn(
            layer_neurons = [3, 3, 2, 3],
            neuron_parameters = [
                [(0.9, 1.1), (0.3, 2.4), (0.4, 3)],
                [(0.1, 4), (0.6, 1.3)],
                [(0.99, 222), (0.1, 10), (0.5, 1.1)]
            ]
        )
  """

  neuroni_lista = []
  d = max(layer_neurons)*0.02
  # LOOP SUI LAYER
  for i in range(0, len(layer_neurons)):

    # Se non è l’input layer e i parametri sono stati passati, carico quelli del layer
    if neuron_parameters != [] and i != 0:
      layer_params = neuron_parameters[i-1]

    # Colori e gestione testo (input = arancione, output = azzurro, hidden = verde)
    if i == 0:
      color = "orange"
      value_text = True
    elif i == len(layer_neurons) - 1:
      color = "cyan"
      value_text = False
    else:
      color = "lime"
      value_text = False

    # Caso: layer con numero pari di neuroni
    if layer_neurons[i] % 2 == 0:
      number_of_neurons = layer_neurons[i]
      neuron_currenntly_drawing = 0

      for neuron in range(int(-number_of_neurons/2), int(+number_of_neurons/2 + 1)):
        if neuron != 0:
          coord = sign(neuron)*0.5 + neuron-sign(neuron)

          # Disegno neurone
          plt.scatter(i, coord, color=color, s=500, zorder=2)

          # Testo dentro il neurone (solo input layer)
          if value_text and neuron_parameters != []:
            plt.text(i, coord, "VAL", ha="center", va="center")

          # Se ci sono parametri, scrivo weight e bias sopra/sotto
          if not value_text and neuron_parameters != []:
            plt.text(i, coord+d,
                     f"W/{layer_params[number_of_neurons-neuron_currenntly_drawing-1][0]}",
                     ha="center", va="center")
            plt.text(i, coord-d,
                     f"B/{layer_params[number_of_neurons-neuron_currenntly_drawing-1][1]}",
                     ha="center", va="center")

          neuroni_lista.append((i, coord))
          neuron_currenntly_drawing += 1

    # Caso: layer con numero dispari di neuroni
    if layer_neurons[i] % 2 == 1:
      number_of_neurons = layer_neurons[i]
      neuron_currenntly_drawing = 0

      for neuron in range(int(-layer_neurons[i]/2), int(+layer_neurons[i]/2 + 1)):
        coord = neuron

        # Disegno neurone
        plt.scatter(i, coord, color=color, s=500, zorder=2)

        # Testo dentro il neurone (solo input layer)
        if value_text and neuron_parameters != []:
          plt.text(i, coord, "VAL", ha="center", va="center")

        # Se ci sono parametri, scrivo weight e bias
        if not value_text and neuron_parameters != []:
          plt.text(i, coord+d,
                   f"W/{layer_params[number_of_neurons-neuron_currenntly_drawing-1][0]}",
                   ha="center", va="center")
          plt.text(i, coord-d,
                   f"B/{layer_params[number_of_neurons-neuron_currenntly_drawing-1][1]}",
                   ha="center", va="center")

        neuroni_lista.append((i, coord))
        neuron_currenntly_drawing += 1

  # DISEGNO CONNESSIONI FRA NEURONI
  for i in range(0, len(layer_neurons)-1):
    actual_neurons = [t for t in neuroni_lista if t[0] == i]
    next_neurons = [t for t in neuroni_lista if t[0] == i+1]
    for neur1 in actual_neurons:
      x1, y1 = neur1
      for neur2 in next_neurons:
        x2, y2 = neur2
        plt.plot([x1,x2], [y1,y2], color="lime", zorder=1)

  plt.axis("off")
  plt.show()
