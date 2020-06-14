# Some tools for use with Ansible
This repo provides some tools I use to run Ansible scripts.

* retrieve_vault.sh: this script is able to retrieve an Ansible vault password from a GPG encrypted file
* runansible: this script wraps ansible-playbook in some options I like to use

## Setup retrieve_vault.sh
The idea behind this script is to retrieve the GPG encrypted ansible-vault key from a file.

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
* Set vault_password_file to .ansible-vault
* Symlink the script into your project

```
ln -s /opt/ansible/vaults/retrieve_vault.sh /opt/ansible/projects/myproject/.ansible-vault
```

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
runansible -h

Usage: /usr/local/bin/runansible [-p project] [-s] playbook.yml

    -g           Update git checkout before running
    -p project   Name of the project to run the playbook from
    -r           Update roles before running playbook
    -s           Make Ansible's output sparse
    -h           This text
```

# facts2mediawiki.sh
This script will use Ansible's JSON file fact cache and generate pages for Mediawiki.

They can be imported directly if you have a Mediawiki server running somewhere. Or,
when you run Mediawiki in Docker, the pages can be copied to your docker server for
processing by the container.

This requires a docker image that periodically runs a script to import them.
