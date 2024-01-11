import pytest
import re

# modules to test
from src.inventory import Inventory


def test_Inventory():
    inventory = Inventory()
    assert inventory.filepath == inventory.timestamp.isoformat()
    inventory.filepath = "tmp/test.json"
    inventory.ext = ".edgelist"
    assert inventory.filepath == "tmp/test.edgelist"
    inventory.dirname = "tts/"
    assert inventory.filepath == "tts/test.edgelist"
    inventory.filename = "tts"
    assert inventory.filepath == "tts/tts.edgelist"
    