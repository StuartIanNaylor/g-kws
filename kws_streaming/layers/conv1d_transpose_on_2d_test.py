# coding=utf-8
# Copyright 2021 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Tests for kws_streaming.layers.conv1d_transpose_on_2d."""

from absl.testing import parameterized
import numpy as np
from kws_streaming.layers import conv1d_transpose_on_2d
from kws_streaming.layers import modes
from kws_streaming.layers import test_utils
from kws_streaming.layers.compat import tf
from kws_streaming.layers.compat import tf1
from kws_streaming.models import utils
from kws_streaming.train import test
tf1.disable_eager_execution()


def conv1d_on_2d_transpose_model(flags,
                                 filters,
                                 kernel_size,
                                 stride,
                                 channels=1):
  """Toy model to up-scale input data with Conv1DTransposeOn2D.

  It can be used for speech enhancement.

  Args:
      flags: model and data settings
      filters: number of filters (output channels)
      kernel_size: kernel_size of Conv1DTranspose layer
      stride: stride of Conv1DTranspose layer
      channels: number of channels in the input data
  Returns:
    Keras model
  """
  input_audio = tf.keras.layers.Input(
      shape=(flags.desired_samples, 1, channels), batch_size=flags.batch_size)
  net = input_audio
  net = conv1d_transpose_on_2d.Conv1DTransposeOn2D(
      filters=filters,
      kernel_size=(kernel_size, 1),
      strides=(stride, 1),
      use_bias=True,
      crop_output=True)(
          net)

  return tf.keras.Model(input_audio, net)


class Conv1DTransposeOn2DTest(tf.test.TestCase, parameterized.TestCase):

  def setUp(self):
    super(Conv1DTransposeOn2DTest, self).setUp()
    test_utils.set_seed(123)
    self.input_channels = 2

  @parameterized.parameters(1, 2, 3, 4, 5, 6)
  def test_streaming_strides(self, stride):
    """Test Conv1DTranspose layer in streaming mode with different strides.

    Args:
        stride: controls the upscaling factor
    """

    tf1.reset_default_graph()
    config = tf1.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf1.Session(config=config)
    tf1.keras.backend.set_session(sess)

    # model and data parameters
    step = 1  # amount of data fed into streaming model on every iteration
    params = test_utils.Params([step], clip_duration_ms=0.25)

    # prepare input data: [batch, time, 1, channels]
    x = np.random.rand(1, params.desired_samples, 1, self.input_channels)
    inp_audio = x

    # prepare non-streaming model
    model = conv1d_on_2d_transpose_model(
        params,
        filters=1,
        kernel_size=3,
        stride=stride,
        channels=self.input_channels)
    model.summary()

    # set weights with bias
    for layer in model.layers:
      if isinstance(layer, tf.keras.layers.Conv1DTranspose):
        layer.set_weights([
            np.ones(layer.weights[0].shape),
            np.zeros(layer.weights[1].shape) + 0.5
        ])

    params.data_shape = (1, 1, self.input_channels)

    # prepare streaming model
    model_stream = utils.to_streaming_inference(
        model, params, modes.Modes.STREAM_INTERNAL_STATE_INFERENCE)
    model_stream.summary()

    # run inference
    non_stream_out = model.predict(inp_audio)
    stream_out = test.run_stream_inference(params, model_stream, inp_audio)

    self.assertAllClose(stream_out, non_stream_out)

    # Convert TF non-streaming model to TFLite external-state streaming model.
    tflite_streaming_model = utils.model_to_tflite(
        sess, model, params, modes.Modes.STREAM_EXTERNAL_STATE_INFERENCE)
    self.assertTrue(tflite_streaming_model)

    # Run TFLite external-state streaming inference.
    interpreter = tf.lite.Interpreter(model_content=tflite_streaming_model)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()

    input_states = []
    # before processing test sequence we create model state
    for s in range(len(input_details)):
      input_states.append(np.zeros(input_details[s]['shape'], dtype=np.float32))

    stream_out_tflite_external_st = test.run_stream_inference_tflite(
        params, interpreter, inp_audio, input_states, concat=True)

    # compare streaming TFLite with external-state vs TF non-streaming
    self.assertAllClose(stream_out_tflite_external_st, non_stream_out)

  def test_dynamic_shape(self):
    # model and data parameters
    params = test_utils.Params([1], clip_duration_ms=0.25)

    # prepare input data
    x = np.random.rand(1, params.desired_samples, 1, self.input_channels)
    inp_audio = x

    # prepare non stream model
    params.desired_samples = None
    model = conv1d_on_2d_transpose_model(
        params,
        filters=1,
        kernel_size=3,
        stride=1,
        channels=self.input_channels)
    model.summary()

    # run inference on input with dynamic shape
    model.predict(inp_audio)

    with self.assertRaisesRegex(
        ValueError, 'in streaming mode time dimension of input packet '
        'should not be dynamic: TFLite limitation'):
      # streaming model expected to fail on input data with dynamic shape
      params.data_shape = (None, 1, self.input_channels)
      utils.to_streaming_inference(
          model, params, modes.Modes.STREAM_INTERNAL_STATE_INFERENCE)


if __name__ == '__main__':
  tf.test.main()
