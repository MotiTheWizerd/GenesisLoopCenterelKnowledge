"""
Memory Service V2 - Updated for new memory structure
Handles all memory operations with the new Ray memory format
"""

import json
import os
import faiss
import time
import sys
import numpy as np
from datetime import