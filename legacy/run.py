from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os

import six
from rasa_dm.channels import HttpInputChannel
from rasa_dm.channels.facebook import FacebookInput
from rasa_dm.channels.console import ConsoleInputChannel
from rasa_dm.agent import Agent
from rasa_dm.interpreter import RasaNLUInterpreter

if six.PY2:
    nlu_model_path = 'models/nlu/current_py2'
else:
    nlu_model_path = 'models/nlu/current_py3'


def run_rasa(serve_forever=True):
    agent = Agent.load("models/policy/current",
                       interpreter=RasaNLUInterpreter(nlu_model_path))
    
    input_channel = FacebookInput(
        os.environ.get("FACEBOOK_VERIFY_TOKEN", ""),
        os.environ.get("FACEBOOK_APP_SECRET", "").encode("utf-8"),
        {
            os.environ.get("FACEBOOK_PAGE_ID", ""):
                os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        },
        True,
    )

    if serve_forever:
        agent.handle_channel(HttpInputChannel(5004, "/app", input_channel))
    return agent

if __name__ == '__main__':
    logging.basicConfig(level="INFO")
    run_rasa()
