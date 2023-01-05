#include <cstdio>
#include <cstring>
#include <iostream>
#include <pcap.h>

#include "sniffex.c"

auto& USAGE_STR = "Usage: ./pcap-feature-extraction [--test] [--file </path/to/file>]\n";

int test_pcap() {
  char errbuf[PCAP_ERRBUF_SIZE];
  pcap_if_t *devs;
  pcap_if_t dev;
  int ret_code;
  struct pcap_pkthdr header {};
  const u_char *packet;

  ret_code = pcap_findalldevs(&devs, errbuf);
  fprintf(stdout, "pcap_findalldevs exited with code: %d\n", ret_code);
  if (devs == nullptr) {
    fprintf(stderr, "Couldn't find default device: %s\n", errbuf);
    return (2);
  }

  // TODO select dev manually or from arguments.
  dev = devs[0];
  printf("Device: %s\n", dev.name);

  pcap_t *handle;
  handle = pcap_open_live(dev.name, BUFSIZ, 0, 1000, errbuf);
  if (handle == nullptr) {
    fprintf(stderr, "Couldn't open device %s: %s\n", dev.name, errbuf);
    return (2);
  }

  packet = pcap_next(handle, &header);
  printf("Got a packet with length of [%d]\n", header.len);
  if (header.len != 0) {
    print_hex_ascii_line(packet, header.len, 0);
  }
  pcap_close(handle);
  return (0);
}

int test_file(const char* path) {
  char errbuf[PCAP_ERRBUF_SIZE];
  pcap_t *handle;
  const u_char *packet;
  struct pcap_pkthdr header {};
  handle = pcap_open_offline(path, errbuf);
  if (handle == nullptr) {
    fprintf(stderr, "Couldn't open pcap file at %s: %s\n", path, errbuf);
    return (2);
  }
  packet = pcap_next(handle, &header);
  // Use the function from sniffex to print packet data.
  got_packet(nullptr, &header, packet);
  pcap_close(handle);
  return (0);
}

int main(int argc, char *argv[]) {
  if (argc == 1) {
    std::cout << USAGE_STR;
    return 0;
  }
  for (auto i = 0; i < argc; i++) {
    if (strcmp(argv[i], "--test") == 0) {
      test_pcap();
    }
    if (strcmp(argv[i], "--file") == 0) {
      if (i == argc - 1) {
        std::cout << USAGE_STR;
        exit (1);
      }
      i++;
      test_file(argv[i]);
    }
  }
}