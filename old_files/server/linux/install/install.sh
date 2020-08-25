#!/bin/bash
#run only as sudo. requires systemd as init and apt-get as packet manager.

#check if script is run by sudo
if [[ $EUID -ne 0 ]]
	then echo "[***] run this script as sudo. exiting"
	exit 1
fi
#check if apt and systemd exist
which apt-get > /dev/null
if [ $? == 1 ]
then echo "[***] apt-get not found. exiting"
	exit 1
fi

which systemctl > /dev/null
if [ $? == 1 ]
then echo "[***] systemd not found. exiting"
	exit 1
fi

#change directory script directory
p=$(dirname $(realpath "$0" ))
cd $p

#variables
a=$(which agetty)
h=$HOME
u=$USER
r=root
w=rmvid_logo.png
x=$HOME/.xinitrc
c=$HOME/.config
t=lxterminal

echo "[***] rmvid server installation started"

#install some additional programs
apt-get update > /dev/null 2>&1
apt-get install -y xinit nitrogen openbox openssh-server $t > /dev/null 2>&1
echo "[***] additional programs installed"

#define real user name for further usage
if [ "$u" == "$r" ]
	then u=$SUDO_USER
fi

#make ~/.xinitrc and fill it
echo "openbox-session" > $x
chown $u:$u $x
chmod +x $x
echo "[***] .xinitrc done"

#configure openbox
if [ -d "$c/openbox" ]
	then mv $c/openbox $c/openbox_old
fi
cp -r openbox $c
sed -i "s/terminal_name_here/$t/g" $c/openbox/menu.xml
sed -i "s/terminal_name_here/$t/g" $c/openbox/rc.xml
chown -R $u:$u $c/openbox
echo "[***] openbox done"

#configure wallpaper with nitrogen
mkdir -p /opt/rmvid-server/wallpaper
cp $w /opt/rmvid-server/wallpaper/
chown -R $u:$u /opt/rmvid-server/wallpaper
echo "[***] nitrogen done"

#set launch end-point on console
systemctl set-default multi-user.target > /dev/null 2>&1
echo "[***] stop init on console done"

#set autologin to tty1 via agetty and systemd
if [ -d "/etc/systemd/system/getty@tty1.service.d/" ]
	then echo "[***] old autologin found, removing"
	rm -r /etc/systemd/system/getty@tty1.service.d/
fi
mkdir /etc/systemd/system/getty@tty1.service.d
touch /etc/systemd/system/getty@tty1.service.d/override.conf
echo -e "[Service]\nExecStart=\nExecStart=-$a --autologin $u --noclear %I 38400 linux" > /etc/systemd/system/getty@tty1.service.d/override.conf
echo "[***] autologin done"

#set X server autostart
if [ -f "$h/.bash_profile" ]
	then mv $h/.bash_profile $h/.bash_profile_old
fi
echo "[[ -z \$DISPLAY && XDG_VTNR -eq 1 ]] && exec startx > /dev/null 2>&1" > $h/.bash_profile
chown $u:$u $h/.bash_profile
echo "[***] autostart X done"

#turn off plymouth
sed -i "s/splash//g" /etc/default/grub
update-grub > /dev/null 2>&1
echo "[***] off plymouth done"

#turn off apport and autoupdate
if [ -f "/etc/default/apport" ]
	then echo "enabled=0" > /etc/default/apport
			echo "[***] off apport done"
	else echo "[***] /etc/default/apport not found"
fi
if [ -f "/etc/apt/apt.conf.d/10periodic" ]
	then echo -e 'APT::Periodic::Update-Package-Lists "0";\nAPT::Periodic::Download-Upgradeable-Packages "0";\nAPT::Periodic::AutocleanInterval "0";\nAPT::Periodic::Unattended-Upgrade "0";' > /etc/apt/apt.conf.d/10periodic
		echo "[***] off autoupdate done"
	else echo "[***] /etc/apt/apt.conf.d/10periodic not found"
fi

python3 config_make.py
chown $u:$u /opt/rmvid-server/*

#set server autostart
if [ -d "/etc/systemd/system/rmvid-server.service" ]
	then echo "[***] old service found, removing"
	rm -r /etc/systemd/system/rmvid-server.service
fi
touch /etc/systemd/system/rmvid-server.service
echo -e "[Unit]\nDescription=Remote video control server\nRequires=syslog.service\n[Service]\nType=oneshot\nWorkingDirectory=/opt/rmvid-server\nExecStart=/bin/bash /opt/rmvid-server/rmvid-daemon\nRestart=no\nRemainAfterExit=True\nUser=$u\nGroup=$u\n[Install]\nWantedBy=multi-user.target" > /etc/systemd/system/rmvid-server.service
systemctl daemon-reload > /dev/null 2>&1
systemctl enable rmvid-server.service > /dev/null 2>&1

echo "[***] rmvid-server installed"
echo "[***] os prepared, reboot required"
