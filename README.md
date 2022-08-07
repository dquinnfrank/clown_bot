# Setup from new install
* Run setup.py
* Ensure that `etc/xdg/lxsession/LXDE-pi/autostart` looks as follows, replacing {path_to_clown_bot} as needed
```
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@lxterminal --command="{path_to_clown_bot}/linux_run_on_start_2.sh"
@xscreensaver -no-splash
```

# Setup from new wifi
* Remove Pi from case (It's really hard to get the display cable in otherwise)
* Plug in power, usb hub, mouse/keyboard, and display (really push the display cable in hard, it is real finicky)
* Turn on Pi
* Don't worry about the window that pops up
* Connect the Pi to wifi
* Don't worry about why it needs a wifi connection
* Turn off the Pi
* Remove the cables and put the Pi into the case
* Plug in the power, usb hub, white keypad, and speaker
* Turn on and wait about a minute

# Instructions
* You can now play your theme song on demand
* The button farthest from the input cable plays the greatest tune ever made
* The middle button mutes and unmutes the device (But why would you ever mute it?)
* The button closest to the cable does nothing
