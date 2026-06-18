#ifndef DIFFDRIVE_ARDUINO_ARDUINO_COMMS_HPP
#define DIFFDRIVE_ARDUINO_ARDUINO_COMMS_HPP

// #include <cstring>
#include <sstream>
// #include <cstdlib>
#include <libserial/SerialPort.h>
#include <iostream>


LibSerial::BaudRate convert_baud_rate(int baud_rate)
{
  // Just handle some common baud rates
  switch (baud_rate)
  {
    case 1200: return LibSerial::BaudRate::BAUD_1200;
    case 1800: return LibSerial::BaudRate::BAUD_1800;
    case 2400: return LibSerial::BaudRate::BAUD_2400;
    case 4800: return LibSerial::BaudRate::BAUD_4800;
    case 9600: return LibSerial::BaudRate::BAUD_9600;
    case 19200: return LibSerial::BaudRate::BAUD_19200;
    case 38400: return LibSerial::BaudRate::BAUD_38400;
    case 57600: return LibSerial::BaudRate::BAUD_57600;
    case 115200: return LibSerial::BaudRate::BAUD_115200;
    case 230400: return LibSerial::BaudRate::BAUD_230400;
    default:
      std::cout << "Error! Baud rate " << baud_rate << " not supported! Default to 57600" << std::endl;
      return LibSerial::BaudRate::BAUD_57600;
  }
}

class ArduinoComms
{

public:

  ArduinoComms() = default;

  void connect(const std::string &serial_device, int32_t baud_rate, int32_t timeout_ms)
  {  
    timeout_ms_ = timeout_ms;
    serial_conn_.Open(serial_device);
    serial_conn_.SetBaudRate(convert_baud_rate(baud_rate));
  }

  void disconnect()
  {
    serial_conn_.Close();
  }

  bool connected() const
  {
    return serial_conn_.IsOpen();
  }


  std::string send_msg(const std::string &msg_to_send, bool print_output = false)
  {
    serial_conn_.FlushIOBuffers(); // Just in case
    serial_conn_.Write(msg_to_send);

    std::string response = "";
    try
    {
      // Responses end with \r\n so we will read up to (and including) the \n.
      serial_conn_.ReadLine(response, '\n', timeout_ms_);
    }
    catch (const LibSerial::ReadTimeout&)
    {
        std::cerr << "The ReadByte() call has timed out." << std::endl ;
    }

    if (print_output)
    {
      std::cout << "Sent: " << msg_to_send << " Recv: " << response << std::endl;
    }

    return response;
  }


  void send_empty_msg()
  {
    std::string response = send_msg("\r");
  }

  void read_encoder_values(int &val_1, int &val_2)
  {
    std::string response = send_msg("e\r");

    std::string delimiter = " ";
    size_t del_pos = response.find(delimiter);
    std::string token_1 = response.substr(0, del_pos);
    std::string token_2 = response.substr(del_pos + delimiter.length());

    val_1 = std::atoi(token_1.c_str());
    val_2 = std::atoi(token_2.c_str());
  }

  std::string reset_encoder_values() {
    std::string response = send_msg("r\r");
    return response;
  }

  void set_strip_color(int r, int g, int b) {
    std::stringstream ss;
    ss << "l " << r << " " << g << " " << b << "\r";
    //std::cout << r << " " << g << " " << b << std::endl;
    send_msg(ss.str());
    //send_msg("l 255 255 255\r");
  }

  void set_motor_values(int val_1, int val_2)
  {
    std::stringstream ss;
    ss << "m " << val_1 << " " << val_2 << "\r";
    send_msg(ss.str());
  }

  void set_pid_values(int k_p, int k_d, int k_i, int k_o)
  {
    std::stringstream ss;
    ss << "u " << k_p << ":" << k_d << ":" << k_i << ":" << k_o << "\r";
    send_msg(ss.str());
  }

  void read_imu_values(double &ax, double &ay, double &az,
                     double &gx, double &gy, double &gz,
                     double &mx, double &my, double &mz)
{
  serial_conn_.FlushIOBuffers();
  serial_conn_.Write("i\r");

  std::string response = "";
  try {
    serial_conn_.ReadLine(response, '\n', 50);
  }
  catch (const LibSerial::ReadTimeout&) {
    std::cerr << "[IMU] Timeout" << std::endl;
    return;
  }

  // чистим \r \n пробелы по краям
  while (!response.empty() &&
         (response.back() == '\r' || response.back() == '\n'))
    response.pop_back();

  std::vector<std::string> values;
  std::istringstream ss(response);
  std::string token;
  while (std::getline(ss, token, ' ')) {
    if (!token.empty()) values.push_back(token);
  }

  if (values.size() != 9) {
    std::cerr << "[IMU] Bad response (" << values.size()
              << " tokens): " << response << std::endl;
    return;
  }

  try {
    ax = std::stod(values[0]); ay = std::stod(values[1]); az = std::stod(values[2]);
    gx = std::stod(values[3]); gy = std::stod(values[4]); gz = std::stod(values[5]);
    mx = std::stod(values[6]); my = std::stod(values[7]); mz = std::stod(values[8]);
  }
  catch (const std::exception &e) {
    std::cerr << "[IMU] Parse error: " << e.what()
              << " | " << response << std::endl;
  }
}

private:
    LibSerial::SerialPort serial_conn_;
    int timeout_ms_;
};

#endif // DIFFDRIVE_ARDUINO_ARDUINO_COMMS_HPP
