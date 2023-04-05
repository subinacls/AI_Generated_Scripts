find_writable_directories() {
  echo "Writable Directories for $(whoami):"
  echo "----------------------------------------"
  find / -type d -writable -user $(whoami) 2>/dev/null
}
