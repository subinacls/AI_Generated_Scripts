get_unknown_process_id() {
    # Attempt to use 'ps' to get process information
    if command -v ps >/dev/null; then
        ps_output=$(ps -A xf)
        unknown_processes=$(echo "$ps_output" | grep -v "$(basename "$0")" | grep -v -e "\[")
        if [ -n "$unknown_processes" ]; then
            echo "$unknown_processes" | awk '{print $1}'
            return 0
        fi
    fi
    # Attempt to use 'top' to get process information
    if command -v top >/dev/null; then
        top_output=$(top -b -n 1)
        unknown_processes=$(echo "$top_output" | grep -v "$(basename "$0")" | grep -v -e "\[")
        if [ -n "$unknown_processes" ]; then
            echo "$unknown_processes" | awk '{print $1}'
            return 0
        fi
    fi
    # Attempt to use the /proc folder to get process information
    for pid_folder in /proc/*/; do
        pid=$(basename "$pid_folder")
        if [ "$pid" -eq "$pid" ] 2>/dev/null; then
            if ! grep -q "^Name:" "$pid_folder/status" 2>/dev/null; then
                continue
            fi
            if ! grep -q "^PPid:" "$pid_folder/status" 2>/dev/null; then
                continue
            fi
            ppid=$(grep "^PPid:" "$pid_folder/status" | awk '{print $2}')
            if [ "$ppid" -eq "1" ] && ! ps -p "$pid" >/dev/null; then
                echo "$pid"
                return 0
            fi
        fi
    done
    echo "No unknown processes found."
    return 1
}
