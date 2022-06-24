#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   caden1225@163.com

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/1/5 下午3:48   caden      1.0         None
"""

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.core.params import ParlaiParser
from blenderbot2.agents import create_agent
from parlai.core.worlds import create_task
from typing import Dict, Any
from parlai.core.script import ParlaiScript, register_script
from parlai.agents.local_human.local_human import LocalHumanAgent
from parlai.utils.world_logging import WorldLogger

SHARED: Dict[Any, Any] = {}


def setup_interactive_args(parser=None):
    if parser is None:
        parser = ParlaiParser(
            True, True, 'Interactive chat with a model on the command line'
        )
    parser.add_argument(
        '-it',
        '--interactive-task',
        type='bool',
        default=True,
        help='Create interactive version of task',
    )
    parser.add_argument(
        '--outfile',
        type=str,
        default='',
        help='Saves a jsonl file containing all of the task examples and '
             'model replies. Set to the empty string to not save at all',
    )
    parser.add_argument(
        '--save-format',
        type=str,
        default='conversations',
        choices=['conversations', 'parlai'],
        help='Format to save logs in. conversations is a jsonl format, parlai is a text format.',
    )
    parser.set_defaults(interactive_mode=True, task='interactive')
    LocalHumanAgent.add_cmdline_args(parser, partial_opt=None)
    WorldLogger.add_cmdline_args(parser, partial_opt=None)
    print(parser.parse_kwargs())
    return parser


def interactive_api(opt):
    global SHARED

    print("#################################### initialing the blenderbot model and agent#############################")
    agent = create_agent(opt, requireModelExists=True)
    agent.opt.log()
    human_agent = LocalHumanAgent(opt)
    world_logger = WorldLogger(opt) if opt.get('outfile') else None

    SHARED['opt'] = agent.opt
    SHARED['agent'] = agent
    SHARED['world_loger'] = world_logger
    SHARED['world'] = create_task(opt, [human_agent, agent])


@register_script('interactive_api', aliases=['iweb'], hidden=True)
class InteractiveWeb(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_interactive_args()

    def run(self):
        return interactive_api(self.opt)

