# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..training_type import TrainingType
from .sft_parameters import SftParameters
from .lora_parameters import LoraParameters
from ..shared.finetuning_type import FinetuningType
from .distillation_parameters import DistillationParameters

__all__ = ["Hyperparameters", "Dpo"]


class Dpo(BaseModel):
    preference_average_log_probs: Optional[bool] = None
    """
    If set to true, the preference loss uses average log-probabilities, making the
    loss less sensitive to sequence length. Setting it to false (default) uses total
    log-probabilities, giving more influence to longer sequences.
    """

    preference_loss_weight: Optional[float] = None
    """Scales the contribution of the preference loss to the overall training
    objective.

    Increasing this value emphasizes learning from preference comparisons more
    strongly.
    """

    ref_policy_kl_penalty: Optional[float] = None
    """
    Controls how strongly the trained policy is penalized for deviating from the
    reference policy. Increasing this value encourages the policy to stay closer to
    the reference (more conservative learning), while decreasing it allows more
    freedom to explore user-preferred behavior. Parameter is called `beta` in the
    original paper
    """

    sft_average_log_probs: Optional[bool] = None
    """
    If set to true, the supervised fine-tuning (SFT) loss normalizes by sequence
    length, treating all examples equally regardless of length. If false (default),
    longer examples contribute more to the loss.
    """

    sft_loss_weight: Optional[float] = None
    """Scales the contribution of the supervised fine-tuning loss.

    Setting this to 0 disables SFT entirely, allowing training to focus exclusively
    on preference-based optimization.
    """


class Hyperparameters(BaseModel):
    finetuning_type: FinetuningType
    """The finetuning type for the customization job."""

    adam_beta1: Optional[float] = None
    """
    Controls the exponential decay rate for the moving average of past gradients
    (momentum), only used with cosine_annealing learning rate schedulers
    """

    adam_beta2: Optional[float] = None
    """
    Controls the decay rate for the moving average of past squared gradients
    (adaptive learning rate scaling), only used with cosine_annealing learning rate
    schedulers
    """

    batch_size: Optional[int] = None
    """
    Batch size is the number of training samples used to train a single forward and
    backward pass. This is related to the gradient_accumulation_steps in HF
    documentation where gradient_accumulation_steps = batch_size // micro_batch_size
    The default batch size for DPO when not provided is 16
    """

    distillation: Optional[DistillationParameters] = None
    """Specific parameters for knowledge distillation"""

    dpo: Optional[Dpo] = None
    """Specific parameters for DPO."""

    epochs: Optional[int] = None
    """
    Epochs is the number of complete passes through the training dataset. Default
    for DPO when not provided is 1
    """

    learning_rate: Optional[float] = None
    """
    How much to adjust the model parameters in response to the loss gradient.
    Default for DPO when not provided is 9e-06
    """

    log_every_n_steps: Optional[int] = None
    """
    Control logging frequency for metrics tracking. It may slow down training to log
    on every single batch.

            By default, logs every 10 training steps. This parameter is log_frequency in HF
    """

    lora: Optional[LoraParameters] = None
    """Specific parameters for LoRA."""

    max_steps: Optional[int] = None
    """
    If this parameter is provided and is greater than 0, we will stop execution
    after this number of steps.

        This number can not be less than val_check_interval.

        If less than val_check_interval it will set val_check_interval to be max_steps - 1
    """

    min_learning_rate: Optional[float] = None
    """
    Starting point for learning_rate scheduling, only used with cosine_annealing
    learning rate schedulers. Must be lower than learning_rate if provided. If not
    provided, this will default to 0.1 \\** learning_rate.
    """

    optimizer: Optional[
        Literal["adam_with_cosine_annealing", "adam_with_flat_lr", "adamw_with_cosine_annealing", "adamw_with_flat_lr"]
    ] = None
    """The supported optimizers that are configurable for customization.

    Cosine Annealing LR scheduler will start at min_learning_rate and move towards
    learning_rate over warmup_steps.

    Note: For models listed as NeMo checkpoint type, the only Adam implementation is
    Fused AdamW.
    """

    seed: Optional[int] = None
    """
    This is the seed that will be used to initialize all underlying Pytorch and
    Triton Trainers. By default this will be randomly initialized.

            Caution: There are a number of processes that still introduce variance between training runs for models trained
            from HF checkpoint.
    """

    sequence_packing_enabled: Optional[bool] = None
    """
    Sequence packing can improve speed of training by letting the training work on
    multiple rows at the same time. Experimental and not supported by all models. If
    a model is not supported, a warning will be returned in the response body and
    training will proceed with sequence packing disabled. Not recommended for
    produciton use. This flag may be removed in the future. See
    https://docs.nvidia.com/nemo-framework/user-guide/latest/sft_peft/packed_sequence.html
    for more details.
    """

    sft: Optional[SftParameters] = None
    """Specific parameters for SFT."""

    training_type: Optional[TrainingType] = None
    """The training type for the customization job."""

    val_check_interval: Optional[float] = None
    """
    Control how often to check the validation set, and how often to check for best
    checkpoint.

            You can check after a fixed number of training batches by passing an integer value.
            You can pass a float in the range [0.1, 1.0] to check after a fraction of the training epoch.

            If the best checkpoint is found after validation, it will be saved at that time temporarily, it is currently
            only uploaded at the end of the training run.

            Note: Early Stopping monitors the validation loss and stops the training when no improvement is observed
                after 10 epochs with a minimum delta of 0.001.

            If val_check_interval is greater than the number of training batches, validation will run every epoch.
    """

    warmup_steps: Optional[int] = None
    """
    Learning rate schedulers gradually increase the learning rate from a small
    initial value to the target value in `learning_rate` over this number of steps
    """

    weight_decay: Optional[float] = None
    """
    An additional penalty term added to the gradient descent to keep weights low and
    mitigate overfitting.
    """
