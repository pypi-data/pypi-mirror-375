"""
   Copyright 2025 Altavo GmbH

   “Commons Clause” License Condition v1.0

   The Software is provided to you by Altavo GmbH under the License, 
   as defined below, subject to the following condition.

   Without limiting other conditions in the License, the grant of rights 
   under the License will not include, and the License does not grant to
   you, the right to Sell the Software.

   For purposes of the foregoing, “Sell” means practicing any or all of the 
   rights granted to you under the License to provide to third parties, 
   for a fee or other consideration (including without limitation fees for
   hosting or consulting/ support services related to the Software), 
   a product or service whose value derives, entirely or substantially, 
   from the functionality of the Software. 

   Any license notice or attribution required by the License must also 
   include this Commons Clause License Condition notice.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

"""
This file is adapted from:
https://github.com/NVIDIA/NeMo/blob/main/nemo/collections/asr/modules/conv_asr.py

under the following license:


Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""



import torch
#from omegaconf import (
#    ListConfig,
#    OmegaConf,
#)
from typing import (
    Optional,
)
from .nemo_jasper import (
    JasperBlock,
    SqueezeExcite,
)
from .nemo_jasper import (
    MaskedConv1d,
    init_weights,
    jasper_activations,
)

""" ML Module port of the ConvASREncoder from the NeMo toolkit without dependencies on the
    following classes: NeuralModule, Exportable, AccessMixin
    Removed the following features:
        - quantization (via the PYTORCH_QUANTIZATION_AVAILABLE flag)
        - input type checking
    Source: 
        https://github.com/NVIDIA/NeMo/blob/main/nemo/collections/asr/modules/conv_asr.py
    """


class ConvASREncoder(torch.nn.Module):
    """
    Convolutional encoder for ASR models. With this class you can implement JasperNet and QuartzNet models.

    Based on these papers:
        https://arxiv.org/pdf/1904.03288.pdf
        https://arxiv.org/pdf/1910.10261.pdf
    """

    def input_example(
        self,
        max_batch=1,
        max_dim=8192,
    ):
        """
        Generates input examples for tracing etc.
        Returns:
            A tuple of input examples.
        """
        device = next(self.parameters()).device
        input_example = torch.randn(
            max_batch,
            self._feat_in,
            max_dim,
            device=device,
        )
        lens = torch.full(
            size=(input_example.shape[0],),
            fill_value=max_dim,
            device=device,
        )
        return tuple(
            [
                input_example,
                lens,
            ]
        )

    def __init__(
        self,
        jasper,
        activation: str,
        feat_in: int,
        normalization_mode: str = "batch",
        residual_mode: str = "add",
        norm_groups: int = -1,
        conv_mask: bool = True,
        frame_splicing: int = 1,
        init_mode: Optional[str] = "xavier_uniform",
    ):
        super().__init__()
        #if isinstance(
        #    jasper,
        #    ListConfig,
        #):
        #    jasper = OmegaConf.to_container(jasper)

        activation = jasper_activations[activation]()

        # If the activation can be executed in place, do so.
        if hasattr(
            activation,
            "inplace",
        ):
            activation.inplace = True

        feat_in = feat_in * frame_splicing

        self._feat_in = feat_in

        residual_panes = []
        encoder_layers = []
        self.dense_residual = False

        for (
            layer_idx,
            lcfg,
        ) in enumerate(jasper):
            dense_res = []
            if lcfg.get(
                "residual_dense",
                False,
            ):
                residual_panes.append(feat_in)
                dense_res = residual_panes
                self.dense_residual = True

            groups = lcfg.get(
                "groups",
                1,
            )
            separable = lcfg.get(
                "separable",
                False,
            )
            heads = lcfg.get(
                "heads",
                -1,
            )
            residual_mode = lcfg.get(
                "residual_mode",
                residual_mode,
            )
            se = lcfg.get(
                "se",
                False,
            )
            se_reduction_ratio = lcfg.get(
                "se_reduction_ratio",
                8,
            )
            se_context_window = lcfg.get(
                "se_context_size",
                -1,
            )
            se_interpolation_mode = lcfg.get(
                "se_interpolation_mode",
                "nearest",
            )
            kernel_size_factor = lcfg.get(
                "kernel_size_factor",
                1.0,
            )
            stride_last = lcfg.get(
                "stride_last",
                False,
            )
            future_context = lcfg.get(
                "future_context",
                -1,
            )

            encoder_layers.append(
                JasperBlock(
                    feat_in,
                    lcfg["filters"],
                    repeat=lcfg["repeat"],
                    kernel_size=lcfg["kernel"],
                    stride=lcfg["stride"],
                    dilation=lcfg["dilation"],
                    dropout=lcfg["dropout"],
                    residual=lcfg["residual"],
                    groups=groups,
                    separable=separable,
                    heads=heads,
                    residual_mode=residual_mode,
                    normalization=normalization_mode,
                    norm_groups=norm_groups,
                    activation=activation,
                    residual_panes=dense_res,
                    conv_mask=conv_mask,
                    se=se,
                    se_reduction_ratio=se_reduction_ratio,
                    se_context_window=se_context_window,
                    se_interpolation_mode=se_interpolation_mode,
                    kernel_size_factor=kernel_size_factor,
                    stride_last=stride_last,
                    future_context=future_context,
                    quantize=False,
                    layer_idx=layer_idx,
                )
            )
            feat_in = lcfg["filters"]

        self._feat_out = feat_in

        self.encoder = torch.nn.Sequential(*encoder_layers)
        self.apply(
            lambda x: init_weights(
                x,
                mode=init_mode,
            )
        )

        self.max_audio_length = 0

    def forward(
        self,
        audio_features,
        lengths,
    ):
        """Returns the output of the encoder.
        Args:
            audio_features (torch.tensor): Input tensor with shape (batch_size, in_feat_dims, time_steps).
            lengths (torch.tensor): Length of the individual input audio feature sequences in the
                batch (batch_size,).
        Returns:
            (torch.tensor): Output of the encoder with shape (batch_size, enc_out_dims, time_steps).
            Note: enc_out_dims (afaik) depends in the out_channels of the last JasperBlock's conv1d layers.
        """

        self.update_max_sequence_length(
            seq_length=audio_features.size(2),
            device=audio_features.device,
        )
        (
            s_input,
            length,
        ) = self.encoder(
            (
                [audio_features],
                lengths,
            )
        )
        # Note: list input is to handle optional dense residual connections (?)
        last_layer = s_input[-1]

        return (
            last_layer,
            lengths,
        )

    def update_max_sequence_length(
        self,
        seq_length: int,
        device,
    ):
        # Find global max audio length across all nodes
        if torch.distributed.is_initialized():
            global_max_len = torch.tensor(
                [seq_length],
                dtype=torch.float32,
                device=device,
            )

            # Update across all ranks in the distributed system
            torch.distributed.all_reduce(
                global_max_len,
                op=torch.distributed.ReduceOp.MAX,
            )

            seq_length = global_max_len.int().item()

        if seq_length > self.max_audio_length:
            if seq_length < 5000:
                seq_length = seq_length * 2
            elif seq_length < 10000:
                seq_length = seq_length * 1.5
            self.max_audio_length = seq_length

            device = next(self.parameters()).device
            seq_range = torch.arange(
                0,
                self.max_audio_length,
                device=device,
            )
            if hasattr(
                self,
                "seq_range",
            ):
                self.seq_range = seq_range
            else:
                self.register_buffer(
                    "seq_range",
                    seq_range,
                    persistent=False,
                )

            # Update all submodules
            for (
                name,
                m,
            ) in self.named_modules():
                if isinstance(
                    m,
                    MaskedConv1d,
                ):
                    m.update_masked_length(
                        self.max_audio_length,
                        seq_range=self.seq_range,
                    )
                elif isinstance(
                    m,
                    SqueezeExcite,
                ):
                    m.set_max_len(
                        self.max_audio_length,
                        seq_range=self.seq_range,
                    )
