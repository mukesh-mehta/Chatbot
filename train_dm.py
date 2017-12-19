from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from actions import RasaPolicy
from rasa_dm.agent import Agent
from rasa_dm.policies.memoization import MemoizationPolicy


def train_rasa_dm():
    training_data_file = 'data/stories.md'
    model_path = 'models/policy/current_'

    agent = Agent("domain.yml",
                  policies=[MemoizationPolicy(), RasaPolicy()])
    
    agent.train(
        training_data_file,
        max_history=41,
        epochs=50,
        batch_size=50,
        validation_split=0.2,
	    augmentation_factor=1
    )

    agent.persist(model_path)


if __name__ == '__main__':
    logging.basicConfig(level="DEBUG")
    train_rasa_dm()
