# Setup

This describes the setup of new robots based on a raspberry pi.

All the steps were tested with a raspberry pi 5.
Last used: 17.04.2025

List of already operational / configured robots:

| Number | Hostname | Color | AP-MAC-Address    | AP-SSID      |
| ------ | -------- | ----- | ----------------- | ------------ |
| 0.     | cvblack  | black | 80:18:01:00:00:00 | cv-bot-black |
| 1.     | cvorange | red   | 80:18:01:00:00:01 | cv-bot-orange|
| 2.     | cvbrown  | brown | 80:18:01:00:00:02 | cv-bot-brown |
| 3.     | cvwhite  | white | 80:18:01:00:00:03 | cv-bot-white |

## 1. Install the operating system

### 1.1 Download the image and install it on the SD card

Download the respberry pi imager and install it on your computer. You can find the imager here:
https://www.raspberrypi.com/software/

Use the latest version of the Raspberry Pi OS, preferably the 64 bit version.
Continue with the installer and activate Wifi, and SSH during the process.

By convention, the hostname should be 'cv-[color]' where [color] is the color for identifying the robot.
For example, 'cv-red' for a red robot.

The username should be 'pi'. Make sure the set a strong password for the user pi and note it.

### 1.2 Boot the raspberry pi

Insert the SD card into the raspberry pi and boot it. Make sure you have a monitor connected or use SSH to connect to the raspberry pi when wifi is available.

### 1.3 Update the system

Run the following commands to keep the system up to date:

Eventually you have to manually accept some new versions of the packages.

```bash
sudo apt update && sudo apt full-upgrade -y && sudo apt autoremove -y && sudo apt clean
```

## 2. Configure the system

### 2.1 Set the hostname

If not done already during flashing the SD card, set the hostname to 'cv-[color]' where [color] is the color for identifying the robot.

### 2.2 Configure Wifi Access Point

To connect to the robot, you need to configure the wifi access point.
The pi will have an access point as well as a client connection to the local network.

This steps are adapted from the following tutorial:
https://forums.raspberrypi.com/viewtopic.php?t=354591

Note since the bookworm release, the default network manager is now `NetworkManager` instead of `dhcpcd`, so few additional steps must be introduced so NetworkManager will not manage our new AP interface.

#### 2.2.1 Install Dependencies

Install the needed interface.

```bash
sudo apt-get install -y rng-tools hostapd dnsmasq dhcpcd5
```

#### 2.2.2 Disable NetworkManager for the new interface

To prevent NetworkManager from managing the new interface, ones needs to alter the configuration file.

```bash
sudo nano /etc/NetworkManager/NetworkManager.conf
```

Append the following keyfile section to the file, if it does not exist yet:

```bash
[keyfile]
unmanaged-devices=interface-name:uap0
```

This will prevent NetworkManager from managing the new interface called uap0.
This is important, as otherwise the access point will not work.

#### 2.2.3 Enable Configure the Access Point Interface with a Static IP

Edit the dhcpcd configuration file to set a static IP address for the access point interface.

```bash
sudo nano /etc/dhcpcd.conf
```

This can be done by adding the following lines at the end of the file:

```bash
interface uap0
  static ip_address=192.168.4.1/24
```

E.g. 192.168.4.1 will now be the static IP and "Host" / "Access Point" address of the robot.

Enable the dhcpcd service to start on boot and start it:

```bash
sudo systemctl start dhcpcd && sudo systemctl enable dhcpcd
```

This needs to be done as dhcpcd is not running on bookworm by default. We use it as additional network manager.

#### 2.2.3 Configure DHCP for the Access Point

To allow clients to connect to the access point, you need to configure the DHCP server.
Edit the dnsmasq configuration file:

```bash
sudo nano /etc/dnsmasq.conf
```

Add the following lines to the file:

```bash
interface=uap0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```

This will allow clients to connect to the access point and get an IP address in the range of
...2 to ...20. The robot will have the IP ...1.
The range can be changed if needed, but make sure to keep the first three octets the same as the static IP address (following the subnet mask and 192.168.4.[x] scheme).

#### 2.2.4 Start the Access Point interface upon boot

To create the interface upon boot, we will create a small service that will create the interface and start the access point.

Therefor open / create the file:
sud

```bash
sudo nano /etc/systemd/system/uap0.service
```

And add the following lines to the file, but change the MAC address.:

E.g. 00:11:22:33:44:55 is the MAC address of the access point interface it must be unique in the network, and different from the MAC address of the wlan0 interface.

To keep the macs similar, one can use the following convention:

80:18:01:XX:XX:XX

801, when very creativly read means "Bot" e.g. BOTBOT and then a ascending number for the robot in hex starting from 0. Check the already used numbers in the table above.

Add your numbers in the list and replace use this then in the file.

```bash
[Unit]
Description=Create uap0 interface
After=sys-subsystem-net-devices-wlan0.device

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/sbin/iw phy phy0 interface add uap0 type __ap
ExecStartPost=/usr/bin/ip link set dev uap0 address 00:11:22:33:44:55
ExecStartPost=/sbin/ifconfig uap0 up
ExecStop=/sbin/iw dev uap0 del

[Install]
WantedBy=multi-user.target
```

#### 2.2.5 Reload the systemd daemon / Start the service

Reload the systemd daemon to make the new service available:

```bash
sudo systemctl daemon-reload && sudo systemctl start uap0.service && sudo systemctl enable uap0.service
```

You can check if the service created the interface by running:

```bash
ifconfig uap0
```

This should now state the onterface with the MAC address as configured.

#### 2.2.6 Configure the Access Point

Now we need to configure the access point itself. This is done by editing the hostapd configuration file:

```bash
sudo nano /etc/hostapd/hostapd.conf
```

Add the following lines to the file, but change the ssid and password:

For the ssid, use the convention "cv-bot-[color]" where [color] is the color for identifying the robot.
For the password, use a strong password that is at least 8 characters long and note it.

The password must be between 8 and 63 characters long. Otherwise, the access point will not start.

```bash
interface=uap0
ssid=ACCESS-POINT-NAME
country_code=DE
hw_mode=g
channel=6
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase="YOUR-PASSWORD-HERE"
```

#### 2.2.7 Linking the hostapd configuration file

To link the hostapd configuration file to the system, edit the following file:

```bash
sudo nano /etc/default/hostapd
```

edit line with DAEMON_CONF or uncomment it if it is commented out.:

```bash
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

#### 2.2.8 Start the Access Point

To start the access point, run the following command:

```bash
sudo systemctl start hostapd && sudo systemctl start dnsmasq && sudo systemctl enable hostapd && sudo systemctl enable dnsmasq
```

If the pi reports with a:

```bash
Failed to start hostapd.service: Unit hostapd.service is masked.
```

Then you need to unmask the service with the following command:

```bash
sudo systemctl unmask hostapd && sudo systemctl enable hostapd && sudo systemctl start hostapd
```

If enabled, execute the above command again to make sure the service is started.

Note it can be stopped with the following command:

```bash
sudo systemctl stop hostapd
```

#### 2.2.9 Check the Access Point

To check if the access point is running, run the following command:

```bash
sudo systemctl status hostapd.service
```

This should show the status of the hostapd service and indicate that it is running.
Containing a uap0: AP-ENABLED

#### 2.2.10 Internet Connection via wlan0

A device in the new hosted access point cannot connect reach the internet, as the pi will not forward the packets from the uap0 interface to the wlan0 which ultimately connects to the internet.
So, we need to first allow ip net forwarding.

Open the following file:

```bash
sudo nano /etc/sysctl.conf
```

and uncomment the line with

```bash
net.ipv4.ip_forward=1
```

Also set it with the following command:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

This will allow the forwarding of packets.

Now we need to set up nftables to allow the forwarding of packets from the uap0 interface to the wlan0 interface. This will create a NAT (Network Address Translation) rule that will allow the packets to be forwarded beyond the interfaces.

To do this, we will use the nftables package. This is a replacement for the iptables package and is used to set up packet filtering rules.

Open the following file:

```bash
sudo nano /etc/nftables.conf
```

And change the content to:

```bash
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
        chain input {
                type filter hook input priority filter;
        }
        chain forward {
                type filter hook forward priority filter; policy drop;
                iifname "wlan0" oifname "uap0" ct state { established, related } counter accept
                iifname "uap0" oifname "wlan0" counter accept
        }
        chain output {
                type filter hook output priority filter;
        }
}

table ip nat {
        chain postrouting {
                type nat hook postrouting priority filter; policy accept;
                oifname "wlan0" masquerade
        }
}
```

This will allow bidirectional forwarding of packets between the wlan0 and uap0 interfaces, as long as the initial packet is coming from the uap0 interface.

Now, start the nftables service and enable it to start on boot:

```bash
sudo systemctl start nftables && sudo systemctl enable nftables
```

Now, internet connection should be available for the devices connected to the access point. If one wants to reach devices from the wlan0 interface (e.g. for initial ssh connections), one needs to set up dedicated forwarding rules for the corresponding devices.

### 2.3 Create new user

Create a new user named student:

```bash
sudo useradd -m student
sudo passwd student
sudo usermod -g users student
```

## 3. Install frameworks and software

This section describes the installation of the frameworks and software needed for the robot.

### 3.1 Install the dependencies

These include the dependencies for pyenv and python, as well as the system dependencies for the robot.

```bash
sudo apt install -y build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

### 3.2 Install Pyenv

Pyenv is an easy way to install and manage multiple versions of Python.

The following command will install pyenv and add it to your bash profile.

```bash
curl -fsSL https://pyenv.run | bash
```

After the installation, you need to add the following lines to your `~/.bashrc` file:

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

### 3.3 Install Python 3.10

Install a recent python version.
The latest version is recommended, but you can also use a specific version if needed.

```bash
pyenv install 3.10.17
```

This will take a while, so be patient.
On success, there should be no error and the command:

```bash
pyenv versions
```

Should show the installed version e.g.:

```bash
* system (set by /home/pi/.pyenv/version)
  3.10.17
```

After the installation, set the global python version to 3.10.17:

```bash
pyenv global 3.10.17
```
