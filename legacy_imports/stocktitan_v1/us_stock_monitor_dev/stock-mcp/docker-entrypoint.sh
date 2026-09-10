#!/bin/sh
set -eu

load_secret() {
  var_name="$1"
  file_var_name="${var_name}_FILE"
  eval "var_value=\${$var_name:-}"
  eval "file_value=\${$file_var_name:-}"

  if [ -n "$var_value" ] && [ -n "$file_value" ]; then
    echo "WARN: both $var_name and $file_var_name are set, using $var_name" >&2
    return
  fi

  if [ -n "$file_value" ]; then
    if [ ! -f "$file_value" ]; then
      echo "ERROR: secret file not found for $file_var_name: $file_value" >&2
      exit 1
    fi
    secret_value="$(tr -d '\r\n' < "$file_value")"
    export "$var_name=$secret_value"
  fi
}

load_secret "DB_PASSWORD"
load_secret "APP_SECURITY_API_KEY"
load_secret "MAIL_PASSWORD"

exec java -jar /app/app.jar
