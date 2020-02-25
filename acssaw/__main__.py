
"""
Main Cloud Wrapper entrypoint
"""
from cloud_wrapper.launcher import launch
import sys

# Call analytics method
if __name__ == "__main__":
    launch(sys.argv)
