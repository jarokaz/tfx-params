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

import time

from absl import app
from absl import flags
from absl import logging

import kfp



FLAGS = flags.FLAGS

# Runner settings
flags.DEFINE_string('project_id', 'jk-mlops-dev', 'Project ID')
flags.DEFINE_string('pipeline_id', None, 'Pipeline ID')
flags.DEFINE_string('endpoint', 'https://73d294ebbe6dd109-dot-us-central1.pipelines.googleusercontent.com', 'KFP endpoint')
flags.DEFINE_string('experiment_name', 'Default', 'Experiment ID')
flags.DEFINE_string('pipeline_name', 'covertype-training', 'Pipeline name')
flags.DEFINE_string('pipeline_root', 'gs://jk-ucaip-demos/covertype/pipeline_root', 'Pipeline root')
#flags.mark_flag_as_required('pipeline_root')
flags.mark_flag_as_required('pipeline_id')


def main(argv):
    del argv
    
    client = kfp.Client(host=FLAGS.endpoint)
    
    #response = client.list_pipelines()
    
    params = {
        'data-root-uri': 'gs://workshop-datasets/covertype/small',
        'pipeline-root': FLAGS.pipeline_root,
        'eval-split-name': 'eval1'
    }
    
    response = client.get_experiment(experiment_name=FLAGS.experiment_name)
    experiment_id = response.id
    
    job_name = 'run-'+ time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    
    response = client.run_pipeline(
        experiment_id=experiment_id,
        job_name=job_name,
        pipeline_id=FLAGS.pipeline_id,
        params=params
    )
    
    
    print(experiment_id)
    
        
if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    app.run(main)

 



