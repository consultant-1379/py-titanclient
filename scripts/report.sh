#!/usr/bin/env bash

readarray -td, logs <<< "$1"; declare -p logs > /dev/null;

logargs=""

for l in "${logs[@]}"; do
  logargs="-l $l $logargs"
done

tcli host log stat report xls -m -s $logargs -o "$2" \
   -u \
   -g rps \
   -g registration_total \
   -g registration_success \
   -g registration_failed \
   -g registration_retry \
   -g registration_gos \
   -g registration_gos_excluding_retry \
   -g call_cps \
   -g call_total \
   -g call_success \
   -g call_failed \
   -g call_retry \
   -g call_gos \
   -g call_gos_excluding_retry \
   -g subscribe_total \
   -g subscribe_success \
   -g subscribe_failed \
   -g subscribe_gos \
   -g message_cps \
   -g message_sent \
   -g message_received \
   -g message_success \
   -g message_failed \
   -g message_retry \
   -g message_gos \
   -g xcap_all_gos \
   -g xcap_all_sent \
   -g xcap_all_success \
   -g xcap_all_failed \
   -g xcap_all_timeout \
   -g xcap_put_gos \
   -g xcap_put_sent \
   -g xcap_put_success \
   -g xcap_put_failed \
   -g xcap_put_timeout \
   -g xcap_get_gos \
   -g xcap_get_sent \
   -g xcap_get_success \
   -g xcap_get_failed \
   -g xcap_get_timeout \
   -g xcap_delete_gos \
   -g xcap_delete_sent \
   -g xcap_delete_success \
   -g xcap_delete_failed \
   -g xcap_delete_timeout \
   -g xcap_post_create_gos \
   -g xcap_post_create_sent \
   -g xcap_post_create_success \
   -g xcap_post_create_failed \
   -g xcap_post_create_timeout \
   -g xcap_post_delete_gos \
   -g xcap_post_delete_sent \
   -g xcap_post_delete_success \
   -g xcap_post_delete_failed \
   -g xcap_post_delete_timeout \
   -g media_total \
   -g media_success \
   -g media_failed \
   -g media_unknown \
   -g media_dropped \
   -g media_error \
   -g media_packets_sent \
   -g media_packets_received \
   -g media_packets_lost \
   -g media_packets_duplicated \
   -g media_packets_late \
   -g media_packets_reordered \
   -g media_latency_95 \
   -g sip_outgoing_bye \
   -g sip_outgoing_retransmitted_bye \
   -g sip_incoming_bye \
   -g sip_outgoing_invite \
   -g sip_outgoing_retransmitted_invite \
   -g sip_incoming_invite \
   -g sip_outgoing_register \
   -c cps \
   -c rps \
   -c call_answer_time_min \
   -c call_holding_time_min \
   -c call_duration \
   -c rrps \
   -c reregistration_margin \
   -c user_count \
   -c simultaneous_calls \
   -c codec \
   -c protocol \
   -a "REGISTER(o)-401(i)-REGISTER(o)-200(i)" \
   -a "INVITE(o)-180(i)" \
   -a "INVITE(o)-200(i)" \
   -a "INVITE(o)-183(i)" \
   -a "INVITE(i)-180(o)" \
   -a "INVITE(i)-183(o)" \
   -a "BYE(o)-200(i)" \
   -a "HANDOVER_INVITE(o)-200(i)"
