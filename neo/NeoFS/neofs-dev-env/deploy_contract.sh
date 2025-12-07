#!/bin/bash

# -------------------------------------------
# HARDCODED DEMO SETTINGS
# -------------------------------------------
# The account sending the GAS (Must match 'owner_key' arg)
OWNER_WALLET="6PYP7YrwGnLuu4WYQbEe3WJiC44aKmqwqawLsp7H3oh5vocS9xTv2ZfTp3" 
# The name/hash of your contract after deployment
CONTRACT_NAME="campaign_managerV3.py" 
echo "Starting"
# -------------------------------------------
# INPUTS
# -------------------------------------------
# Usage: ./run_demo.sh <user_address> <amount> <exp_id> <transcript_id>
USER_ADDR="NQk8BNTQRgAL4BFzJc8rM9V78A7BVeii2R"
AMOUNT=$2
EXP_ID=$3
TRANS_ID=$4



# -------------------------------------------
# EXECUTION
# -------------------------------------------

echo ">>> Running Campaign Manager Demo..."
echo "Sending $AMOUNT to $USER_ADDR for Experiment $EXP_ID..."

# Invokes the 'deploy' method in your python contract
# Arguments match the Python signature: owner_key, user_key, amount, experiment_id, transcript_id
neoxp contract invoke $CONTRACT_NAME deploy \
  $OWNER_WALLET \
  $USER_ADDR \
  $AMOUNT \
  $EXP_ID \
  $TRANS_ID \
  --account $OWNER_WALLET \
  --gas 10

echo ">>> Done."