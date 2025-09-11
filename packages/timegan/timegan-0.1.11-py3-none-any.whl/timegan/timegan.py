"""Time-series Generative Adversarial Networks (TimeGAN) Codebase.

Reference: Jinsung Yoon, Daniel Jarrett, Mihaela van der Schaar,
"Time-series Generative Adversarial Networks,"
Neural Information Processing Systems (NeurIPS), 2019.

Paper link: https://papers.nips.cc/paper/8789-time-series-generative-adversarial-networks

Last updated Date: April 24th 2020
Code author: Jinsung Yoon (jsyoon0823@gmail.com)

-----------------------------

timegan.py

Note: Use original data as training set to generater synthetic data (time-series)
"""

# mypy: ignore-errors
# Necessary Packages
from time import time_ns

import numpy as np
import tensorflow as tf
from tf_slim.layers import layers as _layers

from timegan.utils import batch_generator, extract_time, random_generator, rnn_cell

tf.compat.v1.disable_eager_execution()
tf.compat.v1.disable_v2_behavior()


# Min Max Scaler
def MinMaxScaler(data):
    """Min-Max Normalizer.

    Args:
      - data: raw data

    Returns:
      - norm_data: normalized data
      - min_val: minimum values (for renormalization)
      - max_val: maximum values (for renormalization)
    """
    min_val = np.min(np.min(data, axis=0), axis=0)
    data = data - min_val

    max_val = np.max(np.max(data, axis=0), axis=0)
    norm_data = data / (max_val + 1e-7)

    return norm_data, min_val, max_val


# Unpack parameters
def unpack_parameters(parameters):
    # hidden_dim, num_layers, iterations, batch_size, module_name, z_dim, gamma
    return (
        parameters["hidden_dim"],
        parameters["num_layer"],
        parameters["iterations"],
        parameters["batch_size"],
        parameters["module"],
        parameters["dim"],
        1,
    )


# Components of the network
def embedder(X, T, param):
    """Embedding network between original feature space to latent space.

    Args:
      - X: input time-series features
      - T: input time information

    Returns:
      - H: embeddings

    Update:
        Attempting to update tensorflow v1.x code to v2.x
        Currently able to do so with e_outputs, but may lose e_last_states along the way
    """
    hidden_dim, num_layers, iterations, batch_size, module_name, z_dim, gamma = unpack_parameters(param)
    dim = z_dim
    with tf.compat.v1.variable_scope("embedder", reuse=tf.compat.v1.AUTO_REUSE):
        # e_cell = StackedRNNCells([LSTMCell(hidden_dim) for _ in range(num_layers)])
        e_cell = tf.compat.v1.nn.rnn_cell.MultiRNNCell([rnn_cell(module_name, hidden_dim) for _ in range(num_layers)])

        # print("E cell: " , e_cell, "\nX: ", X)

        # rnn_layer = tf.keras.layers.RNN(e_cell, return_state=True)

        # e_outputs, e_last_states = rnn_layer(X)

        # e_outputs = tf.keras.layers.RNN(e_cell)(X)
        # e_last_states = X

        # print("e out: " , e_outputs, "\n X ", e_last_states)

        # e_outputs, e_last_states = tf.keras.layers.RNN(e_cell, return_sequences=True, return_state=True)(X)
        e_outputs, e_last_states = tf.compat.v1.nn.dynamic_rnn(e_cell, X, dtype=tf.float32, sequence_length=T)

        # H = tf.keras.layers.Dense(hidden_dim, activation=tf.nn.sigmoid)(e_outputs)
        H = _layers.fully_connected(e_outputs, hidden_dim, activation_fn=tf.nn.sigmoid)
        print("H: ", H)
        return H


'''
# Incorperate static features
def embedder (X, T, S, param):
    """Embedding network between original feature space to latent space.

    Args:
      - X: input time-series features
      - T: input time information
      - S: static features

    Returns:
      - HT: time-series embeddings
      - HS: static embeddings
    """
    hidden_dim, num_layers, iterations, batch_size, module_name, z_dim, gamma = unpack_parameters(param)
    dim = z_dim
    with tf.compat.v1.variable_scope("embedder", reuse = tf.compat.v1.AUTO_REUSE):
      print("e_cell") # TEMP
      e_cell = tf.compat.v1.nn.rnn_cell.MultiRNNCell([rnn_cell(module_name, hidden_dim) for _ in range(num_layers)])
      print("e_output") # TEMP
      e_outputs, e_last_states = tf.compat.v1.nn.dynamic_rnn(e_cell, X, dtype=tf.float32, sequence_length = T)
      # TODO: Implement seperate hiddem dim and num layers for static features
      HS = _layers.stack(S, _layers.fully_connected, [hidden_dim for _ in range(num_layers)], activation_fn=tf.nn.sigmoid)
      # TODO, concatinate e_outputs and HS
      h_inputs = # TODO
      H = _layers.fully_connected(h_inputs, hidden_dim, activation_fn=tf.nn.sigmoid)
    return H, HS
'''


def recovery(H, T, param):
    """Recovery network from latent space to original space.

    Args:
      - H: latent representation
      - T: input time information

    Returns:
      - X_tilde: recovered data
    """

    hidden_dim, num_layers, iterations, batch_size, module_name, z_dim, gamma = unpack_parameters(param)
    dim = z_dim

    # print("H shape: ", X.shape)
    with tf.compat.v1.variable_scope("recovery", reuse=tf.compat.v1.AUTO_REUSE):
        # r_cell = StackedRNNCells([LSTMCell(hidden_dim) for _ in range(num_layers)])
        # print("hidden_dim: ", hidden_dim, "num_layers: ", num_layers)
        # print("R cell: ", r_cell)
        # print("H shape: ", X.shape)
        # r_outputs = tf.keras.layers.RNN(r_cell)(H)
        # X_tilde = tf.keras.layers.Dense(dim, activation=tf.nn.sigmoid)(r_outputs)
        r_cell = tf.compat.v1.nn.rnn_cell.MultiRNNCell([rnn_cell(module_name, hidden_dim) for _ in range(num_layers)])
        r_outputs, r_last_states = tf.compat.v1.nn.dynamic_rnn(r_cell, H, dtype=tf.float32, sequence_length=T)
        X_tilde = _layers.fully_connected(r_outputs, dim, activation_fn=tf.nn.sigmoid)

    return X_tilde

    # hidden_dim, num_layers, iterations, batch_size, module_name, z_dim, gamma = unpack_parameters(param)
    # dim = z_dim
    # with tf.compat.v1.variable_scope("recovery", reuse=tf.compat.v1.AUTO_REUSE):

    #
    # return X_tilde


def generator(Z, T, param):
    """Generator function: Generate time-series data in latent space.

    Args:
      - Z: random variables
      - T: input time information

    Returns:
      - E: generated embedding
    """
    hidden_dim, num_layers, iterations, batch_size, module_name, z_dim, gamma = unpack_parameters(param)
    dim = z_dim
    with tf.compat.v1.variable_scope("generator", reuse=tf.compat.v1.AUTO_REUSE):
        e_cell = tf.compat.v1.nn.rnn_cell.MultiRNNCell([rnn_cell(module_name, hidden_dim) for _ in range(num_layers)])
        e_outputs, e_last_states = tf.compat.v1.nn.dynamic_rnn(e_cell, Z, dtype=tf.float32, sequence_length=T)
        E = _layers.fully_connected(e_outputs, hidden_dim, activation_fn=tf.nn.sigmoid)
    return E


def supervisor(H, T, param):
    """Generate next sequence using the previous sequence.

    Args:
      - H: latent representation
      - T: input time information

    Returns:
      - S: generated sequence based on the latent representations generated by the generator
    """
    hidden_dim, num_layers, iterations, batch_size, module_name, z_dim, gamma = unpack_parameters(param)
    dim = z_dim
    with tf.compat.v1.variable_scope("supervisor", reuse=tf.compat.v1.AUTO_REUSE):
        e_cell = tf.compat.v1.nn.rnn_cell.MultiRNNCell(
            [rnn_cell(module_name, hidden_dim) for _ in range(num_layers - 1)]
        )
        e_outputs, e_last_states = tf.compat.v1.nn.dynamic_rnn(e_cell, H, dtype=tf.float32, sequence_length=T)
        S = _layers.fully_connected(e_outputs, hidden_dim, activation_fn=tf.nn.sigmoid)
    return S


def discriminator(H, T, param):
    """Discriminate the original and synthetic time-series data.

    Args:
      - H: latent representation
      - T: input time information

    Returns:
      - Y_hat: classification results between original and synthetic time-series
    """
    hidden_dim, num_layers, iterations, batch_size, module_name, z_dim, gamma = unpack_parameters(param)
    dim = z_dim
    with tf.compat.v1.variable_scope("discriminator", reuse=tf.compat.v1.AUTO_REUSE):
        d_cell = tf.compat.v1.nn.rnn_cell.MultiRNNCell([rnn_cell(module_name, hidden_dim) for _ in range(num_layers)])
        d_outputs, d_last_states = tf.compat.v1.nn.dynamic_rnn(d_cell, H, dtype=tf.float32, sequence_length=T)
        Y_hat = _layers.fully_connected(d_outputs, 1, activation_fn=None)
    return Y_hat


def train_timegan(ori_data, parameters, filename="timegan_save", version=0):
    """TimeGAN training function.

    Use original data as training set to generater synthetic data (time-series)
    Trains timegan from scratch

    Args:
      - ori_data: original time-series data
      - parameters: TimeGAN network parameters
      - filename: filename to save the model in, default "timegan_save"
      - version: version of the snapshot, default 0

    Returns:
      - generated_data: generated time-series data
    """
    # Initialization on the Graph
    tf.compat.v1.reset_default_graph()

    # Basic Parameters
    no, seq_len, dim = np.asarray(ori_data).shape

    # Maximum sequence length and each sequence length
    ori_time, max_seq_len = extract_time(ori_data)

    # Normalization
    ori_data, min_val, max_val = MinMaxScaler(ori_data)

    ## Build a RNN networks

    # Network Parameters
    hidden_dim = parameters["hidden_dim"]
    num_layers = parameters["num_layer"]
    iterations = parameters["iterations"]
    batch_size = parameters["batch_size"]
    module_name = parameters["module"]
    parameters["dim"] = dim
    z_dim = dim
    gamma = 1

    # Input place holders
    X = tf.compat.v1.placeholder(tf.float32, [None, max_seq_len, dim], name="myinput_x")
    Z = tf.compat.v1.placeholder(tf.float32, [None, max_seq_len, z_dim], name="myinput_z")
    T = tf.compat.v1.placeholder(tf.int32, [None], name="myinput_t")

    # Embedder & Recovery
    H = embedder(X, T, parameters)
    X_tilde = recovery(H, T, parameters)

    # Generator
    E_hat = generator(Z, T, parameters)
    H_hat = supervisor(E_hat, T, parameters)
    H_hat_supervise = supervisor(H, T, parameters)

    # Synthetic data
    X_hat = recovery(H_hat, T, parameters)

    # Discriminator
    Y_fake = discriminator(H_hat, T, parameters)
    Y_real = discriminator(H, T, parameters)
    Y_fake_e = discriminator(E_hat, T, parameters)

    # Variables
    e_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("embedder")]
    r_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("recovery")]
    g_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("generator")]
    s_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("supervisor")]
    d_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("discriminator")]

    # Discriminator loss
    D_loss_real = tf.compat.v1.losses.sigmoid_cross_entropy(tf.ones_like(Y_real), Y_real)
    D_loss_fake = tf.compat.v1.losses.sigmoid_cross_entropy(tf.zeros_like(Y_fake), Y_fake)
    D_loss_fake_e = tf.compat.v1.losses.sigmoid_cross_entropy(tf.zeros_like(Y_fake_e), Y_fake_e)
    D_loss = D_loss_real + D_loss_fake + gamma * D_loss_fake_e

    # Generator loss
    # 1. Adversarial loss
    G_loss_U = tf.compat.v1.losses.sigmoid_cross_entropy(tf.ones_like(Y_fake), Y_fake)
    G_loss_U_e = tf.compat.v1.losses.sigmoid_cross_entropy(tf.ones_like(Y_fake_e), Y_fake_e)

    # 2. Supervised loss
    G_loss_S = tf.compat.v1.losses.mean_squared_error(H[:, 1:, :], H_hat_supervise[:, :-1, :])

    # 3. Two Momments
    G_loss_V1 = tf.reduce_mean(
        input_tensor=tf.abs(
            tf.sqrt(tf.nn.moments(x=X_hat, axes=[0])[1] + 1e-6) - tf.sqrt(tf.nn.moments(x=X, axes=[0])[1] + 1e-6)
        )
    )
    G_loss_V2 = tf.reduce_mean(
        input_tensor=tf.abs((tf.nn.moments(x=X_hat, axes=[0])[0]) - (tf.nn.moments(x=X, axes=[0])[0]))
    )

    G_loss_V = G_loss_V1 + G_loss_V2

    # 4. Summation
    G_loss = G_loss_U + gamma * G_loss_U_e + 100 * tf.sqrt(G_loss_S) + 100 * G_loss_V

    # Embedder network loss
    E_loss_T0 = tf.compat.v1.losses.mean_squared_error(X, X_tilde)
    E_loss0 = 10 * tf.sqrt(E_loss_T0)
    E_loss = E_loss0 + 0.1 * G_loss_S

    # optimizer
    E0_solver = tf.compat.v1.train.AdamOptimizer().minimize(E_loss0, var_list=e_vars + r_vars)
    E_solver = tf.compat.v1.train.AdamOptimizer().minimize(E_loss, var_list=e_vars + r_vars)
    D_solver = tf.compat.v1.train.AdamOptimizer().minimize(D_loss, var_list=d_vars)
    G_solver = tf.compat.v1.train.AdamOptimizer().minimize(G_loss, var_list=g_vars + s_vars)
    GS_solver = tf.compat.v1.train.AdamOptimizer().minimize(G_loss_S, var_list=g_vars + s_vars)

    ## TimeGAN training
    sess = tf.compat.v1.Session()
    sess.run(tf.compat.v1.global_variables_initializer())

    # Create Saver
    saver = tf.compat.v1.train.Saver()

    # 1. Embedding network training
    print("Start Embedding Network Training")

    for itt in range(iterations):
        # Set mini-batch
        X_mb, T_mb = batch_generator(ori_data, ori_time, batch_size)
        # Train embedder
        _, step_e_loss = sess.run([E0_solver, E_loss_T0], feed_dict={X: X_mb, T: T_mb})
        # Checkpoint
        if itt % 10 == 0:  # Formerly 100 or 1000
            print("step: " + str(itt) + "/" + str(iterations) + ", e_loss: " + str(np.round(np.sqrt(step_e_loss), 4)))

    print("Finish Embedding Network Training")

    # 2. Training only with supervised loss
    print("Start Training with Supervised Loss Only")

    for itt in range(iterations):
        # Set mini-batch
        X_mb, T_mb = batch_generator(ori_data, ori_time, batch_size)
        # Random vector generation
        Z_mb = random_generator(batch_size, z_dim, T_mb, max_seq_len)
        # Train generator
        _, step_g_loss_s = sess.run([GS_solver, G_loss_S], feed_dict={Z: Z_mb, X: X_mb, T: T_mb})
        # Checkpoint
        if itt % 10 == 0:  # Formerly 100 or 1000
            print("step: " + str(itt) + "/" + str(iterations) + ", s_loss: " + str(np.round(np.sqrt(step_g_loss_s), 4)))

    print("Finish Training with Supervised Loss Only")

    # 3. Joint Training
    print("Start Joint Training")

    for itt in range(iterations):
        # Generator training (twice more than discriminator training)
        for kk in range(2):
            # Set mini-batch
            X_mb, T_mb = batch_generator(ori_data, ori_time, batch_size)
            # Random vector generation
            Z_mb = random_generator(batch_size, z_dim, T_mb, max_seq_len)
            # Train generator
            _, step_g_loss_u, step_g_loss_s, step_g_loss_v = sess.run(
                [G_solver, G_loss_U, G_loss_S, G_loss_V], feed_dict={Z: Z_mb, X: X_mb, T: T_mb}
            )
            # Train embedder
            _, step_e_loss_t0 = sess.run([E_solver, E_loss_T0], feed_dict={Z: Z_mb, X: X_mb, T: T_mb})

        # Discriminator training
        # Set mini-batch
        X_mb, T_mb = batch_generator(ori_data, ori_time, batch_size)
        # Random vector generation
        Z_mb = random_generator(batch_size, z_dim, T_mb, max_seq_len)
        # Check discriminator loss before updating
        check_d_loss = sess.run(D_loss, feed_dict={X: X_mb, T: T_mb, Z: Z_mb})
        # Train discriminator (only when the discriminator does not work well)
        if check_d_loss > 0.15:
            _, step_d_loss = sess.run([D_solver, D_loss], feed_dict={X: X_mb, T: T_mb, Z: Z_mb})

        # Print multiple checkpoints
        if itt % 10 == 0:  # Formerly 100 or 1000
            print(
                "step: "
                + str(itt)
                + "/"
                + str(iterations)
                + ", d_loss: "
                + str(np.round(step_d_loss, 4))
                + ", g_loss_u: "
                + str(np.round(step_g_loss_u, 4))
                + ", g_loss_s: "
                + str(np.round(np.sqrt(step_g_loss_s), 4))
                + ", g_loss_v: "
                + str(np.round(step_g_loss_v, 4))
                + ", e_loss_t0: "
                + str(np.round(np.sqrt(step_e_loss_t0), 4))
            )
    print("Finish Joint Training")

    ## Synthetic data generation
    Z_mb = random_generator(no, z_dim, ori_time, max_seq_len)
    generated_data_curr = sess.run(X_hat, feed_dict={Z: Z_mb, X: ori_data, T: ori_time})

    generated_data = list()

    for i in range(no):
        temp = generated_data_curr[i, : ori_time[i], :]
        generated_data.append(temp)

    # Renormalization
    generated_data = generated_data * max_val
    generated_data = generated_data + min_val

    # Save
    saver.save(sess, filename, global_step=version)

    return generated_data


# Trains a timeGAN model for a specific number of seconds, and then stops training, and saves session
# Parameters
# - ori_data: the original data
# - parameters: network parameters (iterations is changed to remaining iterations)
# - in_filename: the filename to load from
# - out_filename: the filename to save to; if None, will save to in_filename instead
# - seconds: maximum number of seconds to train for
# - phase: the current phase of training (integer)
#          1 - Embedding network training
#          2 - Supervised loss
#          3 - Joint training
#          4 - Data generation
# - current_iter: the current iteration that training paused on
# - new: whether or not to start training network from scratch - defaults to False
# - version: version of the savefile
#
# Returns: A tuple of variable length; the first element of the tuple determines its length and content
#          First value of -1 (error)
#                (-1, msg)
#                - -1: phase indicator; indicates that there is an error
#                - msg: error message
#          First value of 1, 2 or 3 (the network still needs to train)
#                (next_phase, iter)
#                - next_phase: the phase to be run in the next use of this function; either phase, or phase+1
#                              depending upon if the current phase has completed
#                - iter: how many iterations have been completed
#          First value of 4 (training is finished; data is generated)
#                (4, generated_data)
#                - 4: phase indicator; should be 4 to indicate that training has been finished/data has been generated
#                - generated_data: generated data
def train_timegan_timed(
    ori_data, parameters, in_filename, out_filename=None, seconds=3600, phase=1, current_iter=0, new=False, version=0
):
    # Set output filename to input filename if no output filename is provided
    if out_filename is None:
        out_filename = in_filename

    # Initialization on the Graph
    tf.compat.v1.reset_default_graph()

    # Basic Parameters
    no, seq_len, dim = np.asarray(ori_data).shape

    # Maximum sequence length and each sequence length
    ori_time, max_seq_len = extract_time(ori_data)

    # Normalization
    ori_data, min_val, max_val = MinMaxScaler(ori_data)

    ## Build a RNN networks

    # Network Parameters
    hidden_dim = parameters["hidden_dim"]
    num_layers = parameters["num_layer"]
    iterations = parameters["iterations"]
    batch_size = parameters["batch_size"]
    module_name = parameters["module"]
    parameters["dim"] = dim
    z_dim = dim
    gamma = 1

    # Input place holders
    X = tf.compat.v1.placeholder(tf.float32, [None, max_seq_len, dim], name="myinput_x")
    Z = tf.compat.v1.placeholder(tf.float32, [None, max_seq_len, z_dim], name="myinput_z")
    T = tf.compat.v1.placeholder(tf.int32, [None], name="myinput_t")

    # Embedder & Recovery
    H = embedder(X, T, parameters)
    X_tilde = recovery(H, T, parameters)

    # Generator
    E_hat = generator(Z, T, parameters)
    H_hat = supervisor(E_hat, T, parameters)
    H_hat_supervise = supervisor(H, T, parameters)

    # Synthetic data
    X_hat = recovery(H_hat, T, parameters)

    # Discriminator
    Y_fake = discriminator(H_hat, T, parameters)
    Y_real = discriminator(H, T, parameters)
    Y_fake_e = discriminator(E_hat, T, parameters)

    # Variables
    e_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("embedder")]
    r_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("recovery")]
    g_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("generator")]
    s_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("supervisor")]
    d_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("discriminator")]

    # Discriminator loss
    D_loss_real = tf.compat.v1.losses.sigmoid_cross_entropy(tf.ones_like(Y_real), Y_real)
    D_loss_fake = tf.compat.v1.losses.sigmoid_cross_entropy(tf.zeros_like(Y_fake), Y_fake)
    D_loss_fake_e = tf.compat.v1.losses.sigmoid_cross_entropy(tf.zeros_like(Y_fake_e), Y_fake_e)
    D_loss = D_loss_real + D_loss_fake + gamma * D_loss_fake_e

    # Generator loss
    # 1. Adversarial loss
    G_loss_U = tf.compat.v1.losses.sigmoid_cross_entropy(tf.ones_like(Y_fake), Y_fake)
    G_loss_U_e = tf.compat.v1.losses.sigmoid_cross_entropy(tf.ones_like(Y_fake_e), Y_fake_e)

    # 2. Supervised loss
    G_loss_S = tf.compat.v1.losses.mean_squared_error(H[:, 1:, :], H_hat_supervise[:, :-1, :])

    # 3. Two Momments
    G_loss_V1 = tf.reduce_mean(
        input_tensor=tf.abs(
            tf.sqrt(tf.nn.moments(x=X_hat, axes=[0])[1] + 1e-6) - tf.sqrt(tf.nn.moments(x=X, axes=[0])[1] + 1e-6)
        )
    )
    G_loss_V2 = tf.reduce_mean(
        input_tensor=tf.abs((tf.nn.moments(x=X_hat, axes=[0])[0]) - (tf.nn.moments(x=X, axes=[0])[0]))
    )

    G_loss_V = G_loss_V1 + G_loss_V2

    # 4. Summation
    G_loss = G_loss_U + gamma * G_loss_U_e + 100 * tf.sqrt(G_loss_S) + 100 * G_loss_V

    # Embedder network loss
    E_loss_T0 = tf.compat.v1.losses.mean_squared_error(X, X_tilde)
    E_loss0 = 10 * tf.sqrt(E_loss_T0)
    E_loss = E_loss0 + 0.1 * G_loss_S

    # optimizer
    E0_solver = tf.compat.v1.train.AdamOptimizer().minimize(E_loss0, var_list=e_vars + r_vars)
    E_solver = tf.compat.v1.train.AdamOptimizer().minimize(E_loss, var_list=e_vars + r_vars)
    D_solver = tf.compat.v1.train.AdamOptimizer().minimize(D_loss, var_list=d_vars)
    G_solver = tf.compat.v1.train.AdamOptimizer().minimize(G_loss, var_list=g_vars + s_vars)
    GS_solver = tf.compat.v1.train.AdamOptimizer().minimize(G_loss_S, var_list=g_vars + s_vars)

    ## TimeGAN training
    sess = tf.compat.v1.Session()
    # Initialize if training from scratch
    if new:
        phase = 1
        current_iter = 0
        sess.run(tf.compat.v1.global_variables_initializer())

    # Create Saver
    saver = tf.compat.v1.train.Saver()
    # Load data if continuing training
    if not new:
        saver.restore(sess, in_filename + "-" + str(version))

    # Set up time stuff
    start_time = time_ns()  # Get the start time of the training
    max_time_ns = seconds * (10**9)  # Convert seconds to nanoseconds

    # 1. Embedding network training
    if phase == 1:
        print("Start Embedding Network Training")

        for itt in range(current_iter, iterations):
            # Set mini-batch
            X_mb, T_mb = batch_generator(ori_data, ori_time, batch_size)
            # Train embedder
            _, step_e_loss = sess.run([E0_solver, E_loss_T0], feed_dict={X: X_mb, T: T_mb})

            # End/suspend training if time is over max
            now = time_ns()
            if now - start_time >= max_time_ns:
                saver.save(sess, out_filename, global_step=version)
                return (1, itt)

        # Training phase finished, save model and increment phase
        print("Finish Embedding Network Training")
        saver.save(sess, out_filename, global_step=version)
        phase = 2
    if phase == 2:
        # 2. Training only with supervised loss
        print("Start Training with Supervised Loss Only")

        for itt in range(current_iter, iterations):
            # Set mini-batch
            X_mb, T_mb = batch_generator(ori_data, ori_time, batch_size)
            # Random vector generation
            Z_mb = random_generator(batch_size, z_dim, T_mb, max_seq_len)
            # Train generator
            _, step_g_loss_s = sess.run([GS_solver, G_loss_S], feed_dict={Z: Z_mb, X: X_mb, T: T_mb})

            # End/suspend training if time is over max
            now = time_ns()
            if now - start_time >= max_time_ns:
                saver.save(sess, out_filename, global_step=version)
                return (2, itt)

        # Training phase finished, save model and increment phase
        print("Finish Training with Supervised Loss Only")
        saver.save(sess, out_filename, global_step=version)
        phase = 3
    if phase == 3:
        # 3. Joint Training
        print("Start Joint Training")

        for itt in range(current_iter, iterations):
            # Generator training (twice more than discriminator training)
            for kk in range(2):
                # Set mini-batch
                X_mb, T_mb = batch_generator(ori_data, ori_time, batch_size)
                # Random vector generation
                Z_mb = random_generator(batch_size, z_dim, T_mb, max_seq_len)
                # Train generator
                _, step_g_loss_u, step_g_loss_s, step_g_loss_v = sess.run(
                    [G_solver, G_loss_U, G_loss_S, G_loss_V], feed_dict={Z: Z_mb, X: X_mb, T: T_mb}
                )
                # Train embedder
                _, step_e_loss_t0 = sess.run([E_solver, E_loss_T0], feed_dict={Z: Z_mb, X: X_mb, T: T_mb})

            # Discriminator training
            # Set mini-batch
            X_mb, T_mb = batch_generator(ori_data, ori_time, batch_size)
            # Random vector generation
            Z_mb = random_generator(batch_size, z_dim, T_mb, max_seq_len)
            # Check discriminator loss before updating
            check_d_loss = sess.run(D_loss, feed_dict={X: X_mb, T: T_mb, Z: Z_mb})
            # Train discriminator (only when the discriminator does not work well)
            if check_d_loss > 0.15:
                _, step_d_loss = sess.run([D_solver, D_loss], feed_dict={X: X_mb, T: T_mb, Z: Z_mb})

            # End/suspend training if time is over max
            now = time_ns()
            if now - start_time >= max_time_ns:
                saver.save(sess, out_filename, global_step=version)
                return (3, itt)
        # Final training phase finished, proceed to data generation
        print("Finish Joint Training")
    if phase > 4 or phase <= 0:
        # Invalid phase number
        return (-1, str(phase) + " is not a valid phase indicator")

    ## Synthetic data generation
    Z_mb = random_generator(no, z_dim, ori_time, max_seq_len)
    generated_data_curr = sess.run(X_hat, feed_dict={Z: Z_mb, X: ori_data, T: ori_time})

    generated_data = list()

    for i in range(no):
        temp = generated_data_curr[i, : ori_time[i], :]
        generated_data.append(temp)

    # Renormalization
    generated_data = generated_data * max_val
    generated_data = generated_data + min_val

    # Save
    saver.save(sess, out_filename, global_step=version)

    return (4, generated_data)


def load_timegan(ori_data, parameters, filename):
    """TimeGAN function.

    Use original data as training set to generater synthetic data (time-series)
    Loads from snapshot

    Args:
      - ori_data: original time-series data
      - parameters: TimeGAN network parameters
      - filename: filename of the snapshot to load

    Returns:
      - generated_data: generated time-series data
    """
    # Initialization on the Graph
    tf.compat.v1.reset_default_graph()

    # Basic Parameters
    no, seq_len, dim = np.asarray(ori_data).shape

    # Maximum sequence length and each sequence length
    ori_time, max_seq_len = extract_time(ori_data)

    # Normalization
    ori_data, min_val, max_val = MinMaxScaler(ori_data)

    ## Build a RNN networks

    # Network Parameters
    hidden_dim = parameters["hidden_dim"]
    num_layers = parameters["num_layer"]
    iterations = parameters["iterations"]
    batch_size = parameters["batch_size"]
    module_name = parameters["module"]
    parameters["dim"] = dim
    z_dim = dim
    gamma = 1

    # Input place holders
    X = tf.compat.v1.placeholder(tf.float32, [None, max_seq_len, dim], name="myinput_x")
    Z = tf.compat.v1.placeholder(tf.float32, [None, max_seq_len, z_dim], name="myinput_z")
    T = tf.compat.v1.placeholder(tf.int32, [None], name="myinput_t")

    # Embedder & Recovery
    H = embedder(X, T, parameters)
    X_tilde = recovery(H, T, parameters)

    # Generator
    E_hat = generator(Z, T, parameters)
    H_hat = supervisor(E_hat, T, parameters)
    H_hat_supervise = supervisor(H, T, parameters)

    # Synthetic data
    X_hat = recovery(H_hat, T, parameters)

    # Discriminator
    Y_fake = discriminator(H_hat, T, parameters)
    Y_real = discriminator(H, T, parameters)
    Y_fake_e = discriminator(E_hat, T, parameters)

    # Variables
    e_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("embedder")]
    r_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("recovery")]
    g_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("generator")]
    s_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("supervisor")]
    d_vars = [v for v in tf.compat.v1.trainable_variables() if v.name.startswith("discriminator")]

    # Discriminator loss
    D_loss_real = tf.compat.v1.losses.sigmoid_cross_entropy(tf.ones_like(Y_real), Y_real)
    D_loss_fake = tf.compat.v1.losses.sigmoid_cross_entropy(tf.zeros_like(Y_fake), Y_fake)
    D_loss_fake_e = tf.compat.v1.losses.sigmoid_cross_entropy(tf.zeros_like(Y_fake_e), Y_fake_e)
    D_loss = D_loss_real + D_loss_fake + gamma * D_loss_fake_e

    # Generator loss
    # 1. Adversarial loss
    G_loss_U = tf.compat.v1.losses.sigmoid_cross_entropy(tf.ones_like(Y_fake), Y_fake)
    G_loss_U_e = tf.compat.v1.losses.sigmoid_cross_entropy(tf.ones_like(Y_fake_e), Y_fake_e)

    # 2. Supervised loss
    G_loss_S = tf.compat.v1.losses.mean_squared_error(H[:, 1:, :], H_hat_supervise[:, :-1, :])

    # 3. Two Momments
    G_loss_V1 = tf.reduce_mean(
        input_tensor=tf.abs(
            tf.sqrt(tf.nn.moments(x=X_hat, axes=[0])[1] + 1e-6) - tf.sqrt(tf.nn.moments(x=X, axes=[0])[1] + 1e-6)
        )
    )
    G_loss_V2 = tf.reduce_mean(
        input_tensor=tf.abs((tf.nn.moments(x=X_hat, axes=[0])[0]) - (tf.nn.moments(x=X, axes=[0])[0]))
    )

    G_loss_V = G_loss_V1 + G_loss_V2

    # 4. Summation
    G_loss = G_loss_U + gamma * G_loss_U_e + 100 * tf.sqrt(G_loss_S) + 100 * G_loss_V

    # Embedder network loss
    E_loss_T0 = tf.compat.v1.losses.mean_squared_error(X, X_tilde)
    E_loss0 = 10 * tf.sqrt(E_loss_T0)
    E_loss = E_loss0 + 0.1 * G_loss_S

    # optimizer
    E0_solver = tf.compat.v1.train.AdamOptimizer().minimize(E_loss0, var_list=e_vars + r_vars)
    E_solver = tf.compat.v1.train.AdamOptimizer().minimize(E_loss, var_list=e_vars + r_vars)
    D_solver = tf.compat.v1.train.AdamOptimizer().minimize(D_loss, var_list=d_vars)
    G_solver = tf.compat.v1.train.AdamOptimizer().minimize(G_loss, var_list=g_vars + s_vars)
    GS_solver = tf.compat.v1.train.AdamOptimizer().minimize(G_loss_S, var_list=g_vars + s_vars)

    # Load snapshot
    sess = tf.compat.v1.Session()
    saver = tf.compat.v1.train.Saver()
    saver.restore(sess, filename)

    # Synthetic data generation
    Z_mb = random_generator(no, z_dim, ori_time, max_seq_len)
    generated_data_curr = sess.run(X_hat, feed_dict={Z: Z_mb, X: ori_data, T: ori_time})

    generated_data = list()

    for i in range(no):
        temp = generated_data_curr[i, : ori_time[i], :]
        generated_data.append(temp)

    # Renormalization
    generated_data = generated_data * max_val
    generated_data = generated_data + min_val

    return generated_data
