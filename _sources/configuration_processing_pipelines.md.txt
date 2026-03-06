# Processing Pipelines



## BatchProcessingPipeline

This Processing Pipeline accumulates individual data events into fixed-size batches
before passing them downstream. Once a full batch has been collected, it is yielded as
a single dictionary of stacked numpy arrays. Any remaining events that do not fill a
complete batch at the end of the data stream are yielded as a partial batch.

### *Configuration Parameters for BatchProcessingPipeline*

* `batch_size` (int): The number of events to accumulate before yielding a batch.
  Example: `10`



## PeaknetPreprocessingPipeline

This Processing Pipeline prepares detector image data for inference with the PeakNet
peak-finding model. It applies the following steps in order:

1. **Padding**: each individual detector image is zero-padded to a uniform target size
   before being added to the batch.
2. **Batching**: padded images are accumulated into fixed-size batches of `batch_size`
   events.
3. **Channel dimension**: after batching, a channel dimension is optionally inserted
   into the image arrays, converting them from shape `(B, H, W)` to `(B, C, H, W)`.

Non-image data (timestamps, scalars, etc.) passes through all stages unchanged.

### *Configuration Parameters for PeaknetPreprocessingPipeline*

* `batch_size` (int): The number of events to accumulate before yielding a batch.
  Example: `8`

* `target_height` (int): The target height in pixels to which each detector image is
  padded before batching. Images that are already at least this tall are not padded
  along the height axis. Example: `1024`

* `target_width` (int): The target width in pixels to which each detector image is
  padded before batching. Images that are already at least this wide are not padded
  along the width axis. Example: `1024`

* `pad_style` (str): This parameter is optional. It controls how the padding is
  distributed around the image. Accepted values are:

    - `center`: padding is distributed as equally as possible on both sides of each
      axis (top/bottom and left/right).
    - `bottom-right`: all padding is added to the bottom and right edges of the image,
      leaving the top-left corner of the original image aligned with the top-left
      corner of the padded output.

  The default value of this parameter is `center`. Example: `bottom-right`

* `add_channel_dim` (bool): This parameter is optional. When `true`, a channel
  dimension is inserted into batched image arrays after batching, transforming their
  shape from `(B, H, W)` to `(B, C, H, W)`. The default value of this parameter is
  `true`. Example: `false`

* `num_channels` (int): This parameter is optional. It specifies the number of
  channels `C` to produce when `add_channel_dim` is `true`. If greater than 1, the
  image data is repeated along the new channel axis. This parameter is ignored when
  `add_channel_dim` is `false`. The default value of this parameter is `1`.
  Example: `3`
