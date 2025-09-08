#!/usr/bin/env bash

# Make sure we have values in important variables
[[ -z "{{ virtualhosts_root }}" ]] && exit 1
[[ -z "{{ username }}" ]] && exit 2

# Make sure this user's backup directory is present - exit if not
[[ -d "{{ virtualhosts_root }}/{{ username }}/backup" ]] || exit 3

# Make sure we can make backups before we delete any
[[ -x /usr/local/vg_tools/vg_management/sbin/backup_virtualhost ]] || exit 4

# Remove any backups older than three weeks
find "/{{ virtualhosts_root }}/{{ username }}/backup" -type f -mtime +21 -print0 | xargs -0 rm -f >> /dev/null 2>&1

nice /usr/local/vg_tools/vg_management/sbin/backup_virtualhost -r "{{ virtualhosts_root }}" "{{ username }}" >> /dev/null 2>&1
