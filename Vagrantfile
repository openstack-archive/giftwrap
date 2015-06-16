# encoding: UTF-8

GIFTWRAP_MANIFEST = ENV['GIFTWRAP_MANIFEST'] || 'examples/manifest.yml'
GIFTWRAP_ARGS = ENV['GIFTWRAP_ARGS'] || '-t package'
GIFTWRAP_BUILDBOX_NAME = ENV['GIFTWRAP_BUILDBOX_NAME'] || 'ursula-precise'
GIFTWRAP_BUILDBOX_URL = ENV['GIFTWRAP_BUILDBOX_URL'] || 'http://apt.openstack.blueboxgrid.com/vagrant/ursula-precise.box'

# CentOS7 example
#GIFTWRAP_BUILDBOX_NAME = ENV['GIFTWRAP_BUILDBOX_NAME'] || 'centos7'
#GIFTWRAP_BUILDBOX_URL = ENV['GIFTWRAP_BUILDBOX_URL'] || 'https://f0fff3908f081cb6461b407be80daf97f07ac418.googledrive.com/host/0BwtuV7VyVTSkUG1PM3pCeDJ4dVE/centos7.box'

GIFTWRAP_POSTBUILD_SCRIPT = ENV['GIFTWRAP_POSTBUILD_SCRIPT'] || ""

ENV['VAGRANT_DEFAULT_PROVIDER'] = 'virtualbox'

Vagrant.configure('2') do |config|
  config.vm.box = GIFTWRAP_BUILDBOX_NAME
  config.vm.box_url = GIFTWRAP_BUILDBOX_URL

  config.vm.provider :openstack do |os, override|
    os.openstack_auth_url    = "#{ENV['OS_AUTH_URL']}/tokens"
    os.username              = ENV['OS_USERNAME']
    os.password              = ENV['OS_PASSWORD']
    os.tenant_name           = ENV['OS_TENANT_NAME']
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
    elif [ "$OS" == "RedHat" ]; then
        /vagrant/scripts/prepare_redhat.sh
    fi

    gem install --no-ri --no-rdoc fpm
    cd /vagrant

    GET_PIP_MD5='8b911e095db95b4dc1f11d4ce8377efd'
    wget -q -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
    if ! md5sum /tmp/get-pip.py | grep -q $GET_PIP_MD5; then
        echo "pip installation could not be verified. Quitting"
        exit -1
    fi
    python /tmp/get-pip.py
    pip install -U setuptools     
    
    export PATH=/usr/local/bin/:$PATH
    pip install .
    giftwrap build -m #{GIFTWRAP_MANIFEST} #{GIFTWRAP_ARGS}

    if [ ! -z "#{GIFTWRAP_POSTBUILD_SCRIPT}" ]; then
        echo "Running postbuild script: '#{GIFTWRAP_POSTBUILD_SCRIPT}'"
        #{GIFTWRAP_POSTBUILD_SCRIPT}
    fi

  EOF

  config.vm.define 'giftwrap' do |c|
    c.vm.host_name = 'giftwrap'
  end
end
