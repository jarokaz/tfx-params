# Lint as: python2, python3
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Local runner configuration"""


from absl import app
from absl import flags
from absl import logging

from tfx.dsl.components.base import executor_spec
from tfx.components.trainer import executor as trainer_executor
from tfx.extensions.google_cloud_ai_platform.trainer import executor as ai_platform_trainer_executor

from tfx.orchestration import data_types
#from tfx.orchestration.kubeflow.v2 import kubeflow_v2_dag_runner
from tfx.orchestration.kubeflow import kubeflow_dag_runner
from tfx.orchestration.local.local_dag_runner import LocalDagRunner
from tfx.orchestration.metadata import sqlite_metadata_connection_config

from tfx.proto import example_gen_pb2

from google.protobuf import json_format
from google.protobuf import text_format

import pipeline 





def _compile_pipeline(pipeline_def, 
                     project_id,
                     pipeline_name,
                     pipeline_image,
                     pipeline_spec_path):
    """Compiles the pipeline."""

    metadata_config = kubeflow_dag_runner.get_default_kubeflow_metadata_config()
    
    runner_config = kubeflow_dag_runner.KubeflowDagRunnerConfig(
      kubeflow_metadata_config=metadata_config,
      # Specify custom docker image to use.
      # tfx_image=tfx_image
    )
    
    runner = kubeflow_dag_runner.KubeflowDagRunner(
        config=runner_config,
        output_filename=pipeline_spec_path)

    # Compile the pipeline
    runner.run(pipeline_def)
    
    


FLAGS = flags.FLAGS

# Runner settings
flags.DEFINE_string('project_id', 'jk-mlops-dev', 'Project ID')
flags.DEFINE_string('pipeline_spec_path', 'pipeline.yaml', 'Pipeline spec path')

# Pipeline compile time settings
flags.DEFINE_string('pipeline_name', 'covertype-training', 'Pipeline name')
flags.DEFINE_string('pipeline_image', 'gcr.io/jk-mlops-dev/covertype-tfx', 'Pipeline container image')

# Runtime parameters
flags.DEFINE_string('data_root_uri', 'gs://workshop-datasets/covertype/small', 'Data root')
flags.DEFINE_string('pipeline_root', 'gs://jk-ucaip-demos/covertype/pipeline_root', 'Pipeline root')
#flags.mark_flag_as_required('pipeline_root')


def main(argv):
    del argv

    beam_pipeline_args = [
            '--direct_running_mode=multi_processing',
            # 0 means auto-detect based on on the number of CPUs available
            # during execution time.
            '--direct_num_workers=0' ] 

    
    metadata_connection_config = None
    data_root_uri = data_types.RuntimeParameter( 
        name='data-root-uri',
        ptype=str,
        default=FLAGS.data_root_uri)
    
    eval_split_name = data_types.RuntimeParameter(
        name='eval-split-name',
        ptype=str,
        default='eval'
    )
     
    #output_config = example_gen_pb2.Output(
    #    split_config=example_gen_pb2.SplitConfig(splits=[
    #        example_gen_pb2.SplitConfig.Split(name=eval_split_name, hash_buckets=4),
    #        example_gen_pb2.SplitConfig.Split(name='test', hash_buckets=1)]))
    
    output_config = {
        "split_config": {
            "splits": [
                {
                    "name": "train",
                    "hash_buckets": 4
                },
                {
                    "name": eval_split_name,
                    "hash_buckets": 1
                }
            ]
        }
    }
  

    # Create the pipeline
    pipeline_def = pipeline.create_pipeline(
        pipeline_name=FLAGS.pipeline_name,
        pipeline_root=FLAGS.pipeline_root,
        data_root_uri=data_root_uri,
        output_config=output_config,
        beam_pipeline_args=beam_pipeline_args,
        metadata_connection_config=metadata_connection_config)

    logging.info(f'Compiling pipeline to: {FLAGS.pipeline_spec_path}')
    metadata_config = kubeflow_dag_runner.get_default_kubeflow_metadata_config()
    
    runner_config = kubeflow_dag_runner.KubeflowDagRunnerConfig(
        kubeflow_metadata_config=metadata_config,
        # Specify custom docker image to use.
        # tfx_image=tfx_image
    )
    
    runner = kubeflow_dag_runner.KubeflowDagRunner(
        config=runner_config,
        output_filename=FLAGS.pipeline_spec_path)

    runner.run(pipeline_def)


        
if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    app.run(main)

 



