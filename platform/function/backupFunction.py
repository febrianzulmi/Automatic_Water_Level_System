import os


class backupFunction():
    def config():
        os.system("sudo rm -r /home/connex/platform/config/*")
        os.system("sudo cp /boot/cmdline.txt /home/connex/platform/config")
        os.system("sudo cp /boot/config.txt /home/connex/platform/config")
        os.system("sudo cp /etc/dnsmasq.conf /home/connex/platform/config")
        os.system("sudo cp /etc/hostapd/hostapd.conf /home/connex/platform/config")
        os.system("sudo cp /etc/network/interfaces /home/connex/platform/config")
        os.system("sudo cp /etc/snmp/snmpd.conf /home/connex/platform/config")
        os.system("sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /home/connex/platform/config")
        os.system("sudo cp /etc/systemd/timesyncd.conf /home/connex/platform/config")
        
    def db():
        os.system("sudo rm -r /home/connex/db/*")
        os.system("sudo mysqldump -u root NearonProjectDB > /home/connex/db/NearonProjectDB.sql")
        os.system("sudo mysqldump -u root synapsis_control > /home/connex/db/synapsis_control.sql")

    def service():
        os.system("sudo rm -r /home/connex/platform/services/*")
        os.system("sudo cp /lib/systemd/system/nearon* /home/connex/platform/services")
        os.system("sudo cp /lib/systemd/system/sensor* /home/connex/platform/services")
        os.system("sudo cp /lib/systemd/system/actuator* /home/connex/platform/services")