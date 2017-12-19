from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import json
import os

import numpy as np
import rasa_dm
from builtins import str
from rasa_dm.trackers import DialogueStateTracker
from rasa_dm.util import create_dir_for_file, class_from_module_path
from typing import Text, List, Optional


class PolicyEnsemble(object):
    def __init__(self, policies):
        self.policies = policies

    def train(self, X, y, domain, featurizer, **kwargs):
        for policy in self.policies:
            policy.prepare(featurizer, X.shape[1])
            policy.train(X, y, domain, **kwargs)

    def predict_next_action(self, tracker, domain):
        # type: (DialogueStateTracker, Domain) -> (float, int)
        """Predicts the next action the bot should take after seeing x.

        This should be overwritten by more advanced policies to use ML to predict the action.
        Returns the index of the next action"""
        probabilities = self.probabilities_using_best_policy(tracker, domain)
        max_index = np.argmax(probabilities)
        return max_index

    def probabilities_using_best_policy(self, tracker, domain):
        raise NotImplementedError

    def _persist_metadata(self, path, max_history):
        # type: (Text, List[Text]) -> None
        """Persists the domain specification to storage."""

        domain_spec_path = os.path.join(path, 'policy_metadata.json')
        create_dir_for_file(domain_spec_path)
        metadata = {
            "rasa_core": rasa_dm.__version__,
            "max_history": max_history,
            "ensemble_name": self.__module__ + "." + self.__class__.__name__,
            "policy_names": [p.__module__ + "." + p.__class__.__name__ for p in self.policies]
        }
        with io.open(domain_spec_path, 'w') as f:
            f.write(str(json.dumps(metadata, indent=2)))

    def persist(self, path):
        # type: (Text) -> None
        """Persists the policy to storage."""

        self._persist_metadata(path, self.policies[0].max_history if self.policies else None)

        for policy in self.policies:
            policy.persist(path)

    @classmethod
    def load_metadata(cls, path):
        matadata_path = os.path.join(path, 'policy_metadata.json')
        with io.open(matadata_path) as f:
            metadata = json.loads(f.read())
        return metadata

    @classmethod
    def load(cls, path, featurizer):
        # type: (Text, Optional[Domain]) -> PolicyEnsemble
        """Loads policy and domain specification from storage"""

        metadata = cls.load_metadata(path)
        policies = []
        for policy_name in metadata["policy_names"]:
            policy = class_from_module_path(policy_name).load(path)
            policy.featurizer = featurizer
            policy.max_history = metadata["max_history"]
            policies.append(policy)
        ensemble = class_from_module_path(metadata["ensemble_name"])(policies)
        return ensemble


class SimplePolicyEnsemble(PolicyEnsemble):
    def __init__(self, policies):
        super(SimplePolicyEnsemble, self).__init__(policies)

    def probabilities_using_best_policy(self, tracker, domain):
        result = None
        max_confidence = -1
        for p in self.policies:
            probabilities = p.predict_action_probabilities(tracker, domain)
            confidence = np.max(probabilities)
            if confidence > max_confidence:
                max_confidence = confidence
                result = probabilities
        return result
