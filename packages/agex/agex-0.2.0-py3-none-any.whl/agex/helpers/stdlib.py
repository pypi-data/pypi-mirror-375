"""
Standard library registration helpers for agex agents.

This module provides helper functions to register useful Python standard
library modules with agents, focusing on safe mathematical, utility, and
data processing modules.
"""

import base64
import collections
import csv
import datetime
import decimal
import fractions
import hashlib
import io
import json
import math
import os
import random
import re
import statistics
import string
import tempfile
import textwrap
import time
import typing
import uuid

from agex.agent import Agent

# Exclude global state functions from random module
RANDOM_EXCLUDE = [
    "_*",
    "seed",
    "getstate",
    "setstate",
    "SystemRandom",
]


def register_stdlib(agent: Agent, io_friendly: bool = False) -> None:
    """Register useful Python standard library modules with the agent."""

    # Mathematical modules
    agent.module(math, visibility="low")
    agent.module(random, visibility="low", exclude=RANDOM_EXCLUDE)
    agent.module(statistics, visibility="low")
    agent.module(decimal, visibility="low")
    agent.module(fractions, visibility="low")
    agent.module(time, visibility="low")

    # Utility modules
    agent.module(collections, visibility="low")

    # Date/time modules
    agent.module(datetime, visibility="low")
    agent.cls(datetime.datetime, visibility="low")
    agent.cls(datetime.date, visibility="low")
    agent.cls(datetime.time, visibility="low")
    agent.cls(datetime.timedelta, visibility="low")
    agent.cls(datetime.timezone, visibility="low")
    agent.cls(datetime.tzinfo, visibility="low")

    # String and text processing
    agent.module(re, visibility="low")
    agent.module(string, visibility="low")
    agent.module(textwrap, visibility="low")

    # Data encoding/processing
    agent.module(json, visibility="low")
    agent.module(csv, visibility="low")
    agent.module(base64, visibility="low")
    agent.module(uuid, visibility="low")
    agent.module(hashlib, visibility="low")

    # IO and temporary file handling
    agent.module(tempfile, visibility="low")
    if io_friendly:
        agent.module(io, visibility="low")
        agent.module(os, visibility="low")
    else:
        agent.module(
            io, visibility="low", include=["BytesIO", "StringIO", "TextIOWrapper"]
        )
    agent.module(typing, visibility="low")
