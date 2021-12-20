# Some tools for use with Ansible
This repo provides some tools I use to run Ansible scripts.

* facts2mediawiki.sh: crude script to generate Mediawiki pages from Ansible JSON-formatted fact caches
* gpgkey: not specifically for Ansible, but will check if GPG keys are loaded in an gpg-agent (for unattended use)
* gpgkey_el7: this version uses paths for EL7 (see description in script)
* retrieve_vault.sh: this script is able to retrieve an Ansible vault password from a GPG encrypted file
* encryptansible: this script will encrypt values for use in the desired project
* runansible: this script wraps ansible-playbook in some options I like to use
* showansible: this script will (encrypted) retrieve variables from your inventory and show them on the commandline
* update_checkout: also not specifically for Ansible, but will update a Git checkout and any submodules present (note, will remove all untracked stuff as well)

## Setup retrieve_vault.sh
The idea behind this script is to retrieve the GPG encrypted ansible-vault key
from a file (see gpgkey for a way to load an unattended agent).

The following steps set up a project for use with this script:

* Create some directories

```
mkdir -p /opt/ansible/projects/myproject /opt/ansible/vaults
```
* Put this script in /opt/ansible/vaults/retrieve_vault.sh (copy, do not symlink)
* Place your vault key in /opt/ansible/vaults/myproject.gpg

```
echo 'secretkey' | gpg -r me@example.com -e > /opt/ansible/vaults/myproject.gpg
```
* Set up the regular things for your Ansible project (config, playbooks etc.)

```
cd /opt/ansible/projects/myproject
do_stuff
```
* Symlink the script into your project

```
ln -s /opt/ansible/vaults/retrieve_vault.sh /opt/ansible/projects/myproject/.ansible-vault
```

Whenever you run one of the scripts that uses the Ansible Vault password file, they will set the ```ANSIBLE_VAULT_PASSWORD_FILE``` environment variable. In order to be compatible with Ansible Tower / AWX, you _cannot_ set ```vault_password_file``` in ```ansible.cfg``` as this will break Tower's ability to decrypt Vault secrets

If your GPG agent is set up, once Ansible wants to access a vault secret now, you will be asked for the
GPG passphrase.

## Setup runansible
This script works with a similar directory structure as retrieve_vault.sh.

* Place the script in your PATH

```
ln -s /path/to/repo/runansible /usr/local/bin
```
* You can now use it to run your playbook runs!

```
Usage: /usr/local/bin/runansible [-p project] [-i inventory] [-s] playbook.yml

    -b branch    Run on specific git branch
                 When using this option, the script will check out the specified
                 git branch, run Ansible and then check out master
    -g           Update git checkout before running
    -l           Ignore locks and allow for multiple instances of runansible
    -p project   Name of the project to run the playbook from
    -i project   Name of the inventory to use, can be provided multiple times
    -r           Update roles before running playbook
    -R           Update roles before running playbook (compatible with 2.9)
    -s           Make Ansible's output sparse
    -h           This text

By default, this script will attempt to exclusively lock the playbook that is executed.
This is to prevent multiple runs of the same playbook at once.
```

# facts2mediawiki.sh
This script will use Ansible's JSON file fact cache and generate pages for Mediawiki.

They can be imported directly if you have a Mediawiki server running somewhere. Or,
when you run Mediawiki in Docker, the pages can be copied to your docker server for
processing by the container.

This requires a docker image that periodically runs a script to import them.

NOTE: For Mac users, readlink doesn't achieve the same functionality as on GNU/Linux. This might break the ```encryptansible``` script. A solution would be to use greadlink instead. To set this up, do the following:

```
brew install coreutils
alias readlink=greadlink
```
