# Copyright 2021 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Covertype training pipeline DSL."""

import os
import kfp
import tensorflow_model_analysis as tfma

from absl import app
from absl import flags


from ml_metadata.proto import metadata_store_pb2

from tfx.components import Evaluator
from tfx.components import CsvExampleGen
from tfx.components import ExampleValidator
from tfx.components import ImporterNode
from tfx.components import Pusher
from tfx.components import ResolverNode
from tfx.components import SchemaGen
from tfx.components import StatisticsGen
from tfx.components import Trainer
from tfx.components import Transform
from tfx.components.trainer import executor as trainer_executor
from tfx.dsl.experimental import latest_blessed_model_resolver
from tfx.dsl.components.base import executor_spec
from tfx.extensions.google_cloud_ai_platform.pusher import executor as ai_platform_pusher_executor
from tfx.extensions.google_cloud_ai_platform.trainer import executor as ai_platform_trainer_executor
from tfx.extensions.google_cloud_ai_platform.tuner.component import Tuner
from tfx.orchestration import pipeline
from tfx.orchestration import data_types
from tfx.orchestration.metadata import sqlite_metadata_connection_config
from tfx.orchestration.kubeflow.proto import kubeflow_pb2
from tfx.proto import example_gen_pb2
from tfx.proto import evaluator_pb2
from tfx.proto import pusher_pb2
from tfx.proto import trainer_pb2
from tfx.proto import tuner_pb2
from tfx.types import Channel
from tfx.types.standard_artifacts import Model
from tfx.types.standard_artifacts import ModelBlessing
from tfx.types.standard_artifacts import Schema

from typing import Optional, Dict, List, Text, Union, Any

import features

def create_pipeline(
    pipeline_name: Text, 
    pipeline_root: Text,
    data_root_uri: Union[Text, data_types.RuntimeParameter],
    output_config: example_gen_pb2.Output,
    beam_pipeline_args: List[Text],
    metadata_connection_config: Optional[metadata_store_pb2.ConnectionConfig] = None) -> pipeline.Pipeline:

  
    # Brings data into the pipeline and splits the data into training and eval splits
    #output_config = example_gen_pb2.Output(
    #  split_config=example_gen_pb2.SplitConfig(splits=[
    #      example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=4),
    #      example_gen_pb2.SplitConfig.Split(name='test', hash_buckets=1)
    #  ]))
  
    examplegen = CsvExampleGen(input_base=data_root_uri,
                               output_config=output_config)
  
  
    components=[
        examplegen, 
    ]
  
    return pipeline.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        enable_cache=False,
        beam_pipeline_args=beam_pipeline_args,
        metadata_connection_config=metadata_connection_config
    )
  
  
  