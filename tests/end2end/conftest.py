import os
import sys

STRICTDOC_PATH = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.exists(STRICTDOC_PATH), "does not exist: {}".format(
    STRICTDOC_PATH
)
sys.path.append(STRICTDOC_PATH)
