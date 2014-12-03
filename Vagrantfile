# encoding: UTF-8

GIFTWRAP_MANIFEST = ENV['GIFTWRAP_MANIFEST'] || 'manifest.yml'
GIFTWRAP_BUILDBOX_NAME = ENV['GIFTWRAP_BUILDBOX_NAME'] || 'ursula-precise'
GIFTWRAP_BUILDBOX_URL = ENV['GIFTWRAP_BUILDBOX_URL'] || 'http://apt.openstack.blueboxgrid.com/vagrant/ursula-precise.box'

Vagrant.configure('2') do |config|
  config.vm.box = GIFTWRAP_BUILDBOX_NAME
  config.vm.box_url = GIFTWRAP_BUILDBOX_URL

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
  EOF

  config.vm.define 'giftwrap' do |c|
    c.vm.host_name = 'giftwrap'
  end
end
