0 Build image

podman build -f Dockerfile_multiarch -t bsr_zonal_amd64 --platform l
inux/amd64 .

1 Run broker

podman run -it --rm --name Server --network host -v ./vss.json:/opt/kuksa ghcr.io/eclipse-kuksa/kuksa-databroker:main --insecure --vss /opt/kuksa

2 Grant device permission

2.1 lsusb

2.2 find device with ID in run.sh

2.3 sudo chmod 777 /dev/bus/usb/<device_bus_address>

3 Run Zonal

podman run --rm -it --network host --device=/dev/bus/usb/003/011 27ceb98daf4d -loopback=1 127.0.0.1:55555

Check result

podman run -it --rm --network host ghcr.io/eclipse-kuksa/kuksa-databroker-cli:main --server 0.0.0.0:55555

Using kuksa.val.v1



  ⠀⠀⠀⢀⣤⣶⣾⣿⢸⣿⣿⣷⣶⣤⡀

  ⠀⠀⣴⣿⡿⠋⣿⣿⠀⠀⠀⠈⠙⢿⣿⣦⠀

  ⠀⣾⣿⠋⠀⠀⣿⣿⠀⠀⣶⣿⠀⠀⠙⣿⣷   

  ⣸⣿⠇⠀⠀⠀⣿⣿⠠⣾⡿⠃⠀⠀⠀⠸⣿⣇⠀⠀⣶⠀⣠⡶⠂⠀⣶⠀⠀⢰⡆⠀⢰⡆⢀⣴⠖⠀⢠⡶⠶⠶⡦⠀⠀⠀⣰⣶⡀

  ⣿⣿⠀⠀⠀⠀⠿⢿⣷⣦⡀⠀⠀⠀⠀⠀⣿⣿⠀⠀⣿⢾⣏⠀⠀⠀⣿⠀⠀⢸⡇⠀⢸⡷⣿⡁⠀⠀⠘⠷⠶⠶⣦⠀⠀⢠⡟⠘⣷

  ⢹⣿⡆⠀⠀⠀⣿⣶⠈⢻⣿⡆⠀⠀⠀⢰⣿⡏⠀⠀⠿⠀⠙⠷⠄⠀⠙⠷⠶⠟⠁⠀⠸⠇⠈⠻⠦⠀⠐⠷⠶⠶⠟⠀⠠⠿⠁⠀⠹⠧

  ⠀⢿⣿⣄⠀⠀⣿⣿⠀⠀⠿⣿⠀⠀⣠⣿⡿

  ⠀⠀⠻⣿⣷⡄⣿⣿⠀⠀⠀⢀⣠⣾⣿⠟    databroker-cli                

  ⠀⠀⠀⠈⠛⠇⢿⣿⣿⣿⣿⡿⠿⠛⠁     v0.6.1-dev.0                  



Successfully connected to http://0.0.0.0:55555/

kuksa.val.v1 > subscribe Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn

[subscribe]  OK [1]  

Subscription is now running in the background. Received data is identified by [1].

kuksa.val.v1 > subscribe Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed

[subscribe]  OK [2] Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed: true 


Subscription is now running in the background. Received data is identified by [2].

kuksa.val.v1 > subscribe Vehicle.Cabin.Seat.Row1.PassengerSide.AirbagIndicator.AirbagIsEnable.IsSignaling

[subscribe]  OK  

[3] Subscription is now running in the background. Received data is identified by [3].

kuksa.val.v1 > publish Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn true

[publish]  OK  

[1] Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn: true m

[2] Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed: true m

kuksa.val.v1 > publish Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn true

[1] Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn: true m

2;37m[publish]  OK  

kuksa.val.v1 > publish Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn false

[1] Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn: false m

[publish]  OK  

[2] Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed: false m

podman run -it --rm --network host ghcr.io/eclipse-kuksa/kuksa-databroker-cli:main --server 0.0.0.0:55555
Using kuksa.val.v1

  ⠀⠀⠀⢀⣤⣶⣾⣿⢸⣿⣿⣷⣶⣤⡀
  ⠀⠀⣴⣿⡿⠋⣿⣿⠀⠀⠀⠈⠙⢿⣿⣦⠀
  ⠀⣾⣿⠋⠀⠀⣿⣿⠀⠀⣶⣿⠀⠀⠙⣿⣷
  ⣸⣿⠇⠀⠀⠀⣿⣿⠠⣾⡿⠃⠀⠀⠀⠸⣿⣇⠀⠀⣶⠀⣠⡶⠂⠀⣶⠀⠀⢰⡆⠀⢰⡆⢀⣴⠖⠀⢠⡶⠶⠶⡦⠀⠀⠀⣰⣶⡀
  ⣿⣿⠀⠀⠀⠀⠿⢿⣷⣦⡀⠀⠀⠀⠀⠀⣿⣿⠀⠀⣿⢾⣏⠀⠀⠀⣿⠀⠀⢸⡇⠀⢸⡷⣿⡁⠀⠀⠘⠷⠶⠶⣦⠀⠀⢠⡟⠘⣷
  ⢹⣿⡆⠀⠀⠀⣿⣶⠈⢻⣿⡆⠀⠀⠀⢰⣿⡏⠀⠀⠿⠀⠙⠷⠄⠀⠙⠷⠶⠟⠁⠀⠸⠇⠈⠻⠦⠀⠐⠷⠶⠶⠟⠀⠠⠿⠁⠀⠹⠧
  ⠀⢿⣿⣄⠀⠀⣿⣿⠀⠀⠿⣿⠀⠀⣠⣿⡿
  ⠀⠀⠻⣿⣷⡄⣿⣿⠀⠀⠀⢀⣠⣾⣿⠟    databroker-cli
  ⠀⠀⠀⠈⠛⠇⢿⣿⣿⣿⣿⡿⠿⠛⠁     v0.6.1-dev.0

Successfully connected to http://0.0.0.0:55555/
kuksa.val.v1 > subscribe Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn
[subscribe]  OK [1]
Subscription is now running in the background. Received data is identified by [1].
kuksa.val.v1 > subscribe Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed
[subscribe]  OK [2] Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed: true

Subscription is now running in the background. Received data is identified by [2].
kuksa.val.v1 > subscribe Vehicle.Cabin.Seat.Row1.PassengerSide.AirbagIndicator.AirbagIsEnable.IsSignaling
[subscribe]  OK
[3] Subscription is now running in the background. Received data is identified by [3].
kuksa.val.v1 > publish Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn true
[publish]  OK
[1] Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn: true m
[2] Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed: true m
kuksa.val.v1 > publish Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn true
[1] Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn: true m
2;37m[publish]  OK
kuksa.val.v1 > publish Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn false
[1] Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn: false m
[publish]  OK
[2] Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed: false m

podman run -it --rm --network host ghcr.io/eclipse-kuksa/kuksa-databroker-cli:main --server 0.0.0.0:55555
Using kuksa.val.v1

  ⠀⠀⠀⢀⣤⣶⣾⣿⢸⣿⣿⣷⣶⣤⡀
  ⠀⠀⣴⣿⡿⠋⣿⣿⠀⠀⠀⠈⠙⢿⣿⣦⠀
  ⠀⣾⣿⠋⠀⠀⣿⣿⠀⠀⣶⣿⠀⠀⠙⣿⣷
  ⣸⣿⠇⠀⠀⠀⣿⣿⠠⣾⡿⠃⠀⠀⠀⠸⣿⣇⠀⠀⣶⠀⣠⡶⠂⠀⣶⠀⠀⢰⡆⠀⢰⡆⢀⣴⠖⠀⢠⡶⠶⠶⡦⠀⠀⠀⣰⣶⡀
  ⣿⣿⠀⠀⠀⠀⠿⢿⣷⣦⡀⠀⠀⠀⠀⠀⣿⣿⠀⠀⣿⢾⣏⠀⠀⠀⣿⠀⠀⢸⡇⠀⢸⡷⣿⡁⠀⠀⠘⠷⠶⠶⣦⠀⠀⢠⡟⠘⣷
  ⢹⣿⡆⠀⠀⠀⣿⣶⠈⢻⣿⡆⠀⠀⠀⢰⣿⡏⠀⠀⠿⠀⠙⠷⠄⠀⠙⠷⠶⠟⠁⠀⠸⠇⠈⠻⠦⠀⠐⠷⠶⠶⠟⠀⠠⠿⠁⠀⠹⠧
  ⠀⢿⣿⣄⠀⠀⣿⣿⠀⠀⠿⣿⠀⠀⣠⣿⡿
  ⠀⠀⠻⣿⣷⡄⣿⣿⠀⠀⠀⢀⣠⣾⣿⠟    databroker-cli
  ⠀⠀⠀⠈⠛⠇⢿⣿⣿⣿⣿⡿⠿⠛⠁     v0.6.1-dev.0

Successfully connected to http://0.0.0.0:55555/
kuksa.val.v1 > subscribe Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn
[subscribe]  OK [1]
Subscription is now running in the background. Received data is identified by [1].
kuksa.val.v1 > subscribe Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed
[subscribe]  OK [2] Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed: true

Subscription is now running in the background. Received data is identified by [2].
kuksa.val.v1 > subscribe Vehicle.Cabin.Seat.Row1.PassengerSide.AirbagIndicator.AirbagIsEnable.IsSignaling
[subscribe]  OK
[3] Subscription is now running in the background. Received data is identified by [3].
kuksa.val.v1 > publish Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn true
[publish]  OK
[1] Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn: true m
[2] Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed: true m
kuksa.val.v1 > publish Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn true
[1] Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn: true m
2;37m[publish]  OK
kuksa.val.v1 > publish Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn false
[1] Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn: false m
[publish]  OK
[2] Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed: false m
