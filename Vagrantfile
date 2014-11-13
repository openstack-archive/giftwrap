# encoding: UTF-8

GIFTWRAP_MANIFEST = ENV['GIFTWRAP_MANIFEST'] || 'manifest.yml'
GIFTWRAP_BUILDBOX_NAME = ENV['GIFTWRAP_BUILDBOX_NAME'] || 'ursula-precise'
GIFTWRAP_BUILDBOX_URL = ENV['GIFTWRAP_BUILDBOX_URL'] || 'http://apt.openstack.blueboxgrid.com/vagrant/ursula-precise.box'

Vagrant.configure('2') do |config|
  config.vm.box = GIFTWRAP_BUILDBOX_NAME
  config.vm.box_url = GIFTWRAP_BUILDBOX_URL

  config.vm.provision 'shell', inline: <<-EOF
    apt-get update
    apt-get install -y build-essential ruby1.9.1-dev git python-pip python-dev python-virtualenv libxml2-dev libxslt-dev libffi-dev
    gem install --no-ri --no-rdoc fpm
    cd /vagrant
    python setup.py install
    giftwrap build -m #{GIFTWRAP_MANIFEST}
  EOF

  config.vm.define 'giftwrap' do |c|
    c.vm.host_name = 'giftwrap'
  end
end
