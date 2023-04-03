"""
This script will find the ssh-keygen binary, search for existing SSH keys, and attempt to create a temporary SSH key pair. 
The temporary key pair will be deleted after the script finishes execution. If the script encounters any issues, 
it will report the corresponding failure message.
"""

find_and_check_ssh_keygen() {
    ssh_keygen_binary=$(which ssh-keygen)
    if [[ -z "$ssh_keygen_binary" ]]; then
        echo "[FAIL] ssh-keygen binary not found."
        return 1
    fi
    if [[ $EUID -eq 0 ]]; then
        for user_home in $(awk -F: '{ print $6 }' /etc/passwd); do
            if [[ -e "${user_home}/.ssh/id_rsa" ]] || [[ -e "${user_home}/.ssh/id_rsa.pub" ]]; then
                echo "[PASS] SSH key found for user in ${user_home}/.ssh/"
            fi
        done
    else
        if [[ -e "${HOME}/.ssh/id_rsa" ]] || [[ -e "${HOME}/.ssh/id_rsa.pub" ]]; then
            echo "[PASS] SSH key found in ${HOME}/.ssh/"
        else
            temp_key=$(mktemp)
            temp_key_pub="${temp_key}.pub"
            trap 'rm -f "$temp_key" "$temp_key_pub"' EXIT

            if $ssh_keygen_binary -q -t rsa -b 2048 -N "" -f "$temp_key" >/dev/null 2>&1; then
                echo "[PASS] Temporary SSH key pair generated successfully."
            else
                echo "[FAIL] Temporary SSH key pair DID NOT generated successfully."
                return 1
            fi
        fi
    fi
}; # find_and_check_ssh_keygen
