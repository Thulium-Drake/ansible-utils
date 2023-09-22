# Some tools for use with Ansible
This repo provides some tools I use to run Ansible scripts.

* facts2mediawiki.sh: crude script to generate Mediawiki pages from Ansible JSON-formatted fact caches
* gpgkey: not specifically for Ansible, but will check if GPG keys are loaded in an gpg-agent (for unattended use)
* gpgkey_el7: this version uses paths for EL7 (see description in script)
* retrieve_vault.sh: this script is able to retrieve an Ansible vault password from a GPG encrypted file
* encryptansible: this script will encrypt values or files for use in the desired project
* runansible: this script wraps ansible-playbook in some options I like to use
* showansible: this script will retrieve (encrypted) variables from your inventory and show them on the commandline
* update_checkout: also not specifically for Ansible, but will update a Git checkout and any submodules present (note, will remove all untracked stuff as well)
* vaultansible: this script will upload values or files into HashiCorp Vault for use in the desired project

# Secret storage
This script supports a few methods of storing key material to access secrets:

  * Ansible-Vault: the native Ansible tool that utilizes symmetric encryption
  * Bitwarden/Vaultwarden: a password-manager for which Ansible has module support via the Community

The main difference between these methods is that Ansible-Vault requires that all secrets
to be present in your Ansible Project and that makes it not as scalable. The Bitwarden
modules can retrieve secret material using ```lookup``` calls in your inventory, so the secret
retrieved is always current.

Both methods require at least these steps:

* Create some directories
```
mkdir -p /opt/ansible/projects/myproject /opt/ansible/vaults
```
* Set up the regular things for your Ansible project (config, playbooks etc.)
```
cd /opt/ansible/projects/myproject
do_stuff
```

## Ansible-Vault: retrieve_vault.sh
The idea behind this script is to retrieve the GPG encrypted ansible-vault key
from a file (see gpgkey for a way to load an unattended agent).

* Put this script in /opt/ansible/vaults/retrieve_vault.sh (copy, do not symlink)
* Place your vault key in /opt/ansible/vaults/myproject.gpg

```
echo 'secretkey' | gpg -r me@example.com -e > /opt/ansible/vaults/myproject.gpg
```
* Symlink the script into your project

```
ln -s /opt/ansible/vaults/retrieve_vault.sh /opt/ansible/projects/myproject/.ansible-vault
```

Whenever you run one of the scripts that uses the Ansible Vault password file, they will set the ```ANSIBLE_VAULT_PASSWORD_FILE``` environment variable. In order to be compatible with Ansible Tower / AWX, you _cannot_ set ```vault_password_file``` in ```ansible.cfg``` as this will break Tower's ability to decrypt Vault secrets

If your GPG agent is set up, once Ansible wants to access a vault secret now, you will be asked for the
GPG passphrase.

## Bitwarden: .bitwarden.gpg
In order to use Bitwarden integration create a GPG encrypted file in the vaults directory with the following content:

```
export BW_CLIENTID=user.blahblahblah
export BW_CLIENTSECRET=somesecretkey
export BW_PASSWORD=the_bitwarden_master_password
```
* Symlink the file into your project

```
ln -s /opt/ansible/vaults/bw-myproject.gpg /opt/ansible/projects/myproject/.bitwarden.gpg
```

Afterwards, you can retrieve secrets stored in Bitwarden with Ansible, like this example playbook:

```
---
- name: 'Get secret from Bitwarden'
  hosts: 'localhost'
  gather_facts: false
  tasks:
    - name: 'Show secret'
      ansible.builtin.debug:
        msg: "{{ lookup('community.general.bitwarden', 'Root Password', field='password') }}"
```

Note that there are no modules to edit anything in Bitwarden (yet?), so there's no means of
automatically updating secrets in Bitwarden.

# Tools

## Setup runansible
This script works with a similar directory structure as retrieve_vault.sh.

* Place the script in your PATH

```
ln -s /path/to/repo/runansible /usr/local/bin
```
* You can now use it to run your playbook runs!

### Role verification
```runansible``` can verify the GPG signatures of each role signed with Ansible-Sign (https://github.com/ansible/ansible-sign) by passing ```-v``` to the options.

You can configure the following variables in your Ansble Projects for this functionality:

```
#### Exclude known unsigned (or badly signed) roles from verification, defaults to []
role_verify_exceptions:
  - 'role1'
  - 'role2'

#### If roles do not pass validation, continue anyway, defaults to true
role_verify_strict: false
```

NOTE: If any role is not (correctly) validated in strict mode, this means the execution of your playbook will _NOT_ continue.

## facts2mediawiki.sh
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

## Setup vaultansible
This script requires an already set up HashiCorp Vault instance for use. This script leverages the ```community.hashi_vault``` collection's modules to interact with Vault. So you need to have those available as well.

Due to that setup, it also uses the Ansible Inventory for it's configuration, add the following values to your ```group_vars/all.yml```. Do note that the script assumes the Vault recommended authentication method of AppRole:

```
ansible_hashi_vault_url: 'https://vault.example.nl'
ansible_hashi_vault_auth_method: 'approle'
ansible_hashi_vault_role_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
ansible_hashi_vault_secret_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
ansible_hashi_vault_engine_mount_point: 'ansible'  # This is the _name_ of the KV2 secrets engine instance
```

After storing a variable or file, the script will print out a snippet you can use to retrieve the variable.

## styleguide.yml
This is the styleguide I use to write my own code, it's just been added here for reference
