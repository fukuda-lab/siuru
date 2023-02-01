#include <cstdio>
#include <cstring>
#include <iostream>

#include "PcapPlusPlus/Common++/header/IpAddress.h"
#include "PcapPlusPlus/Pcap++/header/PcapFileDevice.h"
#include "PcapPlusPlus/Packet++/header/IPv4Layer.h"
#include "PcapPlusPlus/Packet++/header/Packet.h"
#include "PcapPlusPlus/Packet++/header/RawPacket.h"

auto& USAGE_STR = "Usage: ./pcap-feature-extraction";

int test_pcap() {
  return (0);
}

int test_file(const char* path) {
  // open a pcap file for reading
  pcpp::PcapFileReaderDevice reader(path);
  if (!reader.open())
  {
    std::cerr << "Error opening the pcap file" << std::endl;
    return 1;
  }

  // read the first packet from the file
  pcpp::RawPacket rawPacket;
  if (!reader.getNextPacket(rawPacket))
  {
    std::cerr << "Couldn't read the first packet in the file" << std::endl;
    return 1;
  }

  // parse the raw packet into a parsed packet
  pcpp::Packet parsedPacket(&rawPacket);

  // verify the packet is IPv4
  if (parsedPacket.isPacketOfType(pcpp::IPv4)) {
    // extract source and dest IPs
    pcpp::IPv4Address srcIP = parsedPacket.getLayerOfType<pcpp::IPv4Layer>()->getSrcIPv4Address();
    pcpp::IPv4Address destIP = parsedPacket.getLayerOfType<pcpp::IPv4Layer>()->getDstIPv4Address();

    // print source and dest IPs
    std::cout << "Source IP is '" << srcIP << "'; Dest IP is '" << destIP << "'" << std::endl;
  }
  else {
    std::cout << "Not an IPv4 packet" << std::endl;
  }

  // close the file
  reader.close();

  return 0;


  return (0);
}

void packet_to_features(u_char *args, const struct pcap_pkthdr *header, const u_char *packet) {
//  const struct sniff_ip *ip;
//  const struct sniff_tcp *tcp;
//  ip = (struct sniff_ip*)(packet + SIZE_ETHERNET);
//
//  if (ip->ip_p == IPPROTO_TCP) {
//    tcp = (struct sniff_tcp *)(packet + SIZE_ETHERNET + IP_HL(ip) * 4);
//
//    // TODO input validation and error catching.
//
//    const char *src_host = inet_ntoa(ip->ip_src);
//    const char *dst_host = inet_ntoa(ip->ip_dst);
//    const uint16_t src_port = ntohs(tcp->th_sport);
//    const uint16_t dst_port = ntohs(tcp->th_dport);
//    auto& TCP_PROTO = "tcp";
//    printf("%s %s %d %d %s {", src_host, dst_host, src_port, dst_port, TCP_PROTO);
//
//    // TODO calculate and print features.
//    // Timestamp.
//    printf("\"ts\": %ld, ", header->ts.tv_sec*1000000L + header->ts.tv_usec);
//    // IP packet length.
//    printf("\"ip_len\": %hu, ", ip->ip_len);
//    // TCP segment length.
//    printf("\"tcp_len\": %d}\n", ip->ip_len - ip->ip_off);
//  }
}

int stream_file(const char* path) {
//  char errbuf[PCAP_ERRBUF_SIZE];
//  pcap_t *handle;
//  handle = pcap_open_offline(path, errbuf);
//  if (handle == nullptr) {
//    fprintf(stderr, "Couldn't open pcap file at %s: %s\n", path, errbuf);
//    return (2);
//  }
//  pcap_loop(handle, -1, packet_to_features, nullptr);
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
    if (strcmp(argv[i], "--test-file") == 0) {
      if (i == argc - 1) {
        std::cout << USAGE_STR;
        exit (1);
      }
      i++;
      test_file(argv[i]);
    }
    if (strcmp(argv[i], "--stream") == 0) {
      if (i == argc - 1) {
        std::cout << USAGE_STR;
        exit (1);
      }
      i++;
      stream_file(argv[i]);
    }
  }
}