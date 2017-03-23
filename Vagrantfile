Vagrant.configure("2") do |config|
  config.vm.box = "rafacas/centos63-plain"
  config.vm.network "private_network", ip: "192.168.33.22"
  config.vm.synced_folder ".", "/usr/src/app", type: "rsync", sync__exclude: ".git/"
  config.vm.provider :virtualbox do |vb|
    vb.customize ["setextradata", :id, "VBoxInternal/Devices/VMMDev/0/Config/GetHostTimeDisabled", 0]
  end
end
