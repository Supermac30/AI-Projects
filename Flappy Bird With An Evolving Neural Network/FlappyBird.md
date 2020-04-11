# Flappy Bird With An Evolving Neural Network
An implementation of Flappy Bird where a neural net takes control.

A simple neural net with 3 layers is trained to play flappy bird.
In the first layer, the vertical height of the bird, the vertical height of the next pipe, and whether or not the bird is currently jumping is inputted.
The second layer contains 5 hidden nodes.
The third layer contains one node. If the output is greater than 0.5 the bird jumps.

To train the neural net 50 players are created initially with random weights on each node. After all the players die, the best neural net
reproduces, creating 50 more players using its own weights but randomly changed by a small value. The greater the number of generations the smaller the variation
between parent and child to allow the training to converge onto a local max.

Adjusting the paramaters, like the learning rate and the discount factor, allows for better or worse training. With parameters I chose above
I managed to train a network to reach 400 points in only 6 generations! This network is in the textfile above.

## Dependencies
- TensorFlow
- Keras
- Numpy
- Pygame
