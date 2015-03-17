# encoding: UTF-8

GIFTWRAP_MANIFEST = ENV['GIFTWRAP_MANIFEST'] || 'examples/manifest.yml'
GIFTWRAP_BUILDBOX_NAME = ENV['GIFTWRAP_BUILDBOX_NAME'] || 'ursula-precise'
GIFTWRAP_BUILDBOX_URL = ENV['GIFTWRAP_BUILDBOX_URL'] || 'http://apt.openstack.blueboxgrid.com/vagrant/ursula-precise.box'
GIFTWRAP_POSTBUILD_SCRIPT = ENV['GIFTWRAP_POSTBUILD_SCRIPT'] || ""

Vagrant.configure('2') do |config|
  config.vm.box = GIFTWRAP_BUILDBOX_NAME
  config.vm.box_url = GIFTWRAP_BUILDBOX_URL

  config.ssh.username = 'ubuntu'
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.provider :openstack do |os|
    os.openstack_auth_url    = "#{ENV['OS_AUTH_URL']}/tokens"
    os.username              = ENV['OS_USERNAME']
    os.password              = ENV['OS_PASSWORD']
    os.tenant_name           = ENV['OS_TENANT_NAME']
    os.flavor                = 'm1.small'
    os.image                 = 'ubuntu-12.04'
    os.openstack_network_url = ENV['OS_NEUTRON_URL']
    os.networks              = ['internal']
    os.floating_ip_pool      = 'external'
    os.rsync_exclude_paths   = []
    os.rsync_cvs_exclude     = false
  end

  config.vm.provision 'shell', inline: <<-EOF
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
    giftwrap build -m #{GIFTWRAP_MANIFEST}

    if [ ! -z "#{GIFTWRAP_POSTBUILD_SCRIPT}" ]; then
        #{GIFTWRAP_POSTBUILD_SCRIPT}
    fi

  EOF

  config.vm.define 'giftwrap' do |c|
    c.vm.host_name = 'giftwrap'
  end
end
