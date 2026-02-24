#!/bin/bash
# Wrapper script for launchd background service

# 1. Source the Conda initialization from its exact prefix
source "/opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh"

# 2. Activate the avatar environment
conda activate avatar

# 3. Navigate to the project directory
cd "/Users/alyasi/MyProjects/AvatarAgentPlan/avatar-agent"

# 4. Use exec to replace the bash shell with uvicorn (better for signals/stopping)
# We bind it to 0.0.0.0 so it can be accessed on the local network if needed
exec uvicorn app:app --host 0.0.0.0 --port 8000
