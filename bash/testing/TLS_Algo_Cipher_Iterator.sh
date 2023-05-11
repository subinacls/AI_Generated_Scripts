function iterate_algo_cipher_suites() {
  local ip_address=$1;
  local port=$2;
  function validate_address() {
    local vip_address="$1";
    if [[ "${vip_address}" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      if ! [[ "${vip_address}" =~ ^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$ ]]; then
        echo "Invalid IPv4 address: ${vip_address}"
        return 1
      fi
    else
      iptype='ipv4'
      return 0
    fi
    if [[ "${vip_address}" =~ ^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$ ]]; then
      if ! [[ "${vip_address}" =~ ^(([0-9a-fA-F]{1,4}:){6}|::([0-9a-fA-F]{1,4}:){5}|([0-9a-fA-F]{1,4})?::([0-9a-fA-F]{1,4}:){4}|((([0-9a-fA-F]{1,4}:)?[0-9a-fA-F]{1,4})?::([0-9a-fA-F]{1,4}:){3})|((([0-9a-fA-F]{1,4}:){0,2}[0-9a-fA-F]{1,4})?::([0-9a-fA-F]{1,4}:){2})|((([0-9a-fA-F]{1,4}:){0,3}[0-9a-fA-F]{1,4})?::[0-9a-fA-F]{1,4}:)|((([0-9a-fA-F]{1,4}:){0,4}[0-9a-fA-F]{1,4})?::))$ ]]; then
        echo "Invalid IPv6 address: ${vip_address}"
        return 1
      fi
      iptype='ipv6'
      return 0
    fi
    if [[ "${vip_address}" =~ ^\[([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\]$ ]]; then
      return 'ipv6'
    fi
    if [[ "${vip_address}" =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$ ]]; then
      if ! [[ "${vip_address}" =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$ ]]; then
        echo "Invalid FQDN: ${vip_address}"
        return 1
      fi
    else
      iptype='fqdn'
      return 0
    fi
  }
  validate_address $ip_address;
  local tested_ciphers=();
  local failed_ciphers=();
  local secure=("DHE-RSA-AES128-CCM" "DHE-RSA-AES128-GCM-SHA256" "DHE-RSA-AES256-CCM8" "DHE-RSA-AES256-GCM-SHA384" "ECDHE-ECDSA-AES256-CCM" "DHE-RSA-AES256-CCM" "DHE-PSK-AES128-CCM8" "DHE-PSK-AES256-CCM" "TLS_AES_128_CCM_SHA256" "ECDHE-ECDSA-AES128-CCM8" "DHE-RSA-CHACHA20-POLY1305" "ECDHE-RSA-AES256-GCM-SHA384" "ECDHE-ECDSA-AES256-CCM8" "DHE-PSK-AES256-CCM8" "DHE-RSA-AES128-CCM8" "ECDHE-RSA-CHACHA20-POLY1305" "ECDHE-ECDSA-AES128-CCM" "ECDHE-RSA-AES128-GCM-SHA256" "DHE-PSK-AES128-CCM");
  local insecure=("DHE-PSK-NULL-SHA384" "ADH-CAMELLIA128-SHA" "ADH-AES128-GCM-SHA256" "ADH-AES256-SHA" "DHE-PSK-NULL-SHA256" "ADH-CAMELLIA256-SHA" "ADH-CAMELLIA256-SHA256" "PSK-NULL-SHA" "ECDHE-ECDSA-NULL-SHA" "ADH-CAMELLIA128-SHA256" "NULL-MD5" "ADH-AES256-GCM-SHA384" "NULL-SHA256" "PSK-NULL-SHA384" "ADH-AES128-SHA" "DHE-PSK-NULL-SHA" "ADH-SEED-SHA" "ADH-AES256-SHA256" "PSK-NULL-SHA256" "AECDH-AES128-SHA" "ECDHE-PSK-NULL-SHA" "AECDH-NULL-SHA" "AECDH-AES256-SHA" "ECDHE-RSA-NULL-SHA" "RSA-PSK-NULL-SHA" "ECDHE-PSK-NULL-SHA384" "AECDH-DES-CBC3-SHA" "ADH-DES-CBC3-SHA" "RSA-PSK-NULL-SHA256" "ECDHE-PSK-NULL-SHA256" "ADH-AES128-SHA256" "RSA-PSK-NULL-SHA384" "NULL-SHA");
  local weak=("CAMELLIA128-SHA256" "ECDHE-PSK-CAMELLIA256-SHA384" "DHE-RSA-AES256-SHA256" "RSA-PSK-AES256-CBC-SHA" "AES128-SHA" "PSK-AES256-CBC-SHA384" "DHE-DSS-SEED-SHA" "SRP-AES-128-CBC-SHA" "AES128-CCM" "AES256-CCM" "AES128-SHA256" "ECDHE-RSA-AES128-SHA" "RSA-PSK-CAMELLIA128-SHA256" "DHE-DSS-AES128-SHA256" "ECDHE-ECDSA-AES256-SHA" "ECDHE-RSA-DES-CBC3-SHA" "DHE-RSA-CAMELLIA256-SHA256" "RSA-PSK-CAMELLIA256-SHA384" "DHE-DSS-DES-CBC3-SHA" "DHE-RSA-CAMELLIA128-SHA" "CAMELLIA256-SHA" "ECDHE-RSA-CAMELLIA128-SHA256" "PSK-AES256-CBC-SHA" "SRP-RSA-AES-256-CBC-SHA" "ECDHE-ECDSA-CAMELLIA128-SHA256" "DHE-RSA-DES-CBC3-SHA" "PSK-CHACHA20-POLY1305" "ECDHE-ECDSA-AES128-SHA256" "ECDHE-ECDSA-CAMELLIA256-SHA384" "SRP-AES-256-CBC-SHA" "PSK-AES128-CCM8" "SRP-DSS-3DES-EDE-CBC-SHA" "CAMELLIA256-SHA256" "AES256-CCM8" "SRP-RSA-AES-128-CBC-SHA" "DHE-PSK-AES128-CBC-SHA" "DHE-RSA-AES256-SHA" "DHE-RSA-SEED-SHA" "DHE-PSK-AES256-CBC-SHA384" "ECDHE-ECDSA-AES256-SHA384" "ECDHE-PSK-AES128-CBC-SHA" "DHE-RSA-AES128-SHA" "AES128-CCM8" "DHE-RSA-CAMELLIA256-SHA" "ECDHE-ECDSA-DES-CBC3-SHA" "ECDHE-PSK-CAMELLIA128-SHA256" "DHE-RSA-AES128-SHA256" "DHE-DSS-CAMELLIA128-SHA256" "PSK-AES128-CCM" "DHE-DSS-AES256-SHA256" "ECDHE-PSK-3DES-EDE-CBC-SHA" "DHE-PSK-CAMELLIA256-SHA384" "ECDHE-RSA-AES256-SHA384" "SRP-DSS-AES-256-CBC-SHA" "ECDHE-PSK-AES256-CBC-SHA384" "PSK-AES128-CBC-SHA" "ECDHE-RSA-AES256-SHA" "PSK-AES128-CBC-SHA256" "DHE-DSS-CAMELLIA256-SHA" "RSA-PSK-AES128-CBC-SHA256" "SRP-RSA-3DES-EDE-CBC-SHA" "DHE-PSK-3DES-EDE-CBC-SHA" "ECDHE-RSA-AES128-SHA256" "DHE-PSK-AES128-CBC-SHA256" "PSK-CAMELLIA256-SHA384" "ECDHE-PSK-AES128-CBC-SHA256" "DHE-DSS-CAMELLIA256-SHA256" "RSA-PSK-AES128-CBC-SHA" "PSK-3DES-EDE-CBC-SHA" "RSA-PSK-AES256-GCM-SHA384" "RSA-PSK-AES256-CBC-SHA384" "DHE-RSA-CAMELLIA128-SHA256" "PSK-CAMELLIA128-SHA256" "RSA-PSK-CHACHA20-POLY1305" "ECDHE-RSA-CAMELLIA256-SHA384" "AES256-SHA256" "SRP-DSS-AES-128-CBC-SHA" "DHE-DSS-CAMELLIA128-SHA" "DHE-DSS-AES128-SHA" "DHE-DSS-AES256-SHA" "DHE-PSK-AES256-CBC-SHA" "PSK-AES128-GCM-SHA256" "PSK-AES256-GCM-SHA384" "AES256-GCM-SHA384" "SEED-SHA" "PSK-AES256-CCM" "RSA-PSK-AES128-GCM-SHA256" "DES-CBC3-SHA" "ECDHE-PSK-AES256-CBC-SHA" "PSK-AES256-CCM8" "AES128-GCM-SHA256");
  local recommended=("DHE-PSK-AES256-GCM-SHA384" "ECDHE-ECDSA-CHACHA20-POLY1305" "ECDHE-ECDSA-AES256-GCM-SHA384" "ECDHE-PSK-CHACHA20-POLY1305" "DHE-DSS-AES128-GCM-SHA256" "DHE-PSK-AES128-GCM-SHA256" "ECDHE-ECDSA-AES128-GCM-SHA256" "DHE-PSK-CHACHA20-POLY1305" "TLS_AES_128_GCM_SHA256" "TLS_AES_256_GCM_SHA384" "DHE-DSS-AES256-GCM-SHA384");
  local required_ciphers=("ECDHE-ECDSA-AES256-GCM-SHA384" "ECDHE-ECDSA-CHACHA20-POLY1305" "ECDHE-RSA-AES256-GCM-SHA384" "ECDHE-RSA-CHACHA20-POLY1305" "DHE-RSA-AES256-GCM-SHA384" "DHE-RSA-AES256-CCM" "ECDHE-ECDSA-AES128-GCM-SHA256" "ECDHE-RSA-AES128-GCM-SHA256");
  for version in tls1_2 tls1_3; do
    for cipher in ${required_ciphers[@]}; do
      [[ "${tested_ciphers[@]}" =~ "$version:$cipher" ]] && continue || tested_ciphers+=($version:$cipher);
      [[ "$iptype" =~ "ipv4" || "$iptype" =~ "fqdn" ]] && target="$ip_address:$port";
      [[ "$iptype" =~ "ipv6" && "$ip_address" =~ ^\[(.*)\]$ ]] && target="$ip_address:$port" || target="[$ip_address]:$port";
      res=`echo | openssl s_client -$version -cipher $cipher -connect $target 2>&1 | grep " Cipher "`;
      [[ "$res" =~ "Cipher" ]] && echo "[PASS] $version : $cipher : Required cipher supported" || echo "[ALERT] $version : $cipher : Required cipher NOT supported";
    done;
  done;
  for version in ssl3 tls1 tls1_1 tls1_2 tls1_3; do
    for cipher in $(openssl ciphers -v ALL:NULL 2>&1 | cut -d " " -f1); do
      [[ "$cipher" =~ "error" && ! ${failed_ciphers[@]} =~ "$version:$cipher" ]] && failed_ciphers+=("$version:$cipher") && continue;
      [[ "${required_ciphers[@]}" =~ "$cipher" ]] && continue;
      [[ "${tested_ciphers[@]}" =~ "$version:$cipher" ]] && continue || tested_ciphers+=($version:$cipher);
      [[ "$iptype" =~ "ipv4" || "$iptype" =~ "fqdn" ]] && target="$ip_address:$port";
      [[ "$iptype" =~ "ipv6" && "$ip_address" =~ ^\[(.*)\:(.*)\]$ ]] && target="$ip_address:$port" || target="[$ip_address]:$port";
      res=`echo | openssl s_client -$version -cipher $cipher -connect $target 2>&1 | grep " Cipher "`;
      [[ "$res" =~ "Cipher" && ${insecure[@]} =~ "$cipher" ]] && echo -e "[FAIL] $version : $cipher : Known Insecure Cipher";
      [[ "$res" =~ "Cipher" && ${weak[@]} =~ "$cipher" ]] && echo -e "[WEAK] $version : $cipher : Known Weak Cipher";
      [[ "$res" =~ "Cipher" && ${recommended[@]} =~ "$cipher" ]] && echo -e "[PASS] $version : $cipher : Recommended Cipher being used";
      [[ "$res" =~ "Cipher" && ${secure[@]} =~ "$cipher" ]] && echo -e "[PASS] $version : $cipher : Secure Cipher being used";
      [[ "$res" =~ "Cipher" && ! ${secure[@]} =~ "$cipher" && ! ${recommended[@]} =~ "$cipher" && ! ${weak[@]} =~ "$cipher" && ! ${insecure[@]} =~ "$cipher" && ! ${required_ciphers[@]} =~ "$cipher" ]] && echo -e "[ALERT] $version : $cipher : Unknown Cipher being used";
    done;
  done;
  echo -e "[TESTED CIPHERS] ${tested_ciphers[@]}";
}; # iterate_algo_cipher_suites google.com 443
