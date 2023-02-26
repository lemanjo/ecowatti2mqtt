# ecowatti2mqtt

Integrate Jäspi Ecowatti boiler temperatures to Home Assistant using MQTT.

## Requirements

Hardware capable of running python >3.8 and connecting to Serial interface.
Example Raspberry Pi + USB Serial dongle

Either Home Assistant with Mosquitto or separate MQTT broker instance.

## Installation

Download & unzip the repository

```
|> wget https://github.com/lemanjo/ecowatti2mqtt/archive/refs/heads/master.zip
|> unzip master.zip
```

Move to the downloaded directory

```
|> cd ecowatti2mqtt-master
```

Install the requirements

```
|> pip install -r requirements.txt
```

Create config file from the example config

```
cp config.example.json config.json
```

Edit the file with nano

```
nano config.json
```

Set permissions for the python file

```
sudo chmod +x ecowatti2mqtt.py
```

Check the full path for the file and store it

```
|> pwd
/home/pi/ecowatti2mqtt-master
```

Create service file to run the program after boot

```
|> sudo nano /lib/systemd/system/ecowatti.service
```

Copy paste following config. Note that you need to specify the path to the script based on your environment.
Save (CTRL+O) and exit (CTRL+X).

```
[Unit]
Description=Ecowatti2mqtt service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/pi/ecowatti2mqtt-master/ecowatti2mqtt.py

[Install]
WantedBy=multi-user.target
```

Set permissions for the service file

```
sudo chmod 644 /lib/systemd/system/ecowatti.service
```

Update the systemd configuration

```
|> sudo systemctl daemon-reload
|> sudo systemctl enable ecowatti.service
```

Now its all done and you can reboot the system.
After reboot, the program should load on the background and Home Assistant discovery should find the new mqtt sensors.

```
sudo reboot
```