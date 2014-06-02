# encoding: UTF-8

Vagrant.configure('2') do |config|
  config.vm.box = 'hashicorp/precise64'
  config.vm.provision 'shell', inline: <<-EOF
    apt-get update
    apt-get install build-essential ruby1.9.1-dev -y
    gem install --no-ri --no-rdoc fpm
  EOF

  config.vm.define 'giftwrap' do |c|
    c.vm.host_name = 'giftwrap'
  end
end
