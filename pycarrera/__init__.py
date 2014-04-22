import serial

END_OF_TRANSMISSION_CHARACTER = '$'
COMMAND_PREFIX = '"'
CONTROL_UNIT_BAUD_RATE = 19200
MAXIMUM_RESPONSE_LENGTH_IN_BYTES = 16
RESPONSE_READ_TIMEOUT_IN_SECONDS = 1
UNKNOWN_COMMAND_CHARACTER = '#'

GET_VERSION_COMMAND = '0'
START_RACE_COMMAND = "="

class CommunicationException(Exception):
    pass

class ControlUnitClient(object):

    def __init__(self, serial_port_name):
        self.serial_port_name = serial_port_name
        self.serial_port = None

    def connect(self):
        self.serial_port = serial.Serial()
        self.serial_port.port = self.serial_port_name
        self.serial_port.baudrate = CONTROL_UNIT_BAUD_RATE
        self.serial_port.timeout = RESPONSE_READ_TIMEOUT_IN_SECONDS
        self.serial_port.open()

    def send_command(self, command):
        command_string = self.COMMAND_PREFIX + command
        self.serial_port.write(command_string)
        self.serial_port.flush()
        response = self._read_until_EOT()

        if response:
            # The first character of the response is the issued command repeated back
            repeated_command = response.pop(0)

            if not repeated_command == command:
                raise CommunicationException("Unrecognized command %s" % repeated_command)

            checksum = response.pop()

        return response or None


    @property
    def control_unit_version(self):
        # Response is in the form VVVV, where V is a part of the version
        response = self.send_command(GET_VERSION_COMMAND)
        return str(response)


    def _read_until_EOT(self):
        """Carrera Control Unit responses are terminated with a '$' character.
        We read the response until we see this and return everything up to that character."""
        response_data = bytearray()

        while True:
            response_byte = self.serial_port.read(1)

            if response_byte:
                if response_byte == END_OF_TRANSMISSION_CHARACTER:
                    break;
                if response_byte == UNKNOWN_COMMAND_CHARACTER:
                    break;
                else:
                    response_data.extend(response_byte)
            else:
                break

        return response_data

    def start_race(self):
        """Start the race anew."""
        return self.send_command(START_RACE_COMMAND)