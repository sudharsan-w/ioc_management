from sqlalchemy import Column, Text, Boolean, Numeric, DateTime, ARRAY, Uuid
from globals_ import sql_Base

class IpEnrichment(sql_Base):
    __tablename__ = "ip_enrichment"
    ip = Column(Text(), primary_key=True)
    asn = Column(Text(), nullable=True)
    organization_name = Column(Text(), nullable=True)
    domain_name = Column(Text(), nullable=True)
    entity_type = Column(Text(), nullable=True)
    tor = Column(Boolean(), nullable=True)
    proxy = Column(Boolean(), nullable=True)
    vpn = Column(Boolean(), nullable=True)
    hosting = Column(Boolean(), nullable=True)
    relay = Column(Boolean(), nullable=True)
    service = Column(Boolean(), nullable=True)
    country = Column(Text(), nullable=True)
    city = Column(Text(), nullable=True)
    region = Column(Text(), nullable=True)
    continent = Column(Text(), nullable=True)
    geo_latitude = Column(Numeric(precision=9, scale=6), nullable=True)
    geo_longitude = Column(Numeric(precision=9, scale=6), nullable=True)
    blacklist = Column(Boolean())
    blacklist_sources = Column(ARRAY(Text), default=[])
    blacklist_datepublished = Column(DateTime(), nullable=True)
    ip_reputation = Column(Numeric(precision=10, scale=5), nullable=True)
    threat_types = Column(ARRAY(Text), default=[])
    

class NetFlow(sql_Base):
    __tablename__ = "refined_netflow"
    id = Column(Uuid(), primary_key=True)
    flow_start_milliseconds = Column(Text())
    flow_end_milliseconds = Column(Text())
    ipv4_src_addr = Column(Text())
    l4_src_port = Column(Text())
    ipv4_dst_addr = Column(Text())
    l4_dst_port = Column(Text())
    protocol = Column(Text())
    l7_proto = Column(Text())
    in_bytes = Column(Text())
    in_pkts = Column(Text())
    out_bytes = Column(Text())
    out_pkts = Column(Text())
    tcp_flags = Column(Text())
    client_tcp_flags = Column(Text())
    server_tcp_flags = Column(Text())
    flow_duration_milliseconds = Column(Text())
    duration_in = Column(Text())
    duration_out = Column(Text())
    min_ttl = Column(Text())
    max_ttl = Column(Text())
    longest_flow_pkt = Column(Text())
    shortest_flow_pkt = Column(Text())
    min_ip_pkt_len = Column(Text())
    max_ip_pkt_len = Column(Text())
    src_to_dst_second_bytes = Column(Text())
    dst_to_src_second_bytes = Column(Text())
    retransmitted_in_bytes = Column(Text())
    retransmitted_in_pkts = Column(Text())
    retransmitted_out_bytes = Column(Text())
    retransmitted_out_pkts = Column(Text())
    src_to_dst_avg_throughput = Column(Text())
    dst_to_src_avg_throughput = Column(Text())
    num_pkts_up_to_128_bytes = Column(Text())
    num_pkts_128_to_256_bytes = Column(Text())
    num_pkts_256_to_512_bytes = Column(Text())
    num_pkts_512_to_1024_bytes = Column(Text())
    num_pkts_1024_to_1514_bytes = Column(Text())
    tcp_win_max_in = Column(Text())
    tcp_win_max_out = Column(Text())
    icmp_type = Column(Text())
    icmp_ipv4_type = Column(Text())
    dns_query_id = Column(Text())
    dns_query_type = Column(Text())
    dns_ttl_answer = Column(Text())
    ftp_command_ret_code = Column(Text())
    src_to_dst_iat_min = Column(Text())
    src_to_dst_iat_max = Column(Text())
    src_to_dst_iat_avg = Column(Text())
    src_to_dst_iat_stddev = Column(Text())
    dst_to_src_iat_min = Column(Text())
    dst_to_src_iat_max = Column(Text())
    dst_to_src_iat_avg = Column(Text())
    dst_to_src_iat_stddev = Column(Text())
    label = Column(Text())
    attack = Column(Text())
    src_country = Column(Text())
    src_region = Column(Text())
    src_lat = Column(Text())
    src_long = Column(Text())
    src_asn = Column(Text())
    src_organization_name = Column(Text())
    src_domain_name = Column(Text())
    src_entity_type = Column(Text())
    src_tor = Column(Text())
    src_proxy = Column(Text())
    src_vpn = Column(Text())
    src_hosting = Column(Text())
    src_relay = Column(Text())
    src_service = Column(Text())
    src_blacklisted = Column(Text())
    src_region_code = Column(Text())
    dest_country = Column(Text())
    dest_region = Column(Text())
    dest_lat = Column(Text())
    dest_long = Column(Text())
    dest_asn = Column(Text())
    dest_organization_name = Column(Text())
    dest_domain_name = Column(Text())
    dest_entity_type = Column(Text())
    dest_tor = Column(Text())
    dest_proxy = Column(Text())
    dest_vpn = Column(Text())
    dest_hosting = Column(Text())
    dest_relay = Column(Text())
    dest_service = Column(Text())
    dest_blacklisted = Column(Text())
    dest_region_code = Column(Text())
    protocol_name = Column(Text())
    application = Column(Text())
    flow_direction = Column(Text())
    is_suspicious = Column(Text())
    flow_start_timestamp = Column(Text())  # "%Y-%m-%d HH:MM:SS"
    flow_end_timestamp = Column(Text())  # "%Y-%m-%d HH:MM:SS"
    src_to_dst_throughput_mbps = Column(Text())
    dst_to_src_throughput_mbps = Column(Text())
    packet_size_category = Column(Text())
    tcp_flags_text = Column(Text())
    flow_duration_seconds = Column(Text())
