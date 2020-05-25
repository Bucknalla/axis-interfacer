# API

- in order for a port to be matched to a xilinx design, it must at least contain the interface port name somewhere in its name. For example "random_user_PORT_TValid_thing" would be a valid AXIS TVALID interface. 
- interfaces will only be matched if 1. they are enabled by the user and 2. if all required ports are matched.