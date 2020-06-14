#!/bin/bash
# Create pages on Mediawiki with information from Ansible

# Create a config file with the following keys:
#ANSIBLE_DIR="/opt/ansible/projects/myproject"
#FACTS_CACHE="$ANSIBLE_DIR/cache"
#MAIN_PLAYBOOK="main.yml"
#WIKI="root@wiki"

. /opt/ansible/facts2mediawiki.conf

cd $ANSIBLE_DIR
# The following variable controls when the page of a host should be stale and marked as such
STALE=$(date -d '2 weeks ago' +%s)

###
# Generate per host status page
###
for HOST_NAME in $(ansible-playbook playbooks/$MAIN_PLAYBOOK --list-hosts | tail -n+7)
do
    [[ $HOST_NAME == '' ]] && continue
    STALE_NOTE=''

    [[ ! -f $FACTS_CACHE/$HOST_NAME ]] && {
      cat <<EOF >/tmp/INV:${HOST_NAME%%.*}.wiki
  Hostname: ${HOST_NAME%%.*}
  No further information available, this host hasn't been inventoried by Ansible just yet.

  Inventory date: $(date "+%Y/%m/%d %H:%M:%S")

  This page is generated automatically, edits will be lost.
[[Category: Systems]]
[[Category: Unknown]]
EOF
    continue
    }

    cd $FACTS_CACHE
    HOST_FQDN=$(cat $HOST_NAME | jq .ansible_fqdn)
    HOST_DISTRO=$(cat $HOST_NAME | jq .ansible_distribution)
    HOST_DISTRO_MAJOR=$(cat $HOST_NAME | jq .ansible_distribution_major_version)
    HOST_DISTRO_VERSION=$(cat $HOST_NAME | jq .ansible_distribution_version)
    HOST_MEMORY=$(cat $HOST_NAME | jq .ansible_memtotal_mb)
    HOST_VIRT=$(cat $HOST_NAME | jq .ansible_virtualization_type)
    HOST_ARCH=$(cat $HOST_NAME | jq .ansible_architecture)
    HOST_CPUS=$(cat $HOST_NAME | jq .ansible_processor_vcpus)
    DATE=$(cat $HOST_NAME | jq -r .ansible_date_time.epoch)
    DATE_HUMAN=$(date -d@$DATE "+%Y/%m/%d %H:%M:%S")
    ACTIVE="Active"
    [ $DATE -lt $STALE ] && {
        STALE_NOTE="This information is considered stale, the host might not be active anymore"
        ACTIVE="Stale"
    }

    echo $HOST_DISTRO >> /tmp/distrolist.wiki

    cat <<EOF >/tmp/INV:${HOST_NAME%%.*}.wiki
  Hostname: ${HOST_NAME%%.*}
  FQDN: $HOST_FQDN
  OS: $HOST_DISTRO ${HOST_DISTRO_VERSION}

  Hardware type: $HOST_VIRT
  Architecture: $HOST_ARCH

  CPU Sockets: $HOST_CPUS
  RAM: $HOST_MEMORY MB

  Inventory date: $DATE_HUMAN
  $STALE_NOTE

  This page is generated automatically, edits will be lost.
[[Category: Systems]]
[[Category: ${HOST_DISTRO}-${ACTIVE}]]
[[Category: ${HOST_DISTRO}]]
[[Category: ${HOST_DISTRO}-${HOST_DISTRO_MAJOR}]]
[[Category: ${HOST_ARCH}]]
EOF

done

###
# Generate Systems page
###
cat <<EOF >/tmp/Category:Systems.wiki
 WARNING: These pages are generated automatically!

This page contains an overview of all systems known to Ansible.

At the bottom of this page is an overview per OS using categories.
[[Category: Unknown]]
[[Category: x86_64]]
[[Category: i386]]
$(for DISTRO in $(cat /tmp/distrolist.wiki | sort -u)
do
  echo \[\[Category:$DISTRO\]\]
done)
EOF

sed -i 's/"//g' /tmp/*.wiki

# Copy the files to your wiki server and process them.
function upload_wiki() {
  scp -q /tmp/*.wiki $WIKI:/tmp
  ssh $WIKI "
    /usr/bin/php \
        /opt/mediawiki/maintenance/importTextFiles.php \
        -u Ansible \
        --bot \
        --overwrite \
        /tmp/*.wiki 2>/dev/null
    rm /tmp/*.wiki"
}

# Copy the files to your docker volume for processing.
# This requires a docker image that periodically imports
# all files in the configured location
function upload_docker() {
  scp -q /tmp/*.wiki $DOCKER_STORAGE
}

[[ -n "$WIKI"  ]] && upload_wiki
[[ -n "$DOCKER_STORAGE"  ]] && upload_docker

rm /tmp/*.wiki
