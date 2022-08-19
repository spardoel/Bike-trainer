# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 2 - Use a packet sniffer to monitor normal device control
At this stage I knew what services and characteristics the device had but I didn't know which ones were used to control the trainer resistance. 
I used Wireshark and the Bluetooth Virtual Sniffer from Microsoft to monitor the BLE traffic on my computer. (https://techcommunity.microsoft.com/t5/microsoft-bluetooth-blog/introducing-bluetooth-virtual-sniffer-btvs-exe/ba-p/2113478)

### Lauch TrainerRoad to do a bike workout
I started the sniffer and launched a workout on TrainerRoad. The TrainerRoad interface looks like this
![Trainer road image](https://user-images.githubusercontent.com/102377660/185466247-819c4fad-b2e1-46f3-b5eb-d9b476920a45.PNG)

Basically, the program has a set workout template that will increase and decrease the resistance at specific times. The blue outline at the bottom is the target power plotted over time. 
The rider just has to keep pedaling and the resistance will be changed to match the desired workout profile.
At this point, the two most important values were the Target Power (aka the trainer resistance) and the User Power (aka how hard the cyclist is turning the pedals).
In the above image, the target power is 95 Watts and the user power is 0 Watts (because I was sitting at my computer not on the bike...).

### Inspect the packet traffic
After letting the workout run for a few minutes I noticed some patterns in the BLE packet traffic. 
First, I noticed that the SUITO trainer (address 'F3:DB:2B:F4:47:0C') was notifying the computer once every second using the Fitness Machine Service and the Indoor Bike Data characteristic. 
![Sniffer bike data example](https://user-images.githubusercontent.com/102377660/185469411-faf199e6-8543-4918-8289-9af0051ffdad.PNG)

I also noticed that the only write requests were using the Fitness Machine service and the Fitness Machine Control Point characteristic.
![write request example](https://user-images.githubusercontent.com/102377660/185468851-9b907899-95a3-4be8-8d25-3cc154a947e7.PNG)

Following a write request there were always notification, indication and confirmation messages sent back to the app. 

In the notification from the Fitness Machine Status, we can see the current target power (95 W). 
This notification was sent after the Fitness Machine Control Point write request and appears to be a confirmation that the trainer resistance was changed (confirmation code 08). 
![status confirmation](https://user-images.githubusercontent.com/102377660/185469826-080ec645-09ed-4345-a0bd-2057d961de02.PNG)

### Wrap up
So now I knew that the 'Fitness Machine Control' point characteristic was used to write the trainer target power (resistance) and the 'Indoor Bike Data' notification was used to send the user power back to the application.
The next step was to connect to the device in python and set up the device comminucation using these same characteristics. 
