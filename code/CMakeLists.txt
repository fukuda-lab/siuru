cmake_minimum_required (VERSION 3.2.0 FATAL_ERROR)
project (pcap-feature-extraction)

add_executable(${PROJECT_NAME}
  cpp-extract-features/main.cpp)

find_package(PcapPlusPlus REQUIRED)
message(STATUS "Using Pcap++ ${PcapPlusPlus_VERSION}")
message(STATUS "Include dir: ${PcapPlusPlus_INCLUDE_DIR}")
message(STATUS ${PCAPPLUSPLUS_LIBRARY_DIRS})

target_link_libraries(${PROJECT_NAME}
  pcap
  PcapPlusPlus::Pcap++)