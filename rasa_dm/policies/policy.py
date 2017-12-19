from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import json
import logging
import os

import numpy as np
from builtins import object, str
from numpy.core.records import ndarray
from typing import Any
from typing import List
from typing import Optional
from typing import Text

from rasa_dm.domain import Domain
from rasa_dm.featurizers import Featurizer, BinaryFeaturizer
from rasa_dm.trackers import DialogueStateTracker
from rasa_dm.util import create_dir_for_file

logger = logging.getLogger(__name__)


class Policy(object):
    SUPPORTS_ONLINE_TRAINING = False
    MAX_HISTORY_DEFAULT = 3

    def __init__(self):
        # type: (Optional[Featurizer]) -> None

        self.featurizer = BinaryFeaturizer()
        self.max_history = self.MAX_HISTORY_DEFAULT

    def featurize(self, tracker, domain):
        # type: (DialogueStateTracker, Domain) -> ndarray
        """Transform tracker into a vector representation.

        The tracker, consisting of multiple turns, will be transformed
        into a float vector which can be used by a ML model."""

        x = domain.feature_vector_for_tracker(self.featurizer, tracker, self.max_history)
        return np.array(x)

    def predict_action_probabilities(self, tracker, domain):
        # type: (DialogueStateTracker, Domain) -> List[float]

        return []

    def prepare(self, featurizer, max_history):
        self.featurizer = featurizer
        self.max_history = max_history

    def train(self, X, y, domain, **kwargs):
        # type: (ndarray, List[int], Domain, **Any) -> None
        """Trains the policy on given training data."""

        raise NotImplementedError

    def continue_training(self, X, y, domain, **kwargs):
        """Continues training an already trained policy.

        This doesn't need to be supported by every policy. If it is supported, the policy can be used for
        online training and the implementation for the continued training should be put into this function."""
        pass

    def persist(self, path):
        # type: (Text) -> None
        """Persists the policy to storage."""

        pass

    @classmethod
    def load(cls, path):
        raise NotImplementedError
