#!/bin/bash

# This approach has been tested against `macOS 15.1.1` and a Unifi Cloud Key Gen 1 running controller version `7.2.97`.
# Your environment might be different and these steps might need to be modified. **Running the script from within a
# virtual environment is not recommended.**
#
# ***By using this script, you agree that you're using it at your own risk.***
#
# Setting Up the Environment
# To make the script run as autonomously as possible, you need to create key-based authentication credentials so that the
# script can log into the controller without needing to enter a username or password (ey-based authentication is
# considered superior to username/password logins).
#
# Create an Authentication Key
# Generate SSH Key Pair (if you don't already have one): On the local machine (the one you’ll use to run the script),
# generate an SSH key pair if you don't already have one:
#
#    `ssh-keygen -t ed25519`
#
# Follow the prompts to save the key. By default, it'll save the key to `~/.ssh/id_ed25519`. If you want to save it
# with a different name, specify the file path during the generation process.
#
# Copy the Public Key to the UniFi controller: You need to copy your public key (`~/.ssh/id_ed25519.pub`) to the UniFi
# controller’s authorized_keys file for SSH access:
#
#    `ssh-copy-id -i ~/.ssh/id_ed25519.pub admin@10.0.1.123`
#
# This will add your public key to the controller's `~/.ssh/authorized_keys` file. If you've completed these steps
# successfully, you should be able to ssh into the controller without entering a password. You can test this with the
# following command:
#
#    `ssh USERNAME@10.0.1.123`

# Config
HOST="10.0.1.123"                               # TODO: Replace with your UniFi Cloud Key IP address
USER="Dave"                                     # TODO: Replace with your SSH username
PRIVATE_KEY_PATH="/Users/Dave/.ssh/id_ed25519"  # TODO: Path to your private key (default: ~/.ssh/id_ed25519)
BACKUP_FOLDER="/data/autobackup"                # TODO: Path to the backup directory on the Cloud Key
LOCAL_FOLDER="/Users/Dave/Temp/unifi"           # TODO: Local directory to store backups

# Ensure local backup directory exists
mkdir -p "$LOCAL_FOLDER"

# Use SCP to copy backup files from the Cloud Key to local directory
echo "Copying files from $HOST to $LOCAL_FOLDER..."

# Loop to copy files over SSH with key-based auth
for backup_file in $(ssh -i "$PRIVATE_KEY_PATH" "$USER@$HOST" "ls $BACKUP_FOLDER"); do
    remote_file="$BACKUP_FOLDER/$backup_file"
    local_file="$LOCAL_FOLDER/$backup_file"

    # If the file is autobackup_meta.json, replace it even if it exists. This way, the file references the most
    # current backup file set.
    if [ "$backup_file" == "autobackup_meta.json" ]; then
        echo "Replacing $local_file (autobackup_meta.json)"
        scp -i "$PRIVATE_KEY_PATH" "$USER@$HOST:$remote_file" "$LOCAL_FOLDER"
    # Skip other files if they already exist locally
    elif [ -f "$local_file" ]; then
        echo "Skipping $local_file (already exists)"
    # Copy anything not covered above
    else
        echo "Copying $remote_file to $LOCAL_FOLDER..."
        scp -i "$PRIVATE_KEY_PATH" "$USER@$HOST:$remote_file" "$LOCAL_FOLDER"
    fi
done

echo "Backup completed."
