# Iot-Predictive-Maintenance-System
**Hardware requirement:**
1. Raspberry Pi 4 Model B.
2. MPU-6050 Accelerometer and Gyroscopic Sensor.
3. SSH1106G OLED Display.
4. 16 GB SD-CARD.

**Software Requirement:**
1. Raspberry Pi OS.
2. THONNY(Comes built-in with Pi OS).
3. Dataplicity.
4. TWILIO SMS Notification app.
5. SMTP(Self Mail Transfer Protocol).
6. Python
7. Python Libraries:
   1. Hardware Interface Libraries: mpu6050-raspberrypi, luma.oled, luma.core.
   2. Machine Learning Stack Libraries: sklearn.ensemble.IsolationForest, job.lib.
   3. Data Processing and Ai Libraries: numpy, math.
   4. System and File Management: time, csv, datetime.

**Creation of Secondary Bus for Display Connection:**
**Step 1**: Edit the System Configuration
-The Raspberry Pi manages its hardware capabilities through a file called config.txt. You need to add a "Device Tree Overlay" to activate the new bus.
-Open the terminal on your Raspberry Pi.
-Run the following command to edit the configuration file:
sudo nano /boot/config.txt

**Step 2**: Add the Overlay Command
Scroll to the very bottom of the file and add this exact line:
dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=17,i2c_gpio_scl=27

**Parameter Breakdown**:
i2c-gpio: Tells the kernel to use the software I2C driver.
bus=3: Names this new path "Bus 3" to avoid clashing with the default "Bus 1."
i2c_gpio_sda=17: Assigns Physical Pin 11 (BCM 17) as the Data line.
i2c_gpio_scl=27: Assigns Physical Pin 13 (BCM 27) as the Clock line.
Press Ctrl+O, then Enter to save.
Press Ctrl+X to exit.

**Step 3**: Reboot and Verify
The changes only take effect after the system reinitializes the GPIO header.
Reboot your Pi:
sudo reboot
Once rebooted, check if the new bus exists in the device list:
ls /dev/i2c-*
You should now see both /dev/i2c-1 (the hardware bus) and /dev/i2c-3 (your new software bus).

**Step 4**: Detect the SH1106 Display
With the OLED wired to pins 11 and 13, run a scan on the new bus:
sudo i2cdetect -y 3

Wiring Table
----------------------------------------------------------------------
| Component | Component Pin | Raspberry Pi Pin  | Purpose            |
----------------------------------------------------------------------
| MPU-6050  | VCC           | Pin-1(3.3V Power) | Sensor Power       |
----------------------------------------------------------------------
| MPU-6050  | GND           | Pin-6(Ground)     | Sensor ground      |
----------------------------------------------------------------------
| MPU-6050  | SCL           | Pin-5(GPIO 3)     | Sensor Clock(Bus1) |
----------------------------------------------------------------------
| MPU-6050  | SDA           | Pin-3(GPIO 2)     | Sensor Data(Bus1)  |
----------------------------------------------------------------------
| SSH1106G  | VCC           | Pin-17(3.3V Power)| Display Power      |
----------------------------------------------------------------------
| SSH1106G  | GND           | Pin-9(Ground)     | Display Ground     |
----------------------------------------------------------------------
| SSH1106G  | SCK           | Pin-13(GPIO 27)   | Display Clock(Bus3)|
----------------------------------------------------------------------
| SSH1106G  | SDA           | Pin-11(GPIO 17)   | Display Data(Bus3) |
----------------------------------------------------------------------

The Monitor.py code is used to define functionalities of the device such as reading vibration, frequency and temperature and display contents onto the OLED display.
The app.py is the backend part of the code, where we use flask to generate a web server through which the dashboard can be accessed.
The dashboard.html is the virtual dashboard web page, where we display the status and condition of the machine.

**Auto-Start Service:**
Go to:
/etc/systemd/system/pred_maint.service

and paste the following:
[Unit]
Description=Predictive Maintenance Edge Node
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/main_monitor.py
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
