# encoding: UTF-8

GIFTWRAP_MANIFEST = ENV['GIFTWRAP_MANIFEST'] || 'examples/manifest.yml'
GIFTWRAP_ARGS = ENV['GIFTWRAP_ARGS'] || '-t package'
GIFTWRAP_BUILDBOX_NAME = ENV['GIFTWRAP_BUILDBOX_NAME'] || 'ursula-precise'
GIFTWRAP_BUILDBOX_URL = ENV['GIFTWRAP_BUILDBOX_URL'] || 'http://apt.openstack.blueboxgrid.com/vagrant/ursula-precise.box'
GIFTWRAP_POSTBUILD_SCRIPT = ENV['GIFTWRAP_POSTBUILD_SCRIPT'] || ""
<<<<<<< HEAD

ENV['VAGRANT_DEFAULT_PROVIDER'] = 'virtualbox'
=======
>>>>>>> master

Vagrant.configure('2') do |config|
  config.vm.box = GIFTWRAP_BUILDBOX_NAME
  config.vm.box_url = GIFTWRAP_BUILDBOX_URL

<<<<<<< HEAD
  config.vm.provider :openstack do |os, override|
=======
  config.ssh.username = 'ubuntu'
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.provider :openstack do |os|
>>>>>>> master
    os.openstack_auth_url    = "#{ENV['OS_AUTH_URL']}/tokens"
    os.username              = ENV['OS_USERNAME']
    os.password              = ENV['OS_PASSWORD']
    os.tenant_name           = ENV['OS_TENANT_NAME']
<<<<<<< HEAD
    os.openstack_network_url = ENV['OS_NEUTRON_URL']
    
    os.flavor                = ENV['GIFTWRAP_OS_FLAVOR'] || 'm1.small'
    os.image                 = ENV['GIFTWRAP_OS_IMAGE'] || 'ubuntu-12.04'

    if ENV['GIFTWRAP_OS_NETWORKS']
        os.networks          = ENV['GIFTWRAP_OS_NETWORKS'].split(",")
    else
        os.networks          = ['internal']
    end
    
    override.ssh.username = ENV['GIFTWRAP_OS_USERNAME'] || 'ubuntu'
    if ENV['GIFTWRAP_OS_FLOATING_IP_POOL']
        os.floating_ip_pool  = ENV['GIFTWRAP_OS_FLOATING_IP_POOL']
    end
    if ENV['GIFTWRAP_OS_SECURITY_GROUPS']
        os.security_groups   = ENV['GIFTWRAP_SECURITY_GROUPS'].split(",")
    end
=======
    os.flavor                = 'm1.small'
    os.image                 = 'ubuntu-12.04'
    os.openstack_network_url = ENV['OS_NEUTRON_URL']
    os.networks              = ['internal']
    os.floating_ip_pool      = 'external'
>>>>>>> master
    os.rsync_exclude_paths   = []
    os.rsync_cvs_exclude     = false
  end

  config.vm.provision 'shell', inline: <<-EOF
    #!/bin/bash
    set -x
    set -e 
    if [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
    elif [ -f /etc/debian_version ]; then
        OS=Debian
    elif [ -f /etc/redhat-release ]; then
        OS=RedHat
    fi

    if [ "$OS" == "Debian" ] || [ "$OS" == "Ubuntu" ]; then
        /vagrant/scripts/prepare_debian.sh
    fi

    gem install --no-ri --no-rdoc fpm
    cd /vagrant
    python setup.py install
<<<<<<< HEAD
    giftwrap build -m #{GIFTWRAP_MANIFEST} #{GIFTWRAP_ARGS}

    if [ ! -z "#{GIFTWRAP_POSTBUILD_SCRIPT}" ]; then
        echo "Running postbuild script: '#{GIFTWRAP_POSTBUILD_SCRIPT}'"
=======
    giftwrap build -m #{GIFTWRAP_MANIFEST}

    if [ ! -z "#{GIFTWRAP_POSTBUILD_SCRIPT}" ]; then
>>>>>>> master
        #{GIFTWRAP_POSTBUILD_SCRIPT}
    fi

  EOF

  config.vm.define 'giftwrap' do |c|
    c.vm.host_name = 'giftwrap'
  end
end
