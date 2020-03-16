class MysqlVarAttribute(object):
    VAR_SCOPE = enumerate(('session', 'global', 'both'))

    def __init__(self, cmd_line, option_file, system_var, status_var, var_scope, dynamic):
        self._cmd_line = cmd_line
        self._option_file = option_file
        self._system_var = system_var
        self._status_var = status_var
        self._var_scope = var_scope
        self._dynamic = dynamic

MYSQL57_CNF_VAR_PREFERENCE = {
    'client':('port',),
    'mysql':(['default-character-set','character-set-server'],),
    'mysqld':('port','basedir','plugin-dir','datadir','pid_file','socket','lc-messages-dir','character-set-server',
              'server-id','default-storage-engine','innodb_file_format','innodb_file_format_max','innodb_file_per_table',
              'innodb_log_buffer_size','innodb_buffer_pool_size','innodb_log_files_in_group','innodb_thread_concurrency',
              'innodb_flush_log_at_trx_commit','sync_binlog','thread_cache_size','max_connections','group_concat_max_len',
              'event_scheduler','show_compatibility_56','read_only','super_read_only','log-bin-trust-function-creators',
              'slow-query-log','slow_query_log_file','long_query_time','log_slow_slave_statements','binlog_format',
              'expire_logs_days','log_bin','log_bin_index','log_error','relay_log','relay_log_index','relay_log_info_file',
              'general_log_file','master_info_repository','relay_log_info_repository','log_slave_updates','gtid_mode',
              'enforce_gtid_consistency','max_binlog_size','innodb_log_file_size','innodb_log_files_in_group','query_cache_size',
              'tmp_table_size','myisam_max_sort_file_size','myisam_sort_buffer_size','key_buffer_size','read_buffer_size',
              'read_rnd_buffer_size','sort_buffer_size','bulk_insert_buffer_size','max_allowed_packet','sql_mode')
}

class MYSQL57_VAR(object):
    Y, N, S, G, B, V = range(6)

    _dict = {
        'abort-slave-event-count': (Y, Y, None, None, None, None),
        'Aborted_clients': (None, None, None, Y, G, N),
        'Aborted_connects': (None, None, None, Y, G, N),
        'allow-suspicious-udfs': (Y, Y, None, None, None, None),
        'ansi': (Y, Y, None, None, None, None),
        'audit-log': (Y, Y, None, None, None, None),
        'audit_log_buffer_size': (Y, Y, Y, None, G, N),
        'audit_log_compression': (Y, Y, Y, None, G, N),
        'audit_log_connection_policy': (Y, Y, Y, None, G, Y),
        'audit_log_current_session': (None, None, Y, None, B, N),
        'Audit_log_current_size': (None, None, None, Y, G, N),
        'audit_log_encryption': (Y, Y, Y, None, G, N),
        'Audit_log_event_max_drop_size': (None, None, None, Y, G, N),
        'Audit_log_events': (None, None, None, Y, G, N),
        'Audit_log_events_filtered': (None, None, None, Y, G, N),
        'Audit_log_events_lost': (None, None, None, Y, G, N),
        'Audit_log_events_written': (None, None, None, Y, G, N),
        'audit_log_exclude_accounts': (Y, Y, Y, None, G, Y),
        'audit_log_file': (Y, Y, Y, None, G, N),
        'audit_log_filter_id': (None, None, Y, None, B, N),
        'audit_log_flush': (None, None, Y, None, G, Y),
        'audit_log_format': (Y, Y, Y, None, G, N),
        'audit_log_include_accounts': (Y, Y, Y, None, G, Y),
        'audit_log_policy': (Y, Y, Y, None, G, N),
        'audit_log_read_buffer_size': (Y, Y, Y, None, V, V),
        'audit_log_rotate_on_size': (Y, Y, Y, None, G, Y),
        'audit_log_statement_policy': (Y, Y, Y, None, G, Y),
        'audit_log_strategy': (Y, Y, Y, None, G, N),
        'Audit_log_total_size': (None, None, None, Y, G, N),
        'Audit_log_write_waits': (None, None, None, Y, G, N),
        'authentication_ldap_sasl_auth_method_name': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_bind_base_dn': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_bind_root_dn': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_bind_root_pwd': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_ca_path': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_group_search_attr': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_group_search_filter': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_init_pool_size': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_log_status': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_max_pool_size': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_server_host': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_server_port': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_tls': (Y, Y, Y, None, G, Y),
        'authentication_ldap_sasl_user_search_attr': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_auth_method_name': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_bind_base_dn': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_bind_root_dn': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_bind_root_pwd': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_ca_path': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_group_search_attr': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_group_search_filter': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_init_pool_size': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_log_status': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_max_pool_size': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_server_host': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_server_port': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_tls': (Y, Y, Y, None, G, Y),
        'authentication_ldap_simple_user_search_attr': (Y, Y, Y, None, G, Y),
        'authentication_windows_log_level': (Y, Y, Y, None, G, N),
        'authentication_windows_use_principal_name': (Y, Y, Y, None, G, N),
        'auto_generate_certs': (Y, Y, Y, None, G, N),
        'auto_increment_increment': (Y, Y, Y, None, B, Y),
        'auto_increment_offset': (Y, Y, Y, None, B, Y),
        'autocommit': (Y, Y, Y, None, B, Y),
        'automatic_sp_privileges': (Y, Y, Y, None, G, Y),
        'avoid_temporal_upgrade': (Y, Y, Y, None, G, Y),
        'back_log': (Y, Y, Y, None, G, N),
        'basedir': (Y, Y, Y, None, G, N),
        'big_tables': (Y, Y, Y, None, B, Y),
        'bind_address': (Y, Y, Y, None, G, N),
        'Binlog_cache_disk_use': (None, None, None, Y, G, N),
        'binlog_cache_size': (Y, Y, Y, None, G, Y),
        'Binlog_cache_use': (None, None, None, Y, G, N),
        'binlog-checksum': (Y, Y, None, None, None, None),
        'binlog_checksum': (Y, Y, Y, None, G, Y),
        'binlog_direct_non_transactional_updates': (Y, Y, Y, None, B, Y),
        'binlog-do-db': (Y, Y, None, None, None, None),
        'binlog_error_action': (Y, Y, Y, None, G, Y),
        'binlog_format': (Y, Y, Y, None, B, Y),
        'binlog_group_commit_sync_delay': (Y, Y, Y, None, G, Y),
        'binlog_group_commit_sync_no_delay_count': (Y, Y, Y, None, G, Y),
        'binlog_gtid_simple_recovery': (Y, Y, Y, None, G, N),
        'binlog-ignore-db': (Y, Y, None, None, None, None),
        'binlog_max_flush_queue_time': (Y, Y, Y, None, G, Y),
        'binlog_order_commits': (Y, Y, Y, None, G, Y),
        'binlog-row-event-max-size': (Y, Y, None, None, None, None),
        'binlog_row_image': (Y, Y, Y, None, B, Y),
        'binlog_rows_query_log_events': (Y, Y, Y, None, B, Y),
        'Binlog_stmt_cache_disk_use': (None, None, None, Y, G, N),
        'binlog_stmt_cache_size': (Y, Y, Y, None, G, Y),
        'Binlog_stmt_cache_use': (None, None, None, Y, G, N),
        'binlog_transaction_dependency_history_size': (Y, Y, Y, None, G, Y),
        'binlog_transaction_dependency_tracking': (Y, Y, Y, None, G, Y),
        'block_encryption_mode': (Y, Y, Y, None, B, Y),
        'bootstrap': (Y, Y, None, None, None, None),
        'bulk_insert_buffer_size': (Y, Y, Y, None, B, Y),
        'Bytes_received': (None, None, None, Y, B, N),
        'Bytes_sent': (None, None, None, Y, B, N),
        'character_set_client': (None, None, Y, None, B, Y),
        'character-set-client-handshake': (Y, Y, None, None, None, None),
        'character_set_connection': (None, None, Y, None, B, Y),
        'character_set_database (note 1)': (None, None, Y, None, B, Y),
        'character_set_filesystem': (Y, Y, Y, None, B, Y),
        'character_set_results': (None, None, Y, None, B, Y),
        'character_set_server': (Y, Y, Y, None, B, Y),
        'character_set_system': (None, None, Y, None, G, N),
        'character_sets_dir': (Y, Y, Y, None, G, N),
        'check_proxy_users': (Y, Y, Y, None, G, Y),
        'chroot': (Y, Y, None, None, None, None),
        'collation_connection': (None, None, Y, None, B, Y),
        'collation_database (note 1)': (None, None, Y, None, B, Y),
        'collation_server': (Y, Y, Y, None, B, Y),
        'Com_admin_commands': (None, None, None, Y, B, N),
        'Com_alter_db': (None, None, None, Y, B, N),
        'Com_alter_db_upgrade': (None, None, None, Y, B, N),
        'Com_alter_event': (None, None, None, Y, B, N),
        'Com_alter_function': (None, None, None, Y, B, N),
        'Com_alter_procedure': (None, None, None, Y, B, N),
        'Com_alter_server': (None, None, None, Y, B, N),
        'Com_alter_table': (None, None, None, Y, B, N),
        'Com_alter_tablespace': (None, None, None, Y, B, N),
        'Com_alter_user': (None, None, None, Y, B, N),
        'Com_analyze': (None, None, None, Y, B, N),
        'Com_assign_to_keycache': (None, None, None, Y, B, N),
        'Com_begin': (None, None, None, Y, B, N),
        'Com_binlog': (None, None, None, Y, B, N),
        'Com_call_procedure': (None, None, None, Y, B, N),
        'Com_change_db': (None, None, None, Y, B, N),
        'Com_change_master': (None, None, None, Y, B, N),
        'Com_change_repl_filter': (None, None, None, Y, B, N),
        'Com_check': (None, None, None, Y, B, N),
        'Com_checksum': (None, None, None, Y, B, N),
        'Com_commit': (None, None, None, Y, B, N),
        'Com_create_db': (None, None, None, Y, B, N),
        'Com_create_event': (None, None, None, Y, B, N),
        'Com_create_function': (None, None, None, Y, B, N),
        'Com_create_index': (None, None, None, Y, B, N),
        'Com_create_procedure': (None, None, None, Y, B, N),
        'Com_create_server': (None, None, None, Y, B, N),
        'Com_create_table': (None, None, None, Y, B, N),
        'Com_create_trigger': (None, None, None, Y, B, N),
        'Com_create_udf': (None, None, None, Y, B, N),
        'Com_create_user': (None, None, None, Y, B, N),
        'Com_create_view': (None, None, None, Y, B, N),
        'Com_dealloc_sql': (None, None, None, Y, B, N),
        'Com_delete': (None, None, None, Y, B, N),
        'Com_delete_multi': (None, None, None, Y, B, N),
        'Com_do': (None, None, None, Y, B, N),
        'Com_drop_db': (None, None, None, Y, B, N),
        'Com_drop_event': (None, None, None, Y, B, N),
        'Com_drop_function': (None, None, None, Y, B, N),
        'Com_drop_index': (None, None, None, Y, B, N),
        'Com_drop_procedure': (None, None, None, Y, B, N),
        'Com_drop_server': (None, None, None, Y, B, N),
        'Com_drop_table': (None, None, None, Y, B, N),
        'Com_drop_trigger': (None, None, None, Y, B, N),
        'Com_drop_user': (None, None, None, Y, B, N),
        'Com_drop_view': (None, None, None, Y, B, N),
        'Com_empty_query': (None, None, None, Y, B, N),
        'Com_execute_sql': (None, None, None, Y, B, N),
        'Com_explain_other': (None, None, None, Y, B, N),
        'Com_flush': (None, None, None, Y, B, N),
        'Com_get_diagnostics': (None, None, None, Y, B, N),
        'Com_grant': (None, None, None, Y, B, N),
        'Com_group_replication_start': (None, None, None, Y, G, N),
        'Com_group_replication_stop': (None, None, None, Y, G, N),
        'Com_ha_close': (None, None, None, Y, B, N),
        'Com_ha_open': (None, None, None, Y, B, N),
        'Com_ha_read': (None, None, None, Y, B, N),
        'Com_help': (None, None, None, Y, B, N),
        'Com_insert': (None, None, None, Y, B, N),
        'Com_insert_select': (None, None, None, Y, B, N),
        'Com_install_plugin': (None, None, None, Y, B, N),
        'Com_kill': (None, None, None, Y, B, N),
        'Com_load': (None, None, None, Y, B, N),
        'Com_lock_tables': (None, None, None, Y, B, N),
        'Com_optimize': (None, None, None, Y, B, N),
        'Com_preload_keys': (None, None, None, Y, B, N),
        'Com_prepare_sql': (None, None, None, Y, B, N),
        'Com_purge': (None, None, None, Y, B, N),
        'Com_purge_before_date': (None, None, None, Y, B, N),
        'Com_release_savepoint': (None, None, None, Y, B, N),
        'Com_rename_table': (None, None, None, Y, B, N),
        'Com_rename_user': (None, None, None, Y, B, N),
        'Com_repair': (None, None, None, Y, B, N),
        'Com_replace': (None, None, None, Y, B, N),
        'Com_replace_select': (None, None, None, Y, B, N),
        'Com_reset': (None, None, None, Y, B, N),
        'Com_resignal': (None, None, None, Y, B, N),
        'Com_revoke': (None, None, None, Y, B, N),
        'Com_revoke_all': (None, None, None, Y, B, N),
        'Com_rollback': (None, None, None, Y, B, N),
        'Com_rollback_to_savepoint': (None, None, None, Y, B, N),
        'Com_savepoint': (None, None, None, Y, B, N),
        'Com_select': (None, None, None, Y, B, N),
        'Com_set_option': (None, None, None, Y, B, N),
        'Com_show_authors': (None, None, None, Y, B, N),
        'Com_show_binlog_events': (None, None, None, Y, B, N),
        'Com_show_binlogs': (None, None, None, Y, B, N),
        'Com_show_charsets': (None, None, None, Y, B, N),
        'Com_show_collations': (None, None, None, Y, B, N),
        'Com_show_contributors': (None, None, None, Y, B, N),
        'Com_show_create_db': (None, None, None, Y, B, N),
        'Com_show_create_event': (None, None, None, Y, B, N),
        'Com_show_create_func': (None, None, None, Y, B, N),
        'Com_show_create_proc': (None, None, None, Y, B, N),
        'Com_show_create_table': (None, None, None, Y, B, N),
        'Com_show_create_trigger': (None, None, None, Y, B, N),
        'Com_show_create_user': (None, None, None, Y, B, N),
        'Com_show_databases': (None, None, None, Y, B, N),
        'Com_show_engine_logs': (None, None, None, Y, B, N),
        'Com_show_engine_mutex': (None, None, None, Y, B, N),
        'Com_show_engine_status': (None, None, None, Y, B, N),
        'Com_show_errors': (None, None, None, Y, B, N),
        'Com_show_events': (None, None, None, Y, B, N),
        'Com_show_fields': (None, None, None, Y, B, N),
        'Com_show_function_code': (None, None, None, Y, B, N),
        'Com_show_function_status': (None, None, None, Y, B, N),
        'Com_show_grants': (None, None, None, Y, B, N),
        'Com_show_keys': (None, None, None, Y, B, N),
        'Com_show_master_status': (None, None, None, Y, B, N),
        'Com_show_ndb_status': (None, None, None, Y, B, N),
        'Com_show_open_tables': (None, None, None, Y, B, N),
        'Com_show_plugins': (None, None, None, Y, B, N),
        'Com_show_privileges': (None, None, None, Y, B, N),
        'Com_show_procedure_code': (None, None, None, Y, B, N),
        'Com_show_procedure_status': (None, None, None, Y, B, N),
        'Com_show_processlist': (None, None, None, Y, B, N),
        'Com_show_profile': (None, None, None, Y, B, N),
        'Com_show_profiles': (None, None, None, Y, B, N),
        'Com_show_relaylog_events': (None, None, None, Y, B, N),
        'Com_show_slave_hosts': (None, None, None, Y, B, N),
        'Com_show_slave_status': (None, None, None, Y, B, N),
        'Com_show_status': (None, None, None, Y, B, N),
        'Com_show_storage_engines': (None, None, None, Y, B, N),
        'Com_show_table_status': (None, None, None, Y, B, N),
        'Com_show_tables': (None, None, None, Y, B, N),
        'Com_show_triggers': (None, None, None, Y, B, N),
        'Com_show_variables': (None, None, None, Y, B, N),
        'Com_show_warnings': (None, None, None, Y, B, N),
        'Com_shutdown': (None, None, None, Y, B, N),
        'Com_signal': (None, None, None, Y, B, N),
        'Com_slave_start': (None, None, None, Y, B, N),
        'Com_slave_stop': (None, None, None, Y, B, N),
        'Com_stmt_close': (None, None, None, Y, B, N),
        'Com_stmt_execute': (None, None, None, Y, B, N),
        'Com_stmt_fetch': (None, None, None, Y, B, N),
        'Com_stmt_prepare': (None, None, None, Y, B, N),
        'Com_stmt_reprepare': (None, None, None, Y, B, N),
        'Com_stmt_reset': (None, None, None, Y, B, N),
        'Com_stmt_send_long_data': (None, None, None, Y, B, N),
        'Com_truncate': (None, None, None, Y, B, N),
        'Com_uninstall_plugin': (None, None, None, Y, B, N),
        'Com_unlock_tables': (None, None, None, Y, B, N),
        'Com_update': (None, None, None, Y, B, N),
        'Com_update_multi': (None, None, None, Y, B, N),
        'Com_xa_commit': (None, None, None, Y, B, N),
        'Com_xa_end': (None, None, None, Y, B, N),
        'Com_xa_prepare': (None, None, None, Y, B, N),
        'Com_xa_recover': (None, None, None, Y, B, N),
        'Com_xa_rollback': (None, None, None, Y, B, N),
        'Com_xa_start': (None, None, None, Y, B, N),
        'completion_type': (Y, Y, Y, None, B, Y),
        'Compression': (None, None, None, Y, S, N),
        'concurrent_insert': (Y, Y, Y, None, G, Y),
        'connect_timeout': (Y, Y, Y, None, G, Y),
        'Connection_control_delay_generated': (None, None, None, Y, G, N),
        'connection_control_failed_connections_threshold': (Y, Y, Y, None, G, Y),
        'connection_control_max_connection_delay': (Y, Y, Y, None, G, Y),
        'connection_control_min_connection_delay': (Y, Y, Y, None, G, Y),
        'Connection_errors_accept': (None, None, None, Y, G, N),
        'Connection_errors_internal': (None, None, None, Y, G, N),
        'Connection_errors_max_connections': (None, None, None, Y, G, N),
        'Connection_errors_peer_address': (None, None, None, Y, G, N),
        'Connection_errors_select': (None, None, None, Y, G, N),
        'Connection_errors_tcpwrap': (None, None, None, Y, G, N),
        'Connections': (None, None, None, Y, G, N),
        'console': (Y, Y, None, None, None, None),
        'core-file': (Y, Y, None, None, None, None),
        'core_file': (None, None, Y, None, G, N),
        'Created_tmp_disk_tables': (None, None, None, Y, B, N),
        'Created_tmp_files': (None, None, None, Y, G, N),
        'Created_tmp_tables': (None, None, None, Y, B, N),
        'daemon_memcached_enable_binlog': (Y, Y, Y, None, G, N),
        'daemon_memcached_engine_lib_name': (Y, Y, Y, None, G, N),
        'daemon_memcached_engine_lib_path': (Y, Y, Y, None, G, N),
        'daemon_memcached_option': (Y, Y, Y, None, G, N),
        'daemon_memcached_r_batch_size': (Y, Y, Y, None, G, N),
        'daemon_memcached_w_batch_size': (Y, Y, Y, None, G, N),
        'daemonize': (Y, Y, None, None, None, None),
        'datadir': (Y, Y, Y, None, G, N),
        'date_format': (None, None, Y, None, G, N),
        'datetime_format': (None, None, Y, None, G, N),
        'debug': (Y, Y, Y, None, B, Y),
        'debug_sync': (None, None, Y, None, S, Y),
        'debug-sync-timeout': (Y, Y, None, None, None, None),
        'default_authentication_plugin': (Y, Y, Y, None, G, N),
        'default_password_lifetime': (Y, Y, Y, None, G, Y),
        'default_storage_engine': (Y, Y, Y, None, B, Y),
        'default-time-zone': (Y, Y, None, None, None, None),
        'default_tmp_storage_engine': (Y, Y, Y, None, B, Y),
        'default_week_format': (Y, Y, Y, None, B, Y),
        'defaults-extra-file': (Y, None, None, None, None, None),
        'defaults-file': (Y, None, None, None, None, None),
        'defaults-group-suffix': (Y, None, None, None, None, None),
        'delay_key_write': (Y, Y, Y, None, G, Y),
        'Delayed_errors': (None, None, None, Y, G, N),
        'delayed_insert_limit': (Y, Y, Y, None, G, Y),
        'Delayed_insert_threads': (None, None, None, Y, G, N),
        'delayed_insert_timeout': (Y, Y, Y, None, G, Y),
        'delayed_queue_size': (Y, Y, Y, None, G, Y),
        'Delayed_writes': (None, None, None, Y, G, N),
        'des-key-file': (Y, Y, None, None, None, None),
        'disable-partition-engine-check': (Y, Y, None, None, None, None),
        'disabled_storage_engines': (Y, Y, Y, None, G, N),
        'disconnect_on_expired_password': (Y, Y, Y, None, G, N),
        'disconnect-slave-event-count': (Y, Y, None, None, None, None),
        'div_precision_increment': (Y, Y, Y, None, B, Y),
        'early-plugin-load': (Y, Y, None, None, None, None),
        'end_markers_in_json': (Y, Y, Y, None, B, Y),
        'enforce_gtid_consistency': (Y, Y, Y, None, G, V),
        'eq_range_index_dive_limit': (Y, Y, Y, None, B, Y),
        'error_count': (None, None, Y, None, S, N),
        'event_scheduler': (Y, Y, Y, None, G, Y),
        'exit-info': (Y, Y, None, None, None, None),
        'expire_logs_days': (Y, Y, Y, None, G, Y),
        'explicit_defaults_for_timestamp': (Y, Y, Y, None, B, Y),
        'external-locking': (Y, Y, None, None, None, None),
        'external_user': (None, None, Y, None, S, N),
        'federated': (Y, Y, None, None, None, None),
        'Firewall_access_denied': (None, None, None, Y, G, N),
        'Firewall_access_granted': (None, None, None, Y, G, N),
        'Firewall_cached_entries': (None, None, None, Y, G, N),
        'flush': (Y, Y, Y, None, G, Y),
        'Flush_commands': (None, None, None, Y, G, N),
        'flush_time': (Y, Y, Y, None, G, Y),
        'foreign_key_checks': (None, None, Y, None, B, Y),
        'ft_boolean_syntax': (Y, Y, Y, None, G, Y),
        'ft_max_word_len': (Y, Y, Y, None, G, N),
        'ft_min_word_len': (Y, Y, Y, None, G, N),
        'ft_query_expansion_limit': (Y, Y, Y, None, G, N),
        'ft_stopword_file': (Y, Y, Y, None, G, N),
        'gdb': (Y, Y, None, None, None, None),
        'general_log': (Y, Y, Y, None, G, Y),
        'general_log_file': (Y, Y, Y, None, G, Y),
        'group_concat_max_len': (Y, Y, Y, None, B, Y),
        'group_replication_allow_local_disjoint_gtids_join': (Y, Y, Y, None, G, Y),
        'group_replication_allow_local_lower_version_join': (Y, Y, Y, None, G, Y),
        'group_replication_auto_increment_increment': (Y, Y, Y, None, G, Y),
        'group_replication_bootstrap_group': (Y, Y, Y, None, G, Y),
        'group_replication_components_stop_timeout': (Y, Y, Y, None, G, Y),
        'group_replication_compression_threshold': (Y, Y, Y, None, G, Y),
        'group_replication_enforce_update_everywhere_checks': (Y, Y, Y, None, G, Y),
        'group_replication_exit_state_action': (Y, Y, Y, None, G, Y),
        'group_replication_flow_control_applier_threshold': (Y, Y, Y, None, G, Y),
        'group_replication_flow_control_certifier_threshold': (Y, Y, Y, None, G, Y),
        'group_replication_flow_control_mode': (Y, Y, Y, None, G, Y),
        'group_replication_force_members': (Y, Y, Y, None, G, Y),
        'group_replication_group_name': (Y, Y, Y, None, G, Y),
        'group_replication_group_seeds': (Y, Y, Y, None, G, Y),
        'group_replication_gtid_assignment_block_size': (Y, Y, Y, None, G, Y),
        'group_replication_ip_whitelist': (Y, Y, Y, None, G, Y),
        'group_replication_local_address': (Y, Y, Y, None, G, Y),
        'group_replication_member_weight': (Y, Y, Y, None, G, Y),
        'group_replication_poll_spin_loops': (Y, Y, Y, None, G, Y),
        'group_replication_primary_member': (None, None, None, Y, G, N),
        'group_replication_recovery_complete_at': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_reconnect_interval': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_retry_count': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_ssl_ca': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_ssl_capath': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_ssl_cert': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_ssl_cipher': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_ssl_crl': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_ssl_crlpath': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_ssl_key': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_ssl_verify_server_cert': (Y, Y, Y, None, G, Y),
        'group_replication_recovery_use_ssl': (Y, Y, Y, None, G, Y),
        'group_replication_single_primary_mode': (Y, Y, Y, None, G, Y),
        'group_replication_ssl_mode': (Y, Y, Y, None, G, Y),
        'group_replication_start_on_boot': (Y, Y, Y, None, G, Y),
        'group_replication_transaction_size_limit': (Y, Y, Y, None, G, Y),
        'group_replication_unreachable_majority_timeout': (Y, Y, Y, None, G, Y),
        'gtid_executed': (None, None, Y, None, V, N),
        'gtid_executed_compression_period': (Y, Y, Y, None, G, Y),
        'gtid_mode': (Y, Y, Y, None, G, V),
        'gtid_next': (None, None, Y, None, S, Y),
        'gtid_owned': (None, None, Y, None, B, N),
        'gtid_purged': (None, None, Y, None, G, Y),
        'Handler_commit': (None, None, None, Y, B, N),
        'Handler_delete': (None, None, None, Y, B, N),
        'Handler_discover': (None, None, None, Y, B, N),
        'Handler_external_lock': (None, None, None, Y, B, N),
        'Handler_mrr_init': (None, None, None, Y, B, N),
        'Handler_prepare': (None, None, None, Y, B, N),
        'Handler_read_first': (None, None, None, Y, B, N),
        'Handler_read_key': (None, None, None, Y, B, N),
        'Handler_read_last': (None, None, None, Y, B, N),
        'Handler_read_next': (None, None, None, Y, B, N),
        'Handler_read_prev': (None, None, None, Y, B, N),
        'Handler_read_rnd': (None, None, None, Y, B, N),
        'Handler_read_rnd_next': (None, None, None, Y, B, N),
        'Handler_rollback': (None, None, None, Y, B, N),
        'Handler_savepoint': (None, None, None, Y, B, N),
        'Handler_savepoint_rollback': (None, None, None, Y, B, N),
        'Handler_update': (None, None, None, Y, B, N),
        'Handler_write': (None, None, None, Y, B, N),
        'have_compress': (None, None, Y, None, G, N),
        'have_crypt': (None, None, Y, None, G, N),
        'have_dynamic_loading': (None, None, Y, None, G, N),
        'have_geometry': (None, None, Y, None, G, N),
        'have_openssl': (None, None, Y, None, G, N),
        'have_profiling': (None, None, Y, None, G, N),
        'have_query_cache': (None, None, Y, None, G, N),
        'have_rtree_keys': (None, None, Y, None, G, N),
        'have_ssl': (None, None, Y, None, G, N),
        'have_statement_timeout': (None, None, Y, None, G, N),
        'have_symlink': (None, None, Y, None, G, N),
        'help': (Y, Y, None, None, None, None),
        'host_cache_size': (Y, Y, Y, None, G, Y),
        'hostname': (None, None, Y, None, G, N),
        'identity': (None, None, Y, None, S, Y),
        'ignore_builtin_innodb': (Y, Y, Y, None, G, N),
        'ignore-db-dir': (Y, Y, None, None, None, None),
        'ignore_db_dirs': (None, None, Y, None, G, N),
        'init_connect': (Y, Y, Y, None, G, Y),
        'init_file': (Y, Y, Y, None, G, N),
        'init_slave': (Y, Y, Y, None, G, Y),
        'initialize': (Y, Y, None, None, None, None),
        'initialize-insecure': (Y, Y, None, None, None, None),
        'innodb': (Y, Y, None, None, None, None),
        'innodb_adaptive_flushing': (Y, Y, Y, None, G, Y),
        'innodb_adaptive_flushing_lwm': (Y, Y, Y, None, G, Y),
        'innodb_adaptive_hash_index': (Y, Y, Y, None, G, Y),
        'innodb_adaptive_hash_index_parts': (Y, Y, Y, None, G, N),
        'innodb_adaptive_max_sleep_delay': (Y, Y, Y, None, G, Y),
        'innodb_api_bk_commit_interval': (Y, Y, Y, None, G, Y),
        'innodb_api_disable_rowlock': (Y, Y, Y, None, G, N),
        'innodb_api_enable_binlog': (Y, Y, Y, None, G, N),
        'innodb_api_enable_mdl': (Y, Y, Y, None, G, N),
        'innodb_api_trx_level': (Y, Y, Y, None, G, Y),
        'innodb_autoextend_increment': (Y, Y, Y, None, G, Y),
        'innodb_autoinc_lock_mode': (Y, Y, Y, None, G, N),
        'Innodb_available_undo_logs': (None, None, None, Y, G, N),
        'innodb_background_drop_list_empty': (Y, Y, Y, None, G, Y),
        'Innodb_buffer_pool_bytes_data': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_bytes_dirty': (None, None, None, Y, G, N),
        'innodb_buffer_pool_chunk_size': (Y, Y, Y, None, G, N),
        'innodb_buffer_pool_dump_at_shutdown': (Y, Y, Y, None, G, Y),
        'innodb_buffer_pool_dump_now': (Y, Y, Y, None, G, Y),
        'innodb_buffer_pool_dump_pct': (Y, Y, Y, None, G, Y),
        'Innodb_buffer_pool_dump_status': (None, None, None, Y, G, N),
        'innodb_buffer_pool_filename': (Y, Y, Y, None, G, Y),
        'innodb_buffer_pool_instances': (Y, Y, Y, None, G, N),
        'innodb_buffer_pool_load_abort': (Y, Y, Y, None, G, Y),
        'innodb_buffer_pool_load_at_startup': (Y, Y, Y, None, G, N),
        'innodb_buffer_pool_load_now': (Y, Y, Y, None, G, Y),
        'Innodb_buffer_pool_load_status': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_pages_data': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_pages_dirty': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_pages_flushed': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_pages_free': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_pages_latched': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_pages_misc': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_pages_total': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_read_ahead': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_read_ahead_evicted': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_read_ahead_rnd': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_read_requests': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_reads': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_resize_status': (None, None, None, Y, G, N),
        'innodb_buffer_pool_size': (Y, Y, Y, None, G, V),
        'Innodb_buffer_pool_wait_free': (None, None, None, Y, G, N),
        'Innodb_buffer_pool_write_requests': (None, None, None, Y, G, N),
        'innodb_change_buffer_max_size': (Y, Y, Y, None, G, Y),
        'innodb_change_buffering': (Y, Y, Y, None, G, Y),
        'innodb_change_buffering_debug': (Y, Y, Y, None, G, Y),
        'innodb_checksum_algorithm': (Y, Y, Y, None, G, Y),
        'innodb_checksums': (Y, Y, Y, None, G, N),
        'innodb_cmp_per_index_enabled': (Y, Y, Y, None, G, Y),
        'innodb_commit_concurrency': (Y, Y, Y, None, G, Y),
        'innodb_compress_debug': (Y, Y, Y, None, G, Y),
        'innodb_compression_failure_threshold_pct': (Y, Y, Y, None, G, Y),
        'innodb_compression_level': (Y, Y, Y, None, G, Y),
        'innodb_compression_pad_pct_max': (Y, Y, Y, None, G, Y),
        'innodb_concurrency_tickets': (Y, Y, Y, None, G, Y),
        'innodb_data_file_path': (Y, Y, Y, None, G, N),
        'Innodb_data_fsyncs': (None, None, None, Y, G, N),
        'innodb_data_home_dir': (Y, Y, Y, None, G, N),
        'Innodb_data_pending_fsyncs': (None, None, None, Y, G, N),
        'Innodb_data_pending_reads': (None, None, None, Y, G, N),
        'Innodb_data_pending_writes': (None, None, None, Y, G, N),
        'Innodb_data_read': (None, None, None, Y, G, N),
        'Innodb_data_reads': (None, None, None, Y, G, N),
        'Innodb_data_writes': (None, None, None, Y, G, N),
        'Innodb_data_written': (None, None, None, Y, G, N),
        'Innodb_dblwr_pages_written': (None, None, None, Y, G, N),
        'Innodb_dblwr_writes': (None, None, None, Y, G, N),
        'innodb_deadlock_detect': (Y, Y, Y, None, G, Y),
        'innodb_default_row_format': (Y, Y, Y, None, G, Y),
        'innodb_disable_resize_buffer_pool_debug': (Y, Y, Y, None, G, Y),
        'innodb_disable_sort_file_cache': (Y, Y, Y, None, G, Y),
        'innodb_doublewrite': (Y, Y, Y, None, G, N),
        'innodb_fast_shutdown': (Y, Y, Y, None, G, Y),
        'innodb_fil_make_page_dirty_debug': (Y, Y, Y, None, G, Y),
        'innodb_file_format': (Y, Y, Y, None, G, Y),
        'innodb_file_format_check': (Y, Y, Y, None, G, N),
        'innodb_file_format_max': (Y, Y, Y, None, G, Y),
        'innodb_file_per_table': (Y, Y, Y, None, G, Y),
        'innodb_fill_factor': (Y, Y, Y, None, G, Y),
        'innodb_flush_log_at_timeout': (Y, Y, Y, None, G, Y),
        'innodb_flush_log_at_trx_commit': (Y, Y, Y, None, G, Y),
        'innodb_flush_method': (Y, Y, Y, None, G, N),
        'innodb_flush_neighbors': (Y, Y, Y, None, G, Y),
        'innodb_flush_sync': (Y, Y, Y, None, G, Y),
        'innodb_flushing_avg_loops': (Y, Y, Y, None, G, Y),
        'innodb_force_load_corrupted': (Y, Y, Y, None, G, N),
        'innodb_force_recovery': (Y, Y, Y, None, G, N),
        'innodb_ft_aux_table': (None, None, Y, None, G, Y),
        'innodb_ft_cache_size': (Y, Y, Y, None, G, N),
        'innodb_ft_enable_diag_print': (Y, Y, Y, None, G, Y),
        'innodb_ft_enable_stopword': (Y, Y, Y, None, B, Y),
        'innodb_ft_max_token_size': (Y, Y, Y, None, G, N),
        'innodb_ft_min_token_size': (Y, Y, Y, None, G, N),
        'innodb_ft_num_word_optimize': (Y, Y, Y, None, G, Y),
        'innodb_ft_result_cache_limit': (Y, Y, Y, None, G, Y),
        'innodb_ft_server_stopword_table': (Y, Y, Y, None, G, Y),
        'innodb_ft_sort_pll_degree': (Y, Y, Y, None, G, N),
        'innodb_ft_total_cache_size': (Y, Y, Y, None, G, N),
        'innodb_ft_user_stopword_table': (Y, Y, Y, None, B, Y),
        'Innodb_have_atomic_builtins': (None, None, None, Y, G, N),
        'innodb_io_capacity': (Y, Y, Y, None, G, Y),
        'innodb_io_capacity_max': (Y, Y, Y, None, G, Y),
        'innodb_large_prefix': (Y, Y, Y, None, G, Y),
        'innodb_limit_optimistic_insert_debug': (Y, Y, Y, None, G, Y),
        'innodb_lock_wait_timeout': (Y, Y, Y, None, B, Y),
        'innodb_locks_unsafe_for_binlog': (Y, Y, Y, None, G, N),
        'innodb_log_buffer_size': (Y, Y, Y, None, G, N),
        'innodb_log_checkpoint_now': (Y, Y, Y, None, G, Y),
        'innodb_log_checksums': (Y, Y, Y, None, G, Y),
        'innodb_log_compressed_pages': (Y, Y, Y, None, G, Y),
        'innodb_log_file_size': (Y, Y, Y, None, G, N),
        'innodb_log_files_in_group': (Y, Y, Y, None, G, N),
        'innodb_log_group_home_dir': (Y, Y, Y, None, G, N),
        'Innodb_log_waits': (None, None, None, Y, G, N),
        'innodb_log_write_ahead_size': (Y, Y, Y, None, G, Y),
        'Innodb_log_write_requests': (None, None, None, Y, G, N),
        'Innodb_log_writes': (None, None, None, Y, G, N),
        'innodb_lru_scan_depth': (Y, Y, Y, None, G, Y),
        'innodb_max_dirty_pages_pct': (Y, Y, Y, None, G, Y),
        'innodb_max_dirty_pages_pct_lwm': (Y, Y, Y, None, G, Y),
        'innodb_max_purge_lag': (Y, Y, Y, None, G, Y),
        'innodb_max_purge_lag_delay': (Y, Y, Y, None, G, Y),
        'innodb_max_undo_log_size': (Y, Y, Y, None, G, Y),
        'innodb_merge_threshold_set_all_debug': (Y, Y, Y, None, G, Y),
        'innodb_monitor_disable': (Y, Y, Y, None, G, Y),
        'innodb_monitor_enable': (Y, Y, Y, None, G, Y),
        'innodb_monitor_reset': (Y, Y, Y, None, G, Y),
        'innodb_monitor_reset_all': (Y, Y, Y, None, G, Y),
        'Innodb_num_open_files': (None, None, None, Y, G, N),
        'innodb_numa_interleave': (Y, Y, Y, None, G, N),
        'innodb_old_blocks_pct': (Y, Y, Y, None, G, Y),
        'innodb_old_blocks_time': (Y, Y, Y, None, G, Y),
        'innodb_online_alter_log_max_size': (Y, Y, Y, None, G, Y),
        'innodb_open_files': (Y, Y, Y, None, G, N),
        'innodb_optimize_fulltext_only': (Y, Y, Y, None, G, Y),
        'Innodb_os_log_fsyncs': (None, None, None, Y, G, N),
        'Innodb_os_log_pending_fsyncs': (None, None, None, Y, G, N),
        'Innodb_os_log_pending_writes': (None, None, None, Y, G, N),
        'Innodb_os_log_written': (None, None, None, Y, G, N),
        'innodb_page_cleaners': (Y, Y, Y, None, G, N),
        'Innodb_page_size': (None, None, None, Y, G, N),
        'innodb_page_size': (Y, Y, Y, None, G, N),
        'Innodb_pages_created': (None, None, None, Y, G, N),
        'Innodb_pages_read': (None, None, None, Y, G, N),
        'Innodb_pages_written': (None, None, None, Y, G, N),
        'innodb_print_all_deadlocks': (Y, Y, Y, None, G, Y),
        'innodb_purge_batch_size': (Y, Y, Y, None, G, Y),
        'innodb_purge_rseg_truncate_frequency': (Y, Y, Y, None, G, Y),
        'innodb_purge_threads': (Y, Y, Y, None, G, N),
        'innodb_random_read_ahead': (Y, Y, Y, None, G, Y),
        'innodb_read_ahead_threshold': (Y, Y, Y, None, G, Y),
        'innodb_read_io_threads': (Y, Y, Y, None, G, N),
        'innodb_read_only': (Y, Y, Y, None, G, N),
        'innodb_replication_delay': (Y, Y, Y, None, G, Y),
        'innodb_rollback_on_timeout': (Y, Y, Y, None, G, N),
        'innodb_rollback_segments': (Y, Y, Y, None, G, Y),
        'Innodb_row_lock_current_waits': (None, None, None, Y, G, N),
        'Innodb_row_lock_time': (None, None, None, Y, G, N),
        'Innodb_row_lock_time_avg': (None, None, None, Y, G, N),
        'Innodb_row_lock_time_max': (None, None, None, Y, G, N),
        'Innodb_row_lock_waits': (None, None, None, Y, G, N),
        'Innodb_rows_deleted': (None, None, None, Y, G, N),
        'Innodb_rows_inserted': (None, None, None, Y, G, N),
        'Innodb_rows_read': (None, None, None, Y, G, N),
        'Innodb_rows_updated': (None, None, None, Y, G, N),
        'innodb_saved_page_number_debug': (Y, Y, Y, None, G, Y),
        'innodb_sort_buffer_size': (Y, Y, Y, None, G, N),
        'innodb_spin_wait_delay': (Y, Y, Y, None, G, Y),
        'innodb_stats_auto_recalc': (Y, Y, Y, None, G, Y),
        'innodb_stats_include_delete_marked': (Y, Y, Y, None, G, Y),
        'innodb_stats_method': (Y, Y, Y, None, G, Y),
        'innodb_stats_on_metadata': (Y, Y, Y, None, G, Y),
        'innodb_stats_persistent': (Y, Y, Y, None, G, Y),
        'innodb_stats_persistent_sample_pages': (Y, Y, Y, None, G, Y),
        'innodb_stats_sample_pages': (Y, Y, Y, None, G, Y),
        'innodb_stats_transient_sample_pages': (Y, Y, Y, None, G, Y),
        'innodb-status-file': (Y, Y, None, None, None, None),
        'innodb_status_output': (Y, Y, Y, None, G, Y),
        'innodb_status_output_locks': (Y, Y, Y, None, G, Y),
        'innodb_strict_mode': (Y, Y, Y, None, B, Y),
        'innodb_support_xa': (Y, Y, Y, None, B, Y),
        'innodb_sync_array_size': (Y, Y, Y, None, G, N),
        'innodb_sync_debug': (Y, Y, Y, None, G, N),
        'innodb_sync_spin_loops': (Y, Y, Y, None, G, Y),
        'innodb_table_locks': (Y, Y, Y, None, B, Y),
        'innodb_temp_data_file_path': (Y, Y, Y, None, G, N),
        'innodb_thread_concurrency': (Y, Y, Y, None, G, Y),
        'innodb_thread_sleep_delay': (Y, Y, Y, None, G, Y),
        'innodb_tmpdir': (Y, Y, Y, None, B, Y),
        'Innodb_truncated_status_writes': (None, None, None, Y, G, N),
        'innodb_trx_purge_view_update_only_debug': (Y, Y, Y, None, G, Y),
        'innodb_trx_rseg_n_slots_debug': (Y, Y, Y, None, G, Y),
        'innodb_undo_directory': (Y, Y, Y, None, G, N),
        'innodb_undo_log_truncate': (Y, Y, Y, None, G, Y),
        'innodb_undo_logs': (Y, Y, Y, None, G, Y),
        'innodb_undo_tablespaces': (Y, Y, Y, None, G, N),
        'innodb_use_native_aio': (Y, Y, Y, None, G, N),
        'innodb_version': (None, None, Y, None, G, N),
        'innodb_write_io_threads': (Y, Y, Y, None, G, N),
        'insert_id': (None, None, Y, None, S, Y),
        'install': (Y, None, None, None, None, None),
        'install-manual': (Y, None, None, None, None, None),
        'interactive_timeout': (Y, Y, Y, None, B, Y),
        'internal_tmp_disk_storage_engine': (Y, Y, Y, None, G, Y),
        'join_buffer_size': (Y, Y, Y, None, B, Y),
        'keep_files_on_create': (Y, Y, Y, None, B, Y),
        'Key_blocks_not_flushed': (None, None, None, Y, G, N),
        'Key_blocks_unused': (None, None, None, Y, G, N),
        'Key_blocks_used': (None, None, None, Y, G, N),
        'key_buffer_size': (Y, Y, Y, None, G, Y),
        'key_cache_age_threshold': (Y, Y, Y, None, G, Y),
        'key_cache_block_size': (Y, Y, Y, None, G, Y),
        'key_cache_division_limit': (Y, Y, Y, None, G, Y),
        'Key_read_requests': (None, None, None, Y, G, N),
        'Key_reads': (None, None, None, Y, G, N),
        'Key_write_requests': (None, None, None, Y, G, N),
        'Key_writes': (None, None, None, Y, G, N),
        'keyring_aws_cmk_id': (Y, Y, Y, None, G, Y),
        'keyring_aws_conf_file': (Y, Y, Y, None, G, N),
        'keyring_aws_data_file': (Y, Y, Y, None, G, N),
        'keyring_aws_region': (Y, Y, Y, None, G, Y),
        'keyring_encrypted_file_data': (Y, Y, Y, None, G, Y),
        'keyring_encrypted_file_password': (Y, Y, Y, None, G, Y),
        'keyring_file_data': (Y, Y, Y, None, G, Y),
        'keyring-migration-destination': (Y, Y, None, None, None, None),
        'keyring-migration-host': (Y, Y, None, None, None, None),
        'keyring-migration-password': (Y, Y, None, None, None, None),
        'keyring-migration-port': (Y, Y, None, None, None, None),
        'keyring-migration-socket': (Y, Y, None, None, None, None),
        'keyring-migration-source': (Y, Y, None, None, None, None),
        'keyring-migration-user': (Y, Y, None, None, None, None),
        'keyring_okv_conf_dir': (Y, Y, Y, None, G, Y),
        'keyring_operations': (None, None, Y, None, G, Y),
        'language': (Y, Y, Y, None, G, N),
        'large_files_support': (None, None, Y, None, G, N),
        'large_page_size': (None, None, Y, None, G, N),
        'large_pages': (Y, Y, Y, None, G, N),
        'last_insert_id': (None, None, Y, None, S, Y),
        'Last_query_cost': (None, None, None, Y, S, N),
        'Last_query_partial_plans': (None, None, None, Y, S, N),
        'lc_messages': (Y, Y, Y, None, B, Y),
        'lc_messages_dir': (Y, Y, Y, None, G, N),
        'lc_time_names': (Y, Y, Y, None, B, Y),
        'license': (None, None, Y, None, G, N),
        'local_infile': (Y, Y, Y, None, G, Y),
        'local-service': (Y, None, None, None, None, None),
        'lock_wait_timeout': (Y, Y, Y, None, B, Y),
        'Locked_connects': (None, None, None, Y, G, N),
        'locked_in_memory': (None, None, Y, None, G, N),
        'log-bin': (Y, Y, None, None, None, None),
        'log_bin': (None, None, Y, None, G, N),
        'log_bin_basename': (None, None, Y, None, G, N),
        'log_bin_index': (Y, Y, Y, None, G, N),
        'log_bin_trust_function_creators': (Y, Y, Y, None, G, Y),
        'log_bin_use_v1_row_events': (Y, Y, Y, None, G, N),
        'log_builtin_as_identified_by_password': (Y, Y, Y, None, G, Y),
        'log_error': (Y, Y, Y, None, G, N),
        'log_error_verbosity': (Y, Y, Y, None, G, Y),
        'log-isam': (Y, Y, None, None, None, None),
        'log_output': (Y, Y, Y, None, G, Y),
        'log_queries_not_using_indexes': (Y, Y, Y, None, G, Y),
        'log-raw': (Y, Y, None, None, None, None),
        'log-short-format': (Y, Y, None, None, None, None),
        'log_slave_updates': (Y, Y, Y, None, G, N),
        'log_slow_admin_statements': (Y, Y, Y, None, G, Y),
        'log_slow_slave_statements': (Y, Y, Y, None, G, Y),
        'log_statements_unsafe_for_binlog': (Y, Y, Y, None, G, Y),
        'log_syslog': (Y, Y, Y, None, G, Y),
        'log_syslog_facility': (Y, Y, Y, None, G, Y),
        'log_syslog_include_pid': (Y, Y, Y, None, G, Y),
        'log_syslog_tag': (Y, Y, Y, None, G, Y),
        'log-tc': (Y, Y, None, None, None, None),
        'log-tc-size': (Y, Y, None, None, None, None),
        'log_throttle_queries_not_using_indexes': (Y, Y, Y, None, G, Y),
        'log_timestamps': (Y, Y, Y, None, G, Y),
        'log_warnings': (Y, Y, Y, None, G, Y),
        'long_query_time': (Y, Y, Y, None, B, Y),
        'low_priority_updates': (Y, Y, Y, None, B, Y),
        'lower_case_file_system': (None, None, Y, None, G, N),
        'lower_case_table_names': (Y, Y, Y, None, G, N),
        'master-info-file': (Y, Y, None, None, None, None),
        'master_info_repository': (Y, Y, Y, None, G, Y),
        'master-retry-count': (Y, Y, None, None, None, None),
        'master_verify_checksum': (Y, Y, Y, None, G, Y),
        'max_allowed_packet': (Y, Y, Y, None, B, Y),
        'max_binlog_cache_size': (Y, Y, Y, None, G, Y),
        'max-binlog-dump-events': (Y, Y, None, None, None, None),
        'max_binlog_size': (Y, Y, Y, None, G, Y),
        'max_binlog_stmt_cache_size': (Y, Y, Y, None, G, Y),
        'max_connect_errors': (Y, Y, Y, None, G, Y),
        'max_connections': (Y, Y, Y, None, G, Y),
        'max_delayed_threads': (Y, Y, Y, None, B, Y),
        'max_digest_length': (Y, Y, Y, None, G, N),
        'max_error_count': (Y, Y, Y, None, B, Y),
        'max_execution_time': (Y, Y, Y, None, B, Y),
        'Max_execution_time_exceeded': (None, None, None, Y, B, N),
        'Max_execution_time_set': (None, None, None, Y, B, N),
        'Max_execution_time_set_failed': (None, None, None, Y, B, N),
        'max_heap_table_size': (Y, Y, Y, None, B, Y),
        'max_insert_delayed_threads': (None, None, Y, None, B, Y),
        'max_join_size': (Y, Y, Y, None, B, Y),
        'max_length_for_sort_data': (Y, Y, Y, None, B, Y),
        'max_points_in_geometry': (Y, Y, Y, None, B, Y),
        'max_prepared_stmt_count': (Y, Y, Y, None, G, Y),
        'max_relay_log_size': (Y, Y, Y, None, G, Y),
        'max_seeks_for_key': (Y, Y, Y, None, B, Y),
        'max_sort_length': (Y, Y, Y, None, B, Y),
        'max_sp_recursion_depth': (Y, Y, Y, None, B, Y),
        'max_tmp_tables': (None, None, Y, None, B, Y),
        'Max_used_connections': (None, None, None, Y, G, N),
        'Max_used_connections_time': (None, None, None, Y, G, N),
        'max_user_connections': (Y, Y, Y, None, B, Y),
        'max_write_lock_count': (Y, Y, Y, None, G, Y),
        'mecab_charset': (None, None, None, Y, G, N),
        'mecab_rc_file': (Y, Y, Y, None, G, N),
        'memlock': (Y, Y, None, None, None, None),
        'metadata_locks_cache_size': (Y, Y, Y, None, G, N),
        'metadata_locks_hash_instances': (Y, Y, Y, None, G, N),
        'min_examined_row_limit': (Y, Y, Y, None, B, Y),
        'multi_range_count': (Y, Y, Y, None, B, Y),
        'myisam-block-size': (Y, Y, None, None, None, None),
        'myisam_data_pointer_size': (Y, Y, Y, None, G, Y),
        'myisam_max_sort_file_size': (Y, Y, Y, None, G, Y),
        'myisam_mmap_size': (Y, Y, Y, None, G, N),
        'myisam_recover_options': (Y, Y, Y, None, G, N),
        'myisam_repair_threads': (Y, Y, Y, None, B, Y),
        'myisam_sort_buffer_size': (Y, Y, Y, None, B, Y),
        'myisam_stats_method': (Y, Y, Y, None, B, Y),
        'myisam_use_mmap': (Y, Y, Y, None, G, Y),
        'mysql_firewall_mode': (Y, Y, Y, None, G, Y),
        'mysql_firewall_trace': (Y, Y, Y, None, G, Y),
        'mysql_native_password_proxy_users': (Y, Y, Y, None, G, Y),
        'mysqlx': (Y, Y, None, None, None, None),
        'Mysqlx_address': (None, None, None, Y, G, N),
        'mysqlx_bind_address': (Y, Y, Y, None, G, N),
        'Mysqlx_bytes_received': (None, None, None, Y, B, N),
        'Mysqlx_bytes_sent': (None, None, None, Y, B, N),
        'mysqlx_connect_timeout': (Y, Y, Y, None, G, Y),
        'Mysqlx_connection_accept_errors': (None, None, None, Y, B, N),
        'Mysqlx_connection_errors': (None, None, None, Y, B, N),
        'Mysqlx_connections_accepted': (None, None, None, Y, G, N),
        'Mysqlx_connections_closed': (None, None, None, Y, G, N),
        'Mysqlx_connections_rejected': (None, None, None, Y, G, N),
        'Mysqlx_crud_create_view': (None, None, None, Y, B, N),
        'Mysqlx_crud_delete': (None, None, None, Y, B, N),
        'Mysqlx_crud_drop_view': (None, None, None, Y, B, N),
        'Mysqlx_crud_find': (None, None, None, Y, B, N),
        'Mysqlx_crud_insert': (None, None, None, Y, B, N),
        'Mysqlx_crud_modify_view': (None, None, None, Y, B, N),
        'Mysqlx_crud_update': (None, None, None, Y, B, N),
        'Mysqlx_errors_sent': (None, None, None, Y, B, N),
        'Mysqlx_errors_unknown_message_type': (None, None, None, Y, B, N),
        'Mysqlx_expect_close': (None, None, None, Y, B, N),
        'Mysqlx_expect_open': (None, None, None, Y, B, N),
        'mysqlx_idle_worker_thread_timeout': (Y, Y, Y, None, G, Y),
        'Mysqlx_init_error': (None, None, None, Y, B, N),
        'mysqlx_max_allowed_packet': (Y, Y, Y, None, G, Y),
        'mysqlx_max_connections': (Y, Y, Y, None, G, Y),
        'mysqlx_min_worker_threads': (Y, Y, Y, None, G, Y),
        'Mysqlx_notice_other_sent': (None, None, None, Y, B, N),
        'Mysqlx_notice_warning_sent': (None, None, None, Y, B, N),
        'Mysqlx_port': (None, None, None, Y, G, N),
        'mysqlx_port': (Y, Y, Y, None, G, N),
        'mysqlx_port_open_timeout': (Y, Y, Y, None, G, N),
        'Mysqlx_rows_sent': (None, None, None, Y, B, N),
        'Mysqlx_sessions': (None, None, None, Y, G, N),
        'Mysqlx_sessions_accepted': (None, None, None, Y, G, N),
        'Mysqlx_sessions_closed': (None, None, None, Y, G, N),
        'Mysqlx_sessions_fatal_error': (None, None, None, Y, G, N),
        'Mysqlx_sessions_killed': (None, None, None, Y, G, N),
        'Mysqlx_sessions_rejected': (None, None, None, Y, G, N),
        'Mysqlx_socket': (None, None, None, Y, G, N),
        'mysqlx_socket': (Y, Y, Y, None, G, N),
        'Mysqlx_ssl_accept_renegotiates': (None, None, None, Y, G, N),
        'Mysqlx_ssl_accepts': (None, None, None, Y, G, N),
        'Mysqlx_ssl_active': (None, None, None, Y, B, N),
        'mysqlx_ssl_ca': (Y, Y, Y, None, G, N),
        'mysqlx_ssl_capath': (Y, Y, Y, None, G, N),
        'mysqlx_ssl_cert': (Y, Y, Y, None, G, N),
        'Mysqlx_ssl_cipher': (None, None, None, Y, B, N),
        'mysqlx_ssl_cipher': (Y, Y, Y, None, G, N),
        'Mysqlx_ssl_cipher_list': (None, None, None, Y, B, N),
        'mysqlx_ssl_crl': (Y, Y, Y, None, G, N),
        'mysqlx_ssl_crlpath': (Y, Y, Y, None, G, N),
        'Mysqlx_ssl_ctx_verify_depth': (None, None, None, Y, B, N),
        'Mysqlx_ssl_ctx_verify_mode': (None, None, None, Y, B, N),
        'Mysqlx_ssl_finished_accepts': (None, None, None, Y, G, N),
        'mysqlx_ssl_key': (Y, Y, Y, None, G, N),
        'Mysqlx_ssl_server_not_after': (None, None, None, Y, G, N),
        'Mysqlx_ssl_server_not_before': (None, None, None, Y, G, N),
        'Mysqlx_ssl_verify_depth': (None, None, None, Y, G, N),
        'Mysqlx_ssl_verify_mode': (None, None, None, Y, G, N),
        'Mysqlx_ssl_version': (None, None, None, Y, B, N),
        'Mysqlx_stmt_create_collection': (None, None, None, Y, B, N),
        'Mysqlx_stmt_create_collection_index': (None, None, None, Y, B, N),
        'Mysqlx_stmt_disable_notices': (None, None, None, Y, B, N),
        'Mysqlx_stmt_drop_collection': (None, None, None, Y, B, N),
        'Mysqlx_stmt_drop_collection_index': (None, None, None, Y, B, N),
        'Mysqlx_stmt_enable_notices': (None, None, None, Y, B, N),
        'Mysqlx_stmt_ensure_collection': (None, None, None, Y, B, N),
        'Mysqlx_stmt_execute_mysqlx': (None, None, None, Y, B, N),
        'Mysqlx_stmt_execute_sql': (None, None, None, Y, B, N),
        'Mysqlx_stmt_execute_xplugin': (None, None, None, Y, B, N),
        'Mysqlx_stmt_kill_client': (None, None, None, Y, B, N),
        'Mysqlx_stmt_list_clients': (None, None, None, Y, B, N),
        'Mysqlx_stmt_list_notices': (None, None, None, Y, B, N),
        'Mysqlx_stmt_list_objects': (None, None, None, Y, B, N),
        'Mysqlx_stmt_ping': (None, None, None, Y, B, N),
        'Mysqlx_worker_threads': (None, None, None, Y, G, N),
        'Mysqlx_worker_threads_active': (None, None, None, Y, G, N),
        'named_pipe': (Y, Y, Y, None, G, N),
        'named_pipe_full_access_group': (Y, Y, Y, None, G, N),
        'ndb_allow_copying_alter_table': (Y, Y, Y, None, B, Y),
        'Ndb_api_bytes_received_count': (None, None, None, Y, G, N),
        'Ndb_api_bytes_received_count_session': (None, None, None, Y, S, N),
        'Ndb_api_bytes_received_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_bytes_sent_count': (None, None, None, Y, G, N),
        'Ndb_api_bytes_sent_count_session': (None, None, None, Y, S, N),
        'Ndb_api_bytes_sent_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_event_bytes_count': (None, None, None, Y, G, N),
        'Ndb_api_event_bytes_count_injector': (None, None, None, Y, G, N),
        'Ndb_api_event_data_count': (None, None, None, Y, G, N),
        'Ndb_api_event_data_count_injector': (None, None, None, Y, G, N),
        'Ndb_api_event_nondata_count': (None, None, None, Y, G, N),
        'Ndb_api_event_nondata_count_injector': (None, None, None, Y, G, N),
        'Ndb_api_pk_op_count': (None, None, None, Y, G, N),
        'Ndb_api_pk_op_count_session': (None, None, None, Y, S, N),
        'Ndb_api_pk_op_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_pruned_scan_count': (None, None, None, Y, G, N),
        'Ndb_api_pruned_scan_count_session': (None, None, None, Y, S, N),
        'Ndb_api_pruned_scan_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_range_scan_count': (None, None, None, Y, G, N),
        'Ndb_api_range_scan_count_session': (None, None, None, Y, S, N),
        'Ndb_api_range_scan_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_read_row_count': (None, None, None, Y, G, N),
        'Ndb_api_read_row_count_session': (None, None, None, Y, S, N),
        'Ndb_api_read_row_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_scan_batch_count': (None, None, None, Y, G, N),
        'Ndb_api_scan_batch_count_session': (None, None, None, Y, S, N),
        'Ndb_api_scan_batch_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_table_scan_count': (None, None, None, Y, G, N),
        'Ndb_api_table_scan_count_session': (None, None, None, Y, S, N),
        'Ndb_api_table_scan_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_trans_abort_count': (None, None, None, Y, G, N),
        'Ndb_api_trans_abort_count_session': (None, None, None, Y, S, N),
        'Ndb_api_trans_abort_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_trans_close_count': (None, None, None, Y, G, N),
        'Ndb_api_trans_close_count_session': (None, None, None, Y, S, N),
        'Ndb_api_trans_close_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_trans_commit_count': (None, None, None, Y, G, N),
        'Ndb_api_trans_commit_count_session': (None, None, None, Y, S, N),
        'Ndb_api_trans_commit_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_trans_local_read_row_count': (None, None, None, Y, G, N),
        'Ndb_api_trans_local_read_row_count_session': (None, None, None, Y, S, N),
        'Ndb_api_trans_local_read_row_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_trans_start_count': (None, None, None, Y, G, N),
        'Ndb_api_trans_start_count_session': (None, None, None, Y, S, N),
        'Ndb_api_trans_start_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_uk_op_count': (None, None, None, Y, G, N),
        'Ndb_api_uk_op_count_session': (None, None, None, Y, S, N),
        'Ndb_api_uk_op_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_wait_exec_complete_count': (None, None, None, Y, G, N),
        'Ndb_api_wait_exec_complete_count_session': (None, None, None, Y, S, N),
        'Ndb_api_wait_exec_complete_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_wait_meta_request_count': (None, None, None, Y, G, N),
        'Ndb_api_wait_meta_request_count_session': (None, None, None, Y, S, N),
        'Ndb_api_wait_meta_request_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_wait_nanos_count': (None, None, None, Y, G, N),
        'Ndb_api_wait_nanos_count_session': (None, None, None, Y, S, N),
        'Ndb_api_wait_nanos_count_slave': (None, None, None, Y, G, N),
        'Ndb_api_wait_scan_result_count': (None, None, None, Y, G, N),
        'Ndb_api_wait_scan_result_count_session': (None, None, None, Y, S, N),
        'Ndb_api_wait_scan_result_count_slave': (None, None, None, Y, G, N),
        'ndb_autoincrement_prefetch_sz': (Y, Y, Y, None, B, Y),
        'ndb_batch_size': (Y, Y, Y, None, G, N),
        'ndb_blob_read_batch_bytes': (Y, Y, Y, None, B, Y),
        'ndb_blob_write_batch_bytes': (Y, Y, Y, None, B, Y),
        'ndb_cache_check_time': (Y, Y, Y, None, G, Y),
        'ndb_clear_apply_status': (Y, None, Y, None, G, Y),
        'ndb_cluster_connection_pool': (Y, Y, Y, None, G, N),
        'ndb_cluster_connection_pool_nodeids': (Y, Y, Y, None, G, N),
        'Ndb_cluster_node_id': (None, None, None, Y, G, N),
        'Ndb_config_from_host': (None, None, None, Y, B, N),
        'Ndb_config_from_port': (None, None, None, Y, B, N),
        'Ndb_conflict_fn_epoch': (None, None, None, Y, G, N),
        'Ndb_conflict_fn_epoch_trans': (None, None, None, Y, G, N),
        'Ndb_conflict_fn_epoch2': (None, None, None, Y, G, N),
        'Ndb_conflict_fn_epoch2_trans': (None, None, None, Y, G, N),
        'Ndb_conflict_fn_max': (None, None, None, Y, G, N),
        'Ndb_conflict_fn_old': (None, None, None, Y, G, N),
        'Ndb_conflict_last_conflict_epoch': (None, None, Y, None, G, N),
        'Ndb_conflict_last_stable_epoch': (None, None, None, Y, G, N),
        'Ndb_conflict_reflected_op_discard_count': (None, None, None, Y, G, N),
        'Ndb_conflict_reflected_op_prepare_count': (None, None, None, Y, G, N),
        'Ndb_conflict_refresh_op_count': (None, None, None, Y, G, N),
        'Ndb_conflict_trans_conflict_commit_count': (None, None, None, Y, G, N),
        'Ndb_conflict_trans_detect_iter_count': (None, None, None, Y, G, N),
        'Ndb_conflict_trans_reject_count': (None, None, None, Y, G, N),
        'Ndb_conflict_trans_row_conflict_count': (None, None, None, Y, G, N),
        'Ndb_conflict_trans_row_reject_count': (None, None, None, Y, G, N),
        'ndb-connectstring': (Y, Y, None, None, None, None),
        'ndb_data_node_neighbour': (Y, Y, Y, None, G, Y),
        'ndb_default_column_format': (Y, Y, Y, None, G, Y),
        'ndb_default_column_format': (Y, Y, Y, None, G, Y),
        'ndb_deferred_constraints': (Y, Y, Y, None, B, Y),
        'ndb_deferred_constraints': (Y, Y, Y, None, B, Y),
        'ndb_distribution': (Y, Y, Y, None, G, Y),
        'ndb_distribution': (Y, Y, Y, None, G, Y),
        'Ndb_epoch_delete_delete_count': (None, None, None, Y, G, N),
        'ndb_eventbuffer_free_percent': (Y, Y, Y, None, G, Y),
        'ndb_eventbuffer_max_alloc': (Y, Y, Y, None, G, Y),
        'Ndb_execute_count': (None, None, None, Y, G, N),
        'ndb_extra_logging': (Y, Y, Y, None, G, Y),
        'ndb_force_send': (Y, Y, Y, None, B, Y),
        'ndb_fully_replicated': (Y, Y, Y, None, B, Y),
        'ndb_index_stat_enable': (Y, Y, Y, None, B, Y),
        'ndb_index_stat_option': (Y, Y, Y, None, B, Y),
        'ndb_join_pushdown': (None, None, Y, None, B, Y),
        'Ndb_last_commit_epoch_server': (None, None, None, Y, G, N),
        'Ndb_last_commit_epoch_session': (None, None, None, Y, S, N),
        'ndb_log_apply_status': (Y, Y, Y, None, G, N),
        'ndb_log_apply_status': (Y, Y, Y, None, G, N),
        'ndb_log_bin': (Y, None, Y, None, B, Y),
        'ndb_log_binlog_index': (Y, None, Y, None, G, Y),
        'ndb_log_empty_epochs': (Y, Y, Y, None, G, Y),
        'ndb_log_empty_epochs': (Y, Y, Y, None, G, Y),
        'ndb_log_empty_update': (Y, Y, Y, None, G, Y),
        'ndb_log_empty_update': (Y, Y, Y, None, G, Y),
        'ndb_log_exclusive_reads': (Y, Y, Y, None, B, Y),
        'ndb_log_exclusive_reads': (Y, Y, Y, None, B, Y),
        'ndb_log_orig': (Y, Y, Y, None, G, N),
        'ndb_log_orig': (Y, Y, Y, None, G, N),
        'ndb_log_transaction_id': (Y, Y, Y, None, G, N),
        'ndb_log_transaction_id': (None, None, Y, None, G, N),
        'ndb_log_update_as_write': (Y, Y, Y, None, G, Y),
        'ndb_log_update_minimal': (Y, Y, Y, None, G, Y),
        'ndb_log_updated_only': (Y, Y, Y, None, G, Y),
        'ndb-mgmd-host': (Y, Y, None, None, None, None),
        'ndb_nodeid': (Y, Y, None, Y, G, N),
        'Ndb_number_of_data_nodes': (None, None, None, Y, G, N),
        'ndb_optimization_delay': (Y, Y, Y, None, G, Y),
        'ndb_optimized_node_selection': (Y, Y, Y, None, G, N),
        'Ndb_pruned_scan_count': (None, None, None, Y, G, N),
        'Ndb_pushed_queries_defined': (None, None, None, Y, G, N),
        'Ndb_pushed_queries_dropped': (None, None, None, Y, G, N),
        'Ndb_pushed_queries_executed': (None, None, None, Y, G, N),
        'Ndb_pushed_reads': (None, None, None, Y, G, N),
        'ndb_read_backup': (Y, Y, Y, None, G, Y),
        'ndb_recv_thread_activation_threshold': (Y, Y, Y, None, G, Y),
        'ndb_recv_thread_cpu_mask': (Y, Y, Y, None, G, Y),
        'ndb_report_thresh_binlog_epoch_slip': (Y, Y, Y, None, G, Y),
        'ndb_report_thresh_binlog_mem_usage': (Y, Y, Y, None, G, Y),
        'ndb_row_checksum': (None, None, Y, None, B, Y),
        'Ndb_scan_count': (None, None, None, Y, G, N),
        'ndb_show_foreign_key_mock_tables': (Y, Y, Y, None, G, Y),
        'ndb_slave_conflict_role': (Y, Y, Y, None, G, Y),
        'Ndb_slave_max_replicated_epoch': (None, None, Y, None, G, N),
        'Ndb_system_name': (None, None, Y, None, G, N),
        'ndb_table_no_logging': (None, None, Y, None, S, Y),
        'ndb_table_temporary': (None, None, Y, None, S, Y),
        'ndb-transid-mysql-connection-map': (Y, None, None, None, None, None),
        'ndb_use_copying_alter_table': (None, None, Y, None, B, N),
        'ndb_use_exact_count': (None, None, Y, None, B, Y),
        'ndb_use_transactions': (Y, Y, Y, None, B, Y),
        'ndb_version': (None, None, Y, None, G, N),
        'ndb_version_string': (None, None, Y, None, G, N),
        'ndb_wait_connected': (Y, Y, Y, None, G, N),
        'ndb_wait_setup': (Y, Y, Y, None, G, N),
        'ndbcluster': (Y, Y, None, None, None, None),
        'ndbinfo_database': (None, None, Y, None, G, N),
        'ndbinfo_max_bytes': (Y, None, Y, None, B, Y),
        'ndbinfo_max_rows': (Y, None, Y, None, B, Y),
        'ndbinfo_offline': (None, None, Y, None, G, Y),
        'ndbinfo_show_hidden': (Y, None, Y, None, B, Y),
        'ndbinfo_table_prefix': (Y, None, Y, None, B, Y),
        'ndbinfo_version': (None, None, Y, None, G, N),
        'net_buffer_length': (Y, Y, Y, None, B, Y),
        'net_read_timeout': (Y, Y, Y, None, B, Y),
        'net_retry_count': (Y, Y, Y, None, B, Y),
        'net_write_timeout': (Y, Y, Y, None, B, Y),
        'new': (Y, Y, Y, None, B, Y),
        'ngram_token_size': (Y, Y, Y, None, G, N),
        'no-defaults': (Y, None, None, None, None, None),
        'Not_flushed_delayed_rows': (None, None, None, Y, G, N),
        'offline_mode': (Y, Y, Y, None, G, Y),
        'old': (Y, Y, Y, None, G, N),
        'old_alter_table': (Y, Y, Y, None, B, Y),
        'old_passwords': (Y, Y, Y, None, B, Y),
        'old-style-user-limits': (Y, Y, None, None, None, None),
        'Ongoing_anonymous_gtid_violating_transaction_count': (None, None, None, Y, G, N),
        'Ongoing_anonymous_transaction_count': (None, None, None, Y, G, N),
        'Ongoing_automatic_gtid_violating_transaction_count': (None, None, None, Y, G, N),
        'Open_files': (None, None, None, Y, G, N),
        'open_files_limit': (Y, Y, Y, None, G, N),
        'Open_streams': (None, None, None, Y, G, N),
        'Open_table_definitions': (None, None, None, Y, G, N),
        'Open_tables': (None, None, None, Y, B, N),
        'Opened_files': (None, None, None, Y, G, N),
        'Opened_table_definitions': (None, None, None, Y, B, N),
        'Opened_tables': (None, None, None, Y, B, N),
        'optimizer_prune_level': (Y, Y, Y, None, B, Y),
        'optimizer_search_depth': (Y, Y, Y, None, B, Y),
        'optimizer_switch': (Y, Y, Y, None, B, Y),
        'optimizer_trace': (Y, Y, Y, None, B, Y),
        'optimizer_trace_features': (Y, Y, Y, None, B, Y),
        'optimizer_trace_limit': (Y, Y, Y, None, B, Y),
        'optimizer_trace_max_mem_size': (Y, Y, Y, None, B, Y),
        'optimizer_trace_offset': (Y, Y, Y, None, B, Y),
        'parser_max_mem_size': (Y, Y, Y, None, B, Y),
        'partition': (Y, Y, None, None, None, None),
        'performance_schema': (Y, Y, Y, None, G, N),
        'Performance_schema_accounts_lost': (None, None, None, Y, G, N),
        'performance_schema_accounts_size': (Y, Y, Y, None, G, N),
        'Performance_schema_cond_classes_lost': (None, None, None, Y, G, N),
        'Performance_schema_cond_instances_lost': (None, None, None, Y, G, N),
        'performance-schema-consumer-events-stages-current': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-stages-history': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-stages-history-long': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-statements-current': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-statements-history': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-statements-history-long': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-transactions-current': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-transactions-history': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-transactions-history-long': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-waits-current': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-waits-history': (Y, Y, None, None, None, None),
        'performance-schema-consumer-events-waits-history-long': (Y, Y, None, None, None, None),
        'performance-schema-consumer-global-instrumentation': (Y, Y, None, None, None, None),
        'performance-schema-consumer-statements-digest': (Y, Y, None, None, None, None),
        'performance-schema-consumer-thread-instrumentation': (Y, Y, None, None, None, None),
        'Performance_schema_digest_lost': (None, None, None, Y, G, N),
        'performance_schema_digests_size': (Y, Y, Y, None, G, N),
        'performance_schema_events_stages_history_long_size': (Y, Y, Y, None, G, N),
        'performance_schema_events_stages_history_size': (Y, Y, Y, None, G, N),
        'performance_schema_events_statements_history_long_size': (Y, Y, Y, None, G, N),
        'performance_schema_events_statements_history_size': (Y, Y, Y, None, G, N),
        'performance_schema_events_transactions_history_long_size': (Y, Y, Y, None, G, N),
        'performance_schema_events_transactions_history_size': (Y, Y, Y, None, G, N),
        'performance_schema_events_waits_history_long_size': (Y, Y, Y, None, G, N),
        'performance_schema_events_waits_history_size': (Y, Y, Y, None, G, N),
        'Performance_schema_file_classes_lost': (None, None, None, Y, G, N),
        'Performance_schema_file_handles_lost': (None, None, None, Y, G, N),
        'Performance_schema_file_instances_lost': (None, None, None, Y, G, N),
        'Performance_schema_hosts_lost': (None, None, None, Y, G, N),
        'performance_schema_hosts_size': (Y, Y, Y, None, G, N),
        'Performance_schema_index_stat_lost': (None, None, None, Y, G, N),
        'performance-schema-instrument': (Y, Y, None, None, None, None),
        'Performance_schema_locker_lost': (None, None, None, Y, G, N),
        'performance_schema_max_cond_classes': (Y, Y, Y, None, G, N),
        'performance_schema_max_cond_instances': (Y, Y, Y, None, G, N),
        'performance_schema_max_digest_length': (Y, Y, Y, None, G, N),
        'performance_schema_max_file_classes': (Y, Y, Y, None, G, N),
        'performance_schema_max_file_handles': (Y, Y, Y, None, G, N),
        'performance_schema_max_file_instances': (Y, Y, Y, None, G, N),
        'performance_schema_max_index_stat': (Y, Y, Y, None, G, N),
        'performance_schema_max_memory_classes': (Y, Y, Y, None, G, N),
        'performance_schema_max_metadata_locks': (Y, Y, Y, None, G, N),
        'performance_schema_max_mutex_classes': (Y, Y, Y, None, G, N),
        'performance_schema_max_mutex_instances': (Y, Y, Y, None, G, N),
        'performance_schema_max_prepared_statements_instances': (Y, Y, Y, None, G, N),
        'performance_schema_max_program_instances': (Y, Y, Y, None, G, N),
        'performance_schema_max_rwlock_classes': (Y, Y, Y, None, G, N),
        'performance_schema_max_rwlock_instances': (Y, Y, Y, None, G, N),
        'performance_schema_max_socket_classes': (Y, Y, Y, None, G, N),
        'performance_schema_max_socket_instances': (Y, Y, Y, None, G, N),
        'performance_schema_max_sql_text_length': (Y, Y, Y, None, G, N),
        'performance_schema_max_stage_classes': (Y, Y, Y, None, G, N),
        'performance_schema_max_statement_classes': (Y, Y, Y, None, G, N),
        'performance_schema_max_statement_stack': (Y, Y, Y, None, G, N),
        'performance_schema_max_table_handles': (Y, Y, Y, None, G, N),
        'performance_schema_max_table_instances': (Y, Y, Y, None, G, N),
        'performance_schema_max_table_lock_stat': (Y, Y, Y, None, G, N),
        'performance_schema_max_thread_classes': (Y, Y, Y, None, G, N),
        'performance_schema_max_thread_instances': (Y, Y, Y, None, G, N),
        'Performance_schema_memory_classes_lost': (None, None, None, Y, G, N),
        'Performance_schema_metadata_lock_lost': (None, None, None, Y, G, N),
        'Performance_schema_mutex_classes_lost': (None, None, None, Y, G, N),
        'Performance_schema_mutex_instances_lost': (None, None, None, Y, G, N),
        'Performance_schema_nested_statement_lost': (None, None, None, Y, G, N),
        'Performance_schema_prepared_statements_lost': (None, None, None, Y, G, N),
        'Performance_schema_program_lost': (None, None, None, Y, G, N),
        'Performance_schema_rwlock_classes_lost': (None, None, None, Y, G, N),
        'Performance_schema_rwlock_instances_lost': (None, None, None, Y, G, N),
        'Performance_schema_session_connect_attrs_lost': (None, None, None, Y, G, N),
        'performance_schema_session_connect_attrs_size': (Y, Y, Y, None, G, N),
        'performance_schema_setup_actors_size': (Y, Y, Y, None, G, N),
        'performance_schema_setup_objects_size': (Y, Y, Y, None, G, N),
        'Performance_schema_socket_classes_lost': (None, None, None, Y, G, N),
        'Performance_schema_socket_instances_lost': (None, None, None, Y, G, N),
        'Performance_schema_stage_classes_lost': (None, None, None, Y, G, N),
        'Performance_schema_statement_classes_lost': (None, None, None, Y, G, N),
        'Performance_schema_table_handles_lost': (None, None, None, Y, G, N),
        'Performance_schema_table_instances_lost': (None, None, None, Y, G, N),
        'Performance_schema_table_lock_stat_lost': (None, None, None, Y, G, N),
        'Performance_schema_thread_classes_lost': (None, None, None, Y, G, N),
        'Performance_schema_thread_instances_lost': (None, None, None, Y, G, N),
        'Performance_schema_users_lost': (None, None, None, Y, G, N),
        'performance_schema_users_size': (Y, Y, Y, None, G, N),
        'pid_file': (Y, Y, Y, None, G, N),
        'plugin_dir': (Y, Y, Y, None, G, N),
        'plugin_load': (Y, Y, Y, None, G, N),
        'plugin_load_add': (Y, Y, Y, None, G, N),
        'plugin-xxx': (Y, Y, None, None, None, None),
        'port': (Y, Y, Y, None, G, N),
        'port-open-timeout': (Y, Y, None, None, None, None),
        'preload_buffer_size': (Y, Y, Y, None, B, Y),
        'Prepared_stmt_count': (None, None, None, Y, G, N),
        'print-defaults': (Y, None, None, None, None, None),
        'profiling': (None, None, Y, None, B, Y),
        'profiling_history_size': (Y, Y, Y, None, B, Y),
        'protocol_version': (None, None, Y, None, G, N),
        'proxy_user': (None, None, Y, None, S, N),
        'pseudo_slave_mode': (None, None, Y, None, S, Y),
        'pseudo_thread_id': (None, None, Y, None, S, Y),
        'Qcache_free_blocks': (None, None, None, Y, G, N),
        'Qcache_free_memory': (None, None, None, Y, G, N),
        'Qcache_hits': (None, None, None, Y, G, N),
        'Qcache_inserts': (None, None, None, Y, G, N),
        'Qcache_lowmem_prunes': (None, None, None, Y, G, N),
        'Qcache_not_cached': (None, None, None, Y, G, N),
        'Qcache_queries_in_cache': (None, None, None, Y, G, N),
        'Qcache_total_blocks': (None, None, None, Y, G, N),
        'Queries': (None, None, None, Y, B, N),
        'query_alloc_block_size': (Y, Y, Y, None, B, Y),
        'query_cache_limit': (Y, Y, Y, None, G, Y),
        'query_cache_min_res_unit': (Y, Y, Y, None, G, Y),
        'query_cache_size': (Y, Y, Y, None, G, Y),
        'query_cache_type': (Y, Y, Y, None, B, Y),
        'query_cache_wlock_invalidate': (Y, Y, Y, None, B, Y),
        'query_prealloc_size': (Y, Y, Y, None, B, Y),
        'Questions': (None, None, None, Y, B, N),
        'rand_seed1': (None, None, Y, None, S, Y),
        'rand_seed2': (None, None, Y, None, S, Y),
        'range_alloc_block_size': (Y, Y, Y, None, B, Y),
        'range_optimizer_max_mem_size': (Y, Y, Y, None, B, Y),
        'rbr_exec_mode': (None, None, Y, None, B, Y),
        'read_buffer_size': (Y, Y, Y, None, B, Y),
        'read_only': (Y, Y, Y, None, G, Y),
        'read_rnd_buffer_size': (Y, Y, Y, None, B, Y),
        'relay_log': (Y, Y, Y, None, G, N),
        'relay_log_basename': (None, None, Y, None, G, N),
        'relay_log_index': (Y, Y, Y, None, G, N),
        'relay_log_info_file': (Y, Y, Y, None, G, N),
        'relay_log_info_repository': (Y, Y, Y, None, G, Y),
        'relay_log_purge': (Y, Y, Y, None, G, Y),
        'relay_log_recovery': (Y, Y, Y, None, G, N),
        'relay_log_space_limit': (Y, Y, Y, None, G, N),
        'remove': (Y, None, None, None, None, None),
        'replicate-do-db': (Y, Y, None, None, None, None),
        'replicate-do-table': (Y, Y, None, None, None, None),
        'replicate-ignore-db': (Y, Y, None, None, None, None),
        'replicate-ignore-table': (Y, Y, None, None, None, None),
        'replicate-rewrite-db': (Y, Y, None, None, None, None),
        'replicate-same-server-id': (Y, Y, None, None, None, None),
        'replicate-wild-do-table': (Y, Y, None, None, None, None),
        'replicate-wild-ignore-table': (Y, Y, None, None, None, None),
        'report_host': (Y, Y, Y, None, G, N),
        'report_password': (Y, Y, Y, None, G, N),
        'report_port': (Y, Y, Y, None, G, N),
        'report_user': (Y, Y, Y, None, G, N),
        'require_secure_transport': (Y, Y, Y, None, G, Y),
        'rewriter_enabled': (None, None, Y, None, G, Y),
        'Rewriter_number_loaded_rules': (None, None, None, Y, G, N),
        'Rewriter_number_reloads': (None, None, None, Y, G, N),
        'Rewriter_number_rewritten_queries': (None, None, None, Y, G, N),
        'Rewriter_reload_error': (None, None, None, Y, G, N),
        'rewriter_verbose': (None, None, Y, None, G, Y),
        'Rpl_semi_sync_master_clients': (None, None, None, Y, G, N),
        'rpl_semi_sync_master_enabled': (Y, Y, Y, None, G, Y),
        'Rpl_semi_sync_master_net_avg_wait_time': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_net_wait_time': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_net_waits': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_no_times': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_no_tx': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_status': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_timefunc_failures': (None, None, None, Y, G, N),
        'rpl_semi_sync_master_timeout': (Y, Y, Y, None, G, Y),
        'rpl_semi_sync_master_trace_level': (Y, Y, Y, None, G, Y),
        'Rpl_semi_sync_master_tx_avg_wait_time': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_tx_wait_time': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_tx_waits': (None, None, None, Y, G, N),
        'rpl_semi_sync_master_wait_for_slave_count': (Y, Y, Y, None, G, Y),
        'rpl_semi_sync_master_wait_no_slave': (Y, Y, Y, None, G, Y),
        'rpl_semi_sync_master_wait_point': (Y, Y, Y, None, G, Y),
        'Rpl_semi_sync_master_wait_pos_backtraverse': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_wait_sessions': (None, None, None, Y, G, N),
        'Rpl_semi_sync_master_yes_tx': (None, None, None, Y, G, N),
        'rpl_semi_sync_slave_enabled': (Y, Y, Y, None, G, Y),
        'Rpl_semi_sync_slave_status': (None, None, None, Y, G, N),
        'rpl_semi_sync_slave_trace_level': (Y, Y, Y, None, G, Y),
        'rpl_stop_slave_timeout': (Y, Y, Y, None, G, Y),
        'Rsa_public_key': (None, None, None, Y, G, N),
        'safe-user-create': (Y, Y, None, None, None, None),
        'secure_auth': (Y, Y, Y, None, G, Y),
        'secure_file_priv': (Y, Y, Y, None, G, N),
        'Select_full_join': (None, None, None, Y, B, N),
        'Select_full_range_join': (None, None, None, Y, B, N),
        'Select_range': (None, None, None, Y, B, N),
        'Select_range_check': (None, None, None, Y, B, N),
        'Select_scan': (None, None, None, Y, B, N),
        'server_id': (Y, Y, Y, None, G, Y),
        'server_id_bits': (Y, Y, Y, None, G, N),
        'server_uuid': (None, None, Y, None, G, N),
        'session_track_gtids': (Y, Y, Y, None, B, Y),
        'session_track_schema': (Y, Y, Y, None, B, Y),
        'session_track_state_change': (Y, Y, Y, None, B, Y),
        'session_track_system_variables': (Y, Y, Y, None, B, Y),
        'session_track_transaction_info': (Y, Y, Y, None, B, Y),
        'sha256_password_auto_generate_rsa_keys': (Y, Y, Y, None, G, N),
        'sha256_password_private_key_path': (Y, Y, Y, None, G, N),
        'sha256_password_proxy_users': (Y, Y, Y, None, G, Y),
        'sha256_password_public_key_path': (Y, Y, Y, None, G, N),
        'shared_memory': (Y, Y, Y, None, G, N),
        'shared_memory_base_name': (Y, Y, Y, None, G, N),
        'show_compatibility_56': (Y, Y, Y, None, G, Y),
        'show_create_table_verbosity': (Y, Y, Y, None, B, Y),
        'show_old_temporals': (Y, Y, Y, None, B, Y),
        'show-slave-auth-info': (Y, Y, None, None, None, None),
        'skip-character-set-client-handshake': (Y, Y, None, None, None, None),
        'skip_external_locking': (Y, Y, Y, None, G, N),
        'skip-grant-tables': (Y, Y, None, None, None, None),
        'skip-host-cache': (Y, Y, None, None, None, None),
        'skip_name_resolve': (Y, Y, Y, None, G, N),
        'skip-ndbcluster': (Y, Y, None, None, None, None),
        'skip_networking': (Y, Y, Y, None, G, N),
        'skip-new': (Y, Y, None, None, None, None),
        'skip-partition': (Y, Y, None, None, None, None),
        'skip_show_database': (Y, Y, Y, None, G, N),
        'skip-slave-start': (Y, Y, None, None, None, None),
        'skip-ssl': (Y, Y, None, None, None, None),
        'skip-stack-trace': (Y, Y, None, None, None, None),
        'slave_allow_batching': (Y, Y, Y, None, G, Y),
        'slave_checkpoint_group': (Y, Y, Y, None, G, Y),
        'slave_checkpoint_period': (Y, Y, Y, None, G, Y),
        'slave_compressed_protocol': (Y, Y, Y, None, G, Y),
        'slave_exec_mode': (Y, Y, Y, None, G, Y),
        'Slave_heartbeat_period': (None, None, None, Y, G, N),
        'Slave_last_heartbeat': (None, None, None, Y, G, N),
        'slave_load_tmpdir': (Y, Y, Y, None, G, N),
        'slave_max_allowed_packet': (Y, Y, Y, None, G, Y),
        'slave_net_timeout': (Y, Y, Y, None, G, Y),
        'Slave_open_temp_tables': (None, None, None, Y, G, N),
        'slave_parallel_type': (Y, Y, Y, None, G, Y),
        'slave_parallel_workers': (Y, Y, Y, None, G, Y),
        'slave_pending_jobs_size_max': (Y, Y, Y, None, G, Y),
        'slave_preserve_commit_order': (Y, Y, Y, None, G, Y),
        'Slave_received_heartbeats': (None, None, None, Y, G, N),
        'Slave_retried_transactions': (None, None, None, Y, G, N),
        'Slave_rows_last_search_algorithm_used': (None, None, None, Y, G, N),
        'slave_rows_search_algorithms': (Y, Y, Y, None, G, Y),
        'Slave_running': (None, None, None, Y, G, N),
        'slave_skip_errors': (Y, Y, Y, None, G, N),
        'slave-sql-verify-checksum': (Y, Y, None, None, None, None),
        'slave_sql_verify_checksum': (Y, Y, Y, None, G, Y),
        'slave_transaction_retries': (Y, Y, Y, None, G, Y),
        'slave_type_conversions': (Y, Y, Y, None, G, N),
        'Slow_launch_threads': (None, None, None, Y, B, N),
        'slow_launch_time': (Y, Y, Y, None, G, Y),
        'Slow_queries': (None, None, None, Y, B, N),
        'slow_query_log': (Y, Y, Y, None, G, Y),
        'slow_query_log_file': (Y, Y, Y, None, G, Y),
        'slow-start-timeout': (Y, Y, None, None, None, None),
        'socket': (Y, Y, Y, None, G, N),
        'sort_buffer_size': (Y, Y, Y, None, B, Y),
        'Sort_merge_passes': (None, None, None, Y, B, N),
        'Sort_range': (None, None, None, Y, B, N),
        'Sort_rows': (None, None, None, Y, B, N),
        'Sort_scan': (None, None, None, Y, B, N),
        'sporadic-binlog-dump-fail': (Y, Y, None, None, None, None),
        'sql_auto_is_null': (None, None, Y, None, B, Y),
        'sql_big_selects': (None, None, Y, None, B, Y),
        'sql_buffer_result': (None, None, Y, None, B, Y),
        'sql_log_bin': (None, None, Y, None, S, Y),
        'sql_log_off': (None, None, Y, None, B, Y),
        'sql_mode': (Y, Y, Y, None, B, Y),
        'sql_notes': (None, None, Y, None, B, Y),
        'sql_quote_show_create': (None, None, Y, None, B, Y),
        'sql_safe_updates': (None, None, Y, None, B, Y),
        'sql_select_limit': (None, None, Y, None, B, Y),
        'sql_slave_skip_counter': (None, None, Y, None, G, Y),
        'sql_warnings': (None, None, Y, None, B, Y),
        'ssl': (Y, Y, None, None, None, None),
        'Ssl_accept_renegotiates': (None, None, None, Y, G, N),
        'Ssl_accepts': (None, None, None, Y, G, N),
        'ssl_ca': (Y, Y, Y, None, G, N),
        'Ssl_callback_cache_hits': (None, None, None, Y, G, N),
        'ssl_capath': (Y, Y, Y, None, G, N),
        'ssl_cert': (Y, Y, Y, None, G, N),
        'Ssl_cipher': (None, None, None, Y, B, N),
        'ssl_cipher': (Y, Y, Y, None, G, N),
        'Ssl_cipher_list': (None, None, None, Y, B, N),
        'Ssl_client_connects': (None, None, None, Y, G, N),
        'Ssl_connect_renegotiates': (None, None, None, Y, G, N),
        'ssl_crl': (Y, Y, Y, None, G, N),
        'ssl_crlpath': (Y, Y, Y, None, G, N),
        'Ssl_ctx_verify_depth': (None, None, None, Y, G, N),
        'Ssl_ctx_verify_mode': (None, None, None, Y, G, N),
        'Ssl_default_timeout': (None, None, None, Y, B, N),
        'Ssl_finished_accepts': (None, None, None, Y, G, N),
        'Ssl_finished_connects': (None, None, None, Y, G, N),
        'ssl_key': (Y, Y, Y, None, G, N),
        'Ssl_server_not_after': (None, None, None, Y, B, N),
        'Ssl_server_not_before': (None, None, None, Y, B, N),
        'Ssl_session_cache_hits': (None, None, None, Y, G, N),
        'Ssl_session_cache_misses': (None, None, None, Y, G, N),
        'Ssl_session_cache_mode': (None, None, None, Y, G, N),
        'Ssl_session_cache_overflows': (None, None, None, Y, G, N),
        'Ssl_session_cache_size': (None, None, None, Y, G, N),
        'Ssl_session_cache_timeouts': (None, None, None, Y, G, N),
        'Ssl_sessions_reused': (None, None, None, Y, B, N),
        'Ssl_used_session_cache_entries': (None, None, None, Y, G, N),
        'Ssl_verify_depth': (None, None, None, Y, B, N),
        'Ssl_verify_mode': (None, None, None, Y, B, N),
        'Ssl_version': (None, None, None, Y, B, N),
        'standalone': (Y, Y, None, None, None, None),
        'stored_program_cache': (Y, Y, Y, None, G, Y),
        'super-large-pages': (Y, Y, None, None, None, None),
        'super_read_only': (Y, Y, Y, None, G, Y),
        'symbolic-links': (Y, Y, None, None, None, None),
        'sync_binlog': (Y, Y, Y, None, G, Y),
        'sync_frm': (Y, Y, Y, None, G, Y),
        'sync_master_info': (Y, Y, Y, None, G, Y),
        'sync_relay_log': (Y, Y, Y, None, G, Y),
        'sync_relay_log_info': (Y, Y, Y, None, G, Y),
        'sysdate-is-now': (Y, Y, None, None, None, None),
        'system_time_zone': (None, None, Y, None, G, N),
        'table_definition_cache': (Y, Y, Y, None, G, Y),
        'Table_locks_immediate': (None, None, None, Y, G, N),
        'Table_locks_waited': (None, None, None, Y, G, N),
        'table_open_cache': (Y, Y, Y, None, G, Y),
        'Table_open_cache_hits': (None, None, None, Y, B, N),
        'table_open_cache_instances': (Y, Y, Y, None, G, N),
        'Table_open_cache_misses': (None, None, None, Y, B, N),
        'Table_open_cache_overflows': (None, None, None, Y, B, N),
        'tc-heuristic-recover': (Y, Y, None, None, None, None),
        'Tc_log_max_pages_used': (None, None, None, Y, G, N),
        'Tc_log_page_size': (None, None, None, Y, G, N),
        'Tc_log_page_waits': (None, None, None, Y, G, N),
        'temp-pool': (Y, Y, None, None, None, None),
        'thread_cache_size': (Y, Y, Y, None, G, Y),
        'thread_handling': (Y, Y, Y, None, G, N),
        'thread_pool_algorithm': (Y, Y, Y, None, G, N),
        'thread_pool_high_priority_connection': (Y, Y, Y, None, B, Y),
        'thread_pool_max_unused_threads': (Y, Y, Y, None, G, Y),
        'thread_pool_prio_kickup_timer': (Y, Y, Y, None, B, Y),
        'thread_pool_size': (Y, Y, Y, None, G, N),
        'thread_pool_stall_limit': (Y, Y, Y, None, G, Y),
        'thread_stack': (Y, Y, Y, None, G, N),
        'Threads_cached': (None, None, None, Y, G, N),
        'Threads_connected': (None, None, None, Y, G, N),
        'Threads_created': (None, None, None, Y, G, N),
        'Threads_running': (None, None, None, Y, G, N),
        'time_format': (None, None, Y, None, G, N),
        'time_zone': (None, None, Y, None, B, Y),
        'timestamp': (None, None, Y, None, S, Y),
        'tls_version': (Y, Y, Y, None, G, N),
        'tmp_table_size': (Y, Y, Y, None, B, Y),
        'tmpdir': (Y, Y, Y, None, G, N),
        'transaction_alloc_block_size': (Y, Y, Y, None, B, Y),
        'transaction_allow_batching': (None, None, Y, None, S, Y),
        'transaction_isolation': (Y, Y, None, None, B, Y),
        'transaction_prealloc_size': (Y, Y, Y, None, B, Y),
        'transaction_read_only': (Y, Y, None, None, B, Y),
        'transaction_write_set_extraction': (Y, Y, Y, None, B, Y),
        'tx_isolation': (None, None, Y, None, B, Y),
        'tx_read_only': (None, None, Y, None, B, Y),
        'unique_checks': (None, None, Y, None, B, Y),
        'updatable_views_with_limit': (Y, Y, Y, None, B, Y),
        'Uptime': (None, None, None, Y, G, N),
        'Uptime_since_flush_status': (None, None, None, Y, G, N),
        'user': (Y, Y, None, None, None, None),
        'validate-password': (Y, Y, None, None, None, None),
        'validate_password_check_user_name': (Y, Y, Y, None, G, Y),
        'validate_password_dictionary_file': (Y, Y, Y, None, G, V),
        'validate_password_dictionary_file_last_parsed': (None, None, None, Y, G, N),
        'validate_password_dictionary_file_words_count': (None, None, None, Y, G, N),
        'validate_password_length': (Y, Y, Y, None, G, Y),
        'validate_password_mixed_case_count': (Y, Y, Y, None, G, Y),
        'validate_password_number_count': (Y, Y, Y, None, G, Y),
        'validate_password_policy': (Y, Y, Y, None, G, Y),
        'validate_password_special_char_count': (Y, Y, Y, None, G, Y),
        'validate_user_plugins': (Y, Y, Y, None, G, N),
        'verbose': (Y, Y, None, None, None, None),
        'version': (None, None, Y, None, G, N),
        'version_comment': (None, None, Y, None, G, N),
        'version_compile_machine': (None, None, Y, None, G, N),
        'version_compile_os': (None, None, Y, None, G, N),
        'version_tokens_session': (Y, Y, Y, None, B, Y),
        'version_tokens_session_number': (Y, Y, Y, None, B, N),
        'wait_timeout': (Y, Y, Y, None, B, Y),
        'warning_count': (None, None, Y, None, S, N)

    }

    abort_slave_event_count = 'abort-slave-event-count'
    Aborted_clients = 'Aborted_clients'
    Aborted_connects = 'Aborted_connects'
    allow_suspicious_udfs = 'allow-suspicious-udfs'
    ansi = 'ansi'
    audit_log = 'audit-log'
    audit_log_buffer_size = 'audit_log_buffer_size'
    audit_log_compression = 'audit_log_compression'
    audit_log_connection_policy = 'audit_log_connection_policy'
    audit_log_current_session = 'audit_log_current_session'
    Audit_log_current_size = 'Audit_log_current_size'
    audit_log_encryption = 'audit_log_encryption'
    Audit_log_event_max_drop_size = 'Audit_log_event_max_drop_size'
    Audit_log_events = 'Audit_log_events'
    Audit_log_events_filtered = 'Audit_log_events_filtered'
    Audit_log_events_lost = 'Audit_log_events_lost'
    Audit_log_events_written = 'Audit_log_events_written'
    audit_log_exclude_accounts = 'audit_log_exclude_accounts'
    audit_log_file = 'audit_log_file'
    audit_log_filter_id = 'audit_log_filter_id'
    audit_log_flush = 'audit_log_flush'
    audit_log_format = 'audit_log_format'
    audit_log_include_accounts = 'audit_log_include_accounts'
    audit_log_policy = 'audit_log_policy'
    audit_log_read_buffer_size = 'audit_log_read_buffer_size'
    audit_log_rotate_on_size = 'audit_log_rotate_on_size'
    audit_log_statement_policy = 'audit_log_statement_policy'
    audit_log_strategy = 'audit_log_strategy'
    Audit_log_total_size = 'Audit_log_total_size'
    Audit_log_write_waits = 'Audit_log_write_waits'
    authentication_ldap_sasl_auth_method_name = 'authentication_ldap_sasl_auth_method_name'
    authentication_ldap_sasl_bind_base_dn = 'authentication_ldap_sasl_bind_base_dn'
    authentication_ldap_sasl_bind_root_dn = 'authentication_ldap_sasl_bind_root_dn'
    authentication_ldap_sasl_bind_root_pwd = 'authentication_ldap_sasl_bind_root_pwd'
    authentication_ldap_sasl_ca_path = 'authentication_ldap_sasl_ca_path'
    authentication_ldap_sasl_group_search_attr = 'authentication_ldap_sasl_group_search_attr'
    authentication_ldap_sasl_group_search_filter = 'authentication_ldap_sasl_group_search_filter'
    authentication_ldap_sasl_init_pool_size = 'authentication_ldap_sasl_init_pool_size'
    authentication_ldap_sasl_log_status = 'authentication_ldap_sasl_log_status'
    authentication_ldap_sasl_max_pool_size = 'authentication_ldap_sasl_max_pool_size'
    authentication_ldap_sasl_server_host = 'authentication_ldap_sasl_server_host'
    authentication_ldap_sasl_server_port = 'authentication_ldap_sasl_server_port'
    authentication_ldap_sasl_tls = 'authentication_ldap_sasl_tls'
    authentication_ldap_sasl_user_search_attr = 'authentication_ldap_sasl_user_search_attr'
    authentication_ldap_simple_auth_method_name = 'authentication_ldap_simple_auth_method_name'
    authentication_ldap_simple_bind_base_dn = 'authentication_ldap_simple_bind_base_dn'
    authentication_ldap_simple_bind_root_dn = 'authentication_ldap_simple_bind_root_dn'
    authentication_ldap_simple_bind_root_pwd = 'authentication_ldap_simple_bind_root_pwd'
    authentication_ldap_simple_ca_path = 'authentication_ldap_simple_ca_path'
    authentication_ldap_simple_group_search_attr = 'authentication_ldap_simple_group_search_attr'
    authentication_ldap_simple_group_search_filter = 'authentication_ldap_simple_group_search_filter'
    authentication_ldap_simple_init_pool_size = 'authentication_ldap_simple_init_pool_size'
    authentication_ldap_simple_log_status = 'authentication_ldap_simple_log_status'
    authentication_ldap_simple_max_pool_size = 'authentication_ldap_simple_max_pool_size'
    authentication_ldap_simple_server_host = 'authentication_ldap_simple_server_host'
    authentication_ldap_simple_server_port = 'authentication_ldap_simple_server_port'
    authentication_ldap_simple_tls = 'authentication_ldap_simple_tls'
    authentication_ldap_simple_user_search_attr = 'authentication_ldap_simple_user_search_attr'
    authentication_windows_log_level = 'authentication_windows_log_level'
    authentication_windows_use_principal_name = 'authentication_windows_use_principal_name'
    auto_generate_certs = 'auto_generate_certs'
    auto_increment_increment = 'auto_increment_increment'
    auto_increment_offset = 'auto_increment_offset'
    autocommit = 'autocommit'
    automatic_sp_privileges = 'automatic_sp_privileges'
    avoid_temporal_upgrade = 'avoid_temporal_upgrade'
    back_log = 'back_log'
    basedir = 'basedir'
    big_tables = 'big_tables'
    bind_address = 'bind_address'
    Binlog_cache_disk_use = 'Binlog_cache_disk_use'
    binlog_cache_size = 'binlog_cache_size'
    Binlog_cache_use = 'Binlog_cache_use'
    binlog_checksum = 'binlog-checksum'
    binlog_checksum = 'binlog_checksum'
    binlog_direct_non_transactional_updates = 'binlog_direct_non_transactional_updates'
    binlog_do_db = 'binlog-do-db'
    binlog_error_action = 'binlog_error_action'
    binlog_format = 'binlog_format'
    binlog_group_commit_sync_delay = 'binlog_group_commit_sync_delay'
    binlog_group_commit_sync_no_delay_count = 'binlog_group_commit_sync_no_delay_count'
    binlog_gtid_simple_recovery = 'binlog_gtid_simple_recovery'
    binlog_ignore_db = 'binlog-ignore-db'
    binlog_max_flush_queue_time = 'binlog_max_flush_queue_time'
    binlog_order_commits = 'binlog_order_commits'
    binlog_row_event_max_size = 'binlog-row-event-max-size'
    binlog_row_image = 'binlog_row_image'
    binlog_rows_query_log_events = 'binlog_rows_query_log_events'
    Binlog_stmt_cache_disk_use = 'Binlog_stmt_cache_disk_use'
    binlog_stmt_cache_size = 'binlog_stmt_cache_size'
    Binlog_stmt_cache_use = 'Binlog_stmt_cache_use'
    binlog_transaction_dependency_history_size = 'binlog_transaction_dependency_history_size'
    binlog_transaction_dependency_tracking = 'binlog_transaction_dependency_tracking'
    block_encryption_mode = 'block_encryption_mode'
    bootstrap = 'bootstrap'
    bulk_insert_buffer_size = 'bulk_insert_buffer_size'
    Bytes_received = 'Bytes_received'
    Bytes_sent = 'Bytes_sent'
    character_set_client = 'character_set_client'
    character_set_client_handshake = 'character-set-client-handshake'
    character_set_connection = 'character_set_connection'
    character_set_database = 'character_set_database'
    character_set_filesystem = 'character_set_filesystem'
    character_set_results = 'character_set_results'
    character_set_server = 'character_set_server'
    character_set_system = 'character_set_system'
    character_sets_dir = 'character_sets_dir'
    check_proxy_users = 'check_proxy_users'
    chroot = 'chroot'
    collation_connection = 'collation_connection'
    collation_database = 'collation_database'
    collation_server = 'collation_server'
    Com_admin_commands = 'Com_admin_commands'
    Com_alter_db = 'Com_alter_db'
    Com_alter_db_upgrade = 'Com_alter_db_upgrade'
    Com_alter_event = 'Com_alter_event'
    Com_alter_function = 'Com_alter_function'
    Com_alter_procedure = 'Com_alter_procedure'
    Com_alter_server = 'Com_alter_server'
    Com_alter_table = 'Com_alter_table'
    Com_alter_tablespace = 'Com_alter_tablespace'
    Com_alter_user = 'Com_alter_user'
    Com_analyze = 'Com_analyze'
    Com_assign_to_keycache = 'Com_assign_to_keycache'
    Com_begin = 'Com_begin'
    Com_binlog = 'Com_binlog'
    Com_call_procedure = 'Com_call_procedure'
    Com_change_db = 'Com_change_db'
    Com_change_master = 'Com_change_master'
    Com_change_repl_filter = 'Com_change_repl_filter'
    Com_check = 'Com_check'
    Com_checksum = 'Com_checksum'
    Com_commit = 'Com_commit'
    Com_create_db = 'Com_create_db'
    Com_create_event = 'Com_create_event'
    Com_create_function = 'Com_create_function'
    Com_create_index = 'Com_create_index'
    Com_create_procedure = 'Com_create_procedure'
    Com_create_server = 'Com_create_server'
    Com_create_table = 'Com_create_table'
    Com_create_trigger = 'Com_create_trigger'
    Com_create_udf = 'Com_create_udf'
    Com_create_user = 'Com_create_user'
    Com_create_view = 'Com_create_view'
    Com_dealloc_sql = 'Com_dealloc_sql'
    Com_delete = 'Com_delete'
    Com_delete_multi = 'Com_delete_multi'
    Com_do = 'Com_do'
    Com_drop_db = 'Com_drop_db'
    Com_drop_event = 'Com_drop_event'
    Com_drop_function = 'Com_drop_function'
    Com_drop_index = 'Com_drop_index'
    Com_drop_procedure = 'Com_drop_procedure'
    Com_drop_server = 'Com_drop_server'
    Com_drop_table = 'Com_drop_table'
    Com_drop_trigger = 'Com_drop_trigger'
    Com_drop_user = 'Com_drop_user'
    Com_drop_view = 'Com_drop_view'
    Com_empty_query = 'Com_empty_query'
    Com_execute_sql = 'Com_execute_sql'
    Com_explain_other = 'Com_explain_other'
    Com_flush = 'Com_flush'
    Com_get_diagnostics = 'Com_get_diagnostics'
    Com_grant = 'Com_grant'
    Com_group_replication_start = 'Com_group_replication_start'
    Com_group_replication_stop = 'Com_group_replication_stop'
    Com_ha_close = 'Com_ha_close'
    Com_ha_open = 'Com_ha_open'
    Com_ha_read = 'Com_ha_read'
    Com_help = 'Com_help'
    Com_insert = 'Com_insert'
    Com_insert_select = 'Com_insert_select'
    Com_install_plugin = 'Com_install_plugin'
    Com_kill = 'Com_kill'
    Com_load = 'Com_load'
    Com_lock_tables = 'Com_lock_tables'
    Com_optimize = 'Com_optimize'
    Com_preload_keys = 'Com_preload_keys'
    Com_prepare_sql = 'Com_prepare_sql'
    Com_purge = 'Com_purge'
    Com_purge_before_date = 'Com_purge_before_date'
    Com_release_savepoint = 'Com_release_savepoint'
    Com_rename_table = 'Com_rename_table'
    Com_rename_user = 'Com_rename_user'
    Com_repair = 'Com_repair'
    Com_replace = 'Com_replace'
    Com_replace_select = 'Com_replace_select'
    Com_reset = 'Com_reset'
    Com_resignal = 'Com_resignal'
    Com_revoke = 'Com_revoke'
    Com_revoke_all = 'Com_revoke_all'
    Com_rollback = 'Com_rollback'
    Com_rollback_to_savepoint = 'Com_rollback_to_savepoint'
    Com_savepoint = 'Com_savepoint'
    Com_select = 'Com_select'
    Com_set_option = 'Com_set_option'
    Com_show_authors = 'Com_show_authors'
    Com_show_binlog_events = 'Com_show_binlog_events'
    Com_show_binlogs = 'Com_show_binlogs'
    Com_show_charsets = 'Com_show_charsets'
    Com_show_collations = 'Com_show_collations'
    Com_show_contributors = 'Com_show_contributors'
    Com_show_create_db = 'Com_show_create_db'
    Com_show_create_event = 'Com_show_create_event'
    Com_show_create_func = 'Com_show_create_func'
    Com_show_create_proc = 'Com_show_create_proc'
    Com_show_create_table = 'Com_show_create_table'
    Com_show_create_trigger = 'Com_show_create_trigger'
    Com_show_create_user = 'Com_show_create_user'
    Com_show_databases = 'Com_show_databases'
    Com_show_engine_logs = 'Com_show_engine_logs'
    Com_show_engine_mutex = 'Com_show_engine_mutex'
    Com_show_engine_status = 'Com_show_engine_status'
    Com_show_errors = 'Com_show_errors'
    Com_show_events = 'Com_show_events'
    Com_show_fields = 'Com_show_fields'
    Com_show_function_code = 'Com_show_function_code'
    Com_show_function_status = 'Com_show_function_status'
    Com_show_grants = 'Com_show_grants'
    Com_show_keys = 'Com_show_keys'
    Com_show_master_status = 'Com_show_master_status'
    Com_show_ndb_status = 'Com_show_ndb_status'
    Com_show_open_tables = 'Com_show_open_tables'
    Com_show_plugins = 'Com_show_plugins'
    Com_show_privileges = 'Com_show_privileges'
    Com_show_procedure_code = 'Com_show_procedure_code'
    Com_show_procedure_status = 'Com_show_procedure_status'
    Com_show_processlist = 'Com_show_processlist'
    Com_show_profile = 'Com_show_profile'
    Com_show_profiles = 'Com_show_profiles'
    Com_show_relaylog_events = 'Com_show_relaylog_events'
    Com_show_slave_hosts = 'Com_show_slave_hosts'
    Com_show_slave_status = 'Com_show_slave_status'
    Com_show_status = 'Com_show_status'
    Com_show_storage_engines = 'Com_show_storage_engines'
    Com_show_table_status = 'Com_show_table_status'
    Com_show_tables = 'Com_show_tables'
    Com_show_triggers = 'Com_show_triggers'
    Com_show_variables = 'Com_show_variables'
    Com_show_warnings = 'Com_show_warnings'
    Com_shutdown = 'Com_shutdown'
    Com_signal = 'Com_signal'
    Com_slave_start = 'Com_slave_start'
    Com_slave_stop = 'Com_slave_stop'
    Com_stmt_close = 'Com_stmt_close'
    Com_stmt_execute = 'Com_stmt_execute'
    Com_stmt_fetch = 'Com_stmt_fetch'
    Com_stmt_prepare = 'Com_stmt_prepare'
    Com_stmt_reprepare = 'Com_stmt_reprepare'
    Com_stmt_reset = 'Com_stmt_reset'
    Com_stmt_send_long_data = 'Com_stmt_send_long_data'
    Com_truncate = 'Com_truncate'
    Com_uninstall_plugin = 'Com_uninstall_plugin'
    Com_unlock_tables = 'Com_unlock_tables'
    Com_update = 'Com_update'
    Com_update_multi = 'Com_update_multi'
    Com_xa_commit = 'Com_xa_commit'
    Com_xa_end = 'Com_xa_end'
    Com_xa_prepare = 'Com_xa_prepare'
    Com_xa_recover = 'Com_xa_recover'
    Com_xa_rollback = 'Com_xa_rollback'
    Com_xa_start = 'Com_xa_start'
    completion_type = 'completion_type'
    Compression = 'Compression'
    concurrent_insert = 'concurrent_insert'
    connect_timeout = 'connect_timeout'
    Connection_control_delay_generated = 'Connection_control_delay_generated'
    connection_control_failed_connections_threshold = 'connection_control_failed_connections_threshold'
    connection_control_max_connection_delay = 'connection_control_max_connection_delay'
    connection_control_min_connection_delay = 'connection_control_min_connection_delay'
    Connection_errors_accept = 'Connection_errors_accept'
    Connection_errors_internal = 'Connection_errors_internal'
    Connection_errors_max_connections = 'Connection_errors_max_connections'
    Connection_errors_peer_address = 'Connection_errors_peer_address'
    Connection_errors_select = 'Connection_errors_select'
    Connection_errors_tcpwrap = 'Connection_errors_tcpwrap'
    Connections = 'Connections'
    console = 'console'
    core_file = 'core-file'
    core_file = 'core_file'
    Created_tmp_disk_tables = 'Created_tmp_disk_tables'
    Created_tmp_files = 'Created_tmp_files'
    Created_tmp_tables = 'Created_tmp_tables'
    daemon_memcached_enable_binlog = 'daemon_memcached_enable_binlog'
    daemon_memcached_engine_lib_name = 'daemon_memcached_engine_lib_name'
    daemon_memcached_engine_lib_path = 'daemon_memcached_engine_lib_path'
    daemon_memcached_option = 'daemon_memcached_option'
    daemon_memcached_r_batch_size = 'daemon_memcached_r_batch_size'
    daemon_memcached_w_batch_size = 'daemon_memcached_w_batch_size'
    daemonize = 'daemonize'
    datadir = 'datadir'
    date_format = 'date_format'
    datetime_format = 'datetime_format'
    debug = 'debug'
    debug_sync = 'debug_sync'
    debug_sync_timeout = 'debug-sync-timeout'
    default_authentication_plugin = 'default_authentication_plugin'
    default_password_lifetime = 'default_password_lifetime'
    default_storage_engine = 'default_storage_engine'
    default_time_zone = 'default-time-zone'
    default_tmp_storage_engine = 'default_tmp_storage_engine'
    default_week_format = 'default_week_format'
    defaults_extra_file = 'defaults-extra-file'
    defaults_file = 'defaults-file'
    defaults_group_suffix = 'defaults-group-suffix'
    delay_key_write = 'delay_key_write'
    Delayed_errors = 'Delayed_errors'
    delayed_insert_limit = 'delayed_insert_limit'
    Delayed_insert_threads = 'Delayed_insert_threads'
    delayed_insert_timeout = 'delayed_insert_timeout'
    delayed_queue_size = 'delayed_queue_size'
    Delayed_writes = 'Delayed_writes'
    des_key_file = 'des-key-file'
    disable_partition_engine_check = 'disable-partition-engine-check'
    disabled_storage_engines = 'disabled_storage_engines'
    disconnect_on_expired_password = 'disconnect_on_expired_password'
    disconnect_slave_event_count = 'disconnect-slave-event-count'
    div_precision_increment = 'div_precision_increment'
    early_plugin_load = 'early-plugin-load'
    end_markers_in_json = 'end_markers_in_json'
    enforce_gtid_consistency = 'enforce_gtid_consistency'
    eq_range_index_dive_limit = 'eq_range_index_dive_limit'
    error_count = 'error_count'
    event_scheduler = 'event_scheduler'
    exit_info = 'exit-info'
    expire_logs_days = 'expire_logs_days'
    explicit_defaults_for_timestamp = 'explicit_defaults_for_timestamp'
    external_locking = 'external-locking'
    external_user = 'external_user'
    federated = 'federated'
    Firewall_access_denied = 'Firewall_access_denied'
    Firewall_access_granted = 'Firewall_access_granted'
    Firewall_cached_entries = 'Firewall_cached_entries'
    flush = 'flush'
    Flush_commands = 'Flush_commands'
    flush_time = 'flush_time'
    foreign_key_checks = 'foreign_key_checks'
    ft_boolean_syntax = 'ft_boolean_syntax'
    ft_max_word_len = 'ft_max_word_len'
    ft_min_word_len = 'ft_min_word_len'
    ft_query_expansion_limit = 'ft_query_expansion_limit'
    ft_stopword_file = 'ft_stopword_file'
    gdb = 'gdb'
    general_log = 'general_log'
    general_log_file = 'general_log_file'
    group_concat_max_len = 'group_concat_max_len'
    group_replication_allow_local_disjoint_gtids_join = 'group_replication_allow_local_disjoint_gtids_join'
    group_replication_allow_local_lower_version_join = 'group_replication_allow_local_lower_version_join'
    group_replication_auto_increment_increment = 'group_replication_auto_increment_increment'
    group_replication_bootstrap_group = 'group_replication_bootstrap_group'
    group_replication_components_stop_timeout = 'group_replication_components_stop_timeout'
    group_replication_compression_threshold = 'group_replication_compression_threshold'
    group_replication_enforce_update_everywhere_checks = 'group_replication_enforce_update_everywhere_checks'
    group_replication_exit_state_action = 'group_replication_exit_state_action'
    group_replication_flow_control_applier_threshold = 'group_replication_flow_control_applier_threshold'
    group_replication_flow_control_certifier_threshold = 'group_replication_flow_control_certifier_threshold'
    group_replication_flow_control_mode = 'group_replication_flow_control_mode'
    group_replication_force_members = 'group_replication_force_members'
    group_replication_group_name = 'group_replication_group_name'
    group_replication_group_seeds = 'group_replication_group_seeds'
    group_replication_gtid_assignment_block_size = 'group_replication_gtid_assignment_block_size'
    group_replication_ip_whitelist = 'group_replication_ip_whitelist'
    group_replication_local_address = 'group_replication_local_address'
    group_replication_member_weight = 'group_replication_member_weight'
    group_replication_poll_spin_loops = 'group_replication_poll_spin_loops'
    group_replication_primary_member = 'group_replication_primary_member'
    group_replication_recovery_complete_at = 'group_replication_recovery_complete_at'
    group_replication_recovery_reconnect_interval = 'group_replication_recovery_reconnect_interval'
    group_replication_recovery_retry_count = 'group_replication_recovery_retry_count'
    group_replication_recovery_ssl_ca = 'group_replication_recovery_ssl_ca'
    group_replication_recovery_ssl_capath = 'group_replication_recovery_ssl_capath'
    group_replication_recovery_ssl_cert = 'group_replication_recovery_ssl_cert'
    group_replication_recovery_ssl_cipher = 'group_replication_recovery_ssl_cipher'
    group_replication_recovery_ssl_crl = 'group_replication_recovery_ssl_crl'
    group_replication_recovery_ssl_crlpath = 'group_replication_recovery_ssl_crlpath'
    group_replication_recovery_ssl_key = 'group_replication_recovery_ssl_key'
    group_replication_recovery_ssl_verify_server_cert = 'group_replication_recovery_ssl_verify_server_cert'
    group_replication_recovery_use_ssl = 'group_replication_recovery_use_ssl'
    group_replication_single_primary_mode = 'group_replication_single_primary_mode'
    group_replication_ssl_mode = 'group_replication_ssl_mode'
    group_replication_start_on_boot = 'group_replication_start_on_boot'
    group_replication_transaction_size_limit = 'group_replication_transaction_size_limit'
    group_replication_unreachable_majority_timeout = 'group_replication_unreachable_majority_timeout'
    gtid_executed = 'gtid_executed'
    gtid_executed_compression_period = 'gtid_executed_compression_period'
    gtid_mode = 'gtid_mode'
    gtid_next = 'gtid_next'
    gtid_owned = 'gtid_owned'
    gtid_purged = 'gtid_purged'
    Handler_commit = 'Handler_commit'
    Handler_delete = 'Handler_delete'
    Handler_discover = 'Handler_discover'
    Handler_external_lock = 'Handler_external_lock'
    Handler_mrr_init = 'Handler_mrr_init'
    Handler_prepare = 'Handler_prepare'
    Handler_read_first = 'Handler_read_first'
    Handler_read_key = 'Handler_read_key'
    Handler_read_last = 'Handler_read_last'
    Handler_read_next = 'Handler_read_next'
    Handler_read_prev = 'Handler_read_prev'
    Handler_read_rnd = 'Handler_read_rnd'
    Handler_read_rnd_next = 'Handler_read_rnd_next'
    Handler_rollback = 'Handler_rollback'
    Handler_savepoint = 'Handler_savepoint'
    Handler_savepoint_rollback = 'Handler_savepoint_rollback'
    Handler_update = 'Handler_update'
    Handler_write = 'Handler_write'
    have_compress = 'have_compress'
    have_crypt = 'have_crypt'
    have_dynamic_loading = 'have_dynamic_loading'
    have_geometry = 'have_geometry'
    have_openssl = 'have_openssl'
    have_profiling = 'have_profiling'
    have_query_cache = 'have_query_cache'
    have_rtree_keys = 'have_rtree_keys'
    have_ssl = 'have_ssl'
    have_statement_timeout = 'have_statement_timeout'
    have_symlink = 'have_symlink'
    help = 'help'
    host_cache_size = 'host_cache_size'
    hostname = 'hostname'
    identity = 'identity'
    ignore_builtin_innodb = 'ignore_builtin_innodb'
    ignore_db_dir = 'ignore-db-dir'
    ignore_db_dirs = 'ignore_db_dirs'
    init_connect = 'init_connect'
    init_file = 'init_file'
    init_slave = 'init_slave'
    initialize = 'initialize'
    initialize_insecure = 'initialize-insecure'
    innodb = 'innodb'
    innodb_adaptive_flushing = 'innodb_adaptive_flushing'
    innodb_adaptive_flushing_lwm = 'innodb_adaptive_flushing_lwm'
    innodb_adaptive_hash_index = 'innodb_adaptive_hash_index'
    innodb_adaptive_hash_index_parts = 'innodb_adaptive_hash_index_parts'
    innodb_adaptive_max_sleep_delay = 'innodb_adaptive_max_sleep_delay'
    innodb_api_bk_commit_interval = 'innodb_api_bk_commit_interval'
    innodb_api_disable_rowlock = 'innodb_api_disable_rowlock'
    innodb_api_enable_binlog = 'innodb_api_enable_binlog'
    innodb_api_enable_mdl = 'innodb_api_enable_mdl'
    innodb_api_trx_level = 'innodb_api_trx_level'
    innodb_autoextend_increment = 'innodb_autoextend_increment'
    innodb_autoinc_lock_mode = 'innodb_autoinc_lock_mode'
    Innodb_available_undo_logs = 'Innodb_available_undo_logs'
    innodb_background_drop_list_empty = 'innodb_background_drop_list_empty'
    Innodb_buffer_pool_bytes_data = 'Innodb_buffer_pool_bytes_data'
    Innodb_buffer_pool_bytes_dirty = 'Innodb_buffer_pool_bytes_dirty'
    innodb_buffer_pool_chunk_size = 'innodb_buffer_pool_chunk_size'
    innodb_buffer_pool_dump_at_shutdown = 'innodb_buffer_pool_dump_at_shutdown'
    innodb_buffer_pool_dump_now = 'innodb_buffer_pool_dump_now'
    innodb_buffer_pool_dump_pct = 'innodb_buffer_pool_dump_pct'
    Innodb_buffer_pool_dump_status = 'Innodb_buffer_pool_dump_status'
    innodb_buffer_pool_filename = 'innodb_buffer_pool_filename'
    innodb_buffer_pool_instances = 'innodb_buffer_pool_instances'
    innodb_buffer_pool_load_abort = 'innodb_buffer_pool_load_abort'
    innodb_buffer_pool_load_at_startup = 'innodb_buffer_pool_load_at_startup'
    innodb_buffer_pool_load_now = 'innodb_buffer_pool_load_now'
    Innodb_buffer_pool_load_status = 'Innodb_buffer_pool_load_status'
    Innodb_buffer_pool_pages_data = 'Innodb_buffer_pool_pages_data'
    Innodb_buffer_pool_pages_dirty = 'Innodb_buffer_pool_pages_dirty'
    Innodb_buffer_pool_pages_flushed = 'Innodb_buffer_pool_pages_flushed'
    Innodb_buffer_pool_pages_free = 'Innodb_buffer_pool_pages_free'
    Innodb_buffer_pool_pages_latched = 'Innodb_buffer_pool_pages_latched'
    Innodb_buffer_pool_pages_misc = 'Innodb_buffer_pool_pages_misc'
    Innodb_buffer_pool_pages_total = 'Innodb_buffer_pool_pages_total'
    Innodb_buffer_pool_read_ahead = 'Innodb_buffer_pool_read_ahead'
    Innodb_buffer_pool_read_ahead_evicted = 'Innodb_buffer_pool_read_ahead_evicted'
    Innodb_buffer_pool_read_ahead_rnd = 'Innodb_buffer_pool_read_ahead_rnd'
    Innodb_buffer_pool_read_requests = 'Innodb_buffer_pool_read_requests'
    Innodb_buffer_pool_reads = 'Innodb_buffer_pool_reads'
    Innodb_buffer_pool_resize_status = 'Innodb_buffer_pool_resize_status'
    innodb_buffer_pool_size = 'innodb_buffer_pool_size'
    Innodb_buffer_pool_wait_free = 'Innodb_buffer_pool_wait_free'
    Innodb_buffer_pool_write_requests = 'Innodb_buffer_pool_write_requests'
    innodb_change_buffer_max_size = 'innodb_change_buffer_max_size'
    innodb_change_buffering = 'innodb_change_buffering'
    innodb_change_buffering_debug = 'innodb_change_buffering_debug'
    innodb_checksum_algorithm = 'innodb_checksum_algorithm'
    innodb_checksums = 'innodb_checksums'
    innodb_cmp_per_index_enabled = 'innodb_cmp_per_index_enabled'
    innodb_commit_concurrency = 'innodb_commit_concurrency'
    innodb_compress_debug = 'innodb_compress_debug'
    innodb_compression_failure_threshold_pct = 'innodb_compression_failure_threshold_pct'
    innodb_compression_level = 'innodb_compression_level'
    innodb_compression_pad_pct_max = 'innodb_compression_pad_pct_max'
    innodb_concurrency_tickets = 'innodb_concurrency_tickets'
    innodb_data_file_path = 'innodb_data_file_path'
    Innodb_data_fsyncs = 'Innodb_data_fsyncs'
    innodb_data_home_dir = 'innodb_data_home_dir'
    Innodb_data_pending_fsyncs = 'Innodb_data_pending_fsyncs'
    Innodb_data_pending_reads = 'Innodb_data_pending_reads'
    Innodb_data_pending_writes = 'Innodb_data_pending_writes'
    Innodb_data_read = 'Innodb_data_read'
    Innodb_data_reads = 'Innodb_data_reads'
    Innodb_data_writes = 'Innodb_data_writes'
    Innodb_data_written = 'Innodb_data_written'
    Innodb_dblwr_pages_written = 'Innodb_dblwr_pages_written'
    Innodb_dblwr_writes = 'Innodb_dblwr_writes'
    innodb_deadlock_detect = 'innodb_deadlock_detect'
    innodb_default_row_format = 'innodb_default_row_format'
    innodb_disable_resize_buffer_pool_debug = 'innodb_disable_resize_buffer_pool_debug'
    innodb_disable_sort_file_cache = 'innodb_disable_sort_file_cache'
    innodb_doublewrite = 'innodb_doublewrite'
    innodb_fast_shutdown = 'innodb_fast_shutdown'
    innodb_fil_make_page_dirty_debug = 'innodb_fil_make_page_dirty_debug'
    innodb_file_format = 'innodb_file_format'
    innodb_file_format_check = 'innodb_file_format_check'
    innodb_file_format_max = 'innodb_file_format_max'
    innodb_file_per_table = 'innodb_file_per_table'
    innodb_fill_factor = 'innodb_fill_factor'
    innodb_flush_log_at_timeout = 'innodb_flush_log_at_timeout'
    innodb_flush_log_at_trx_commit = 'innodb_flush_log_at_trx_commit'
    innodb_flush_method = 'innodb_flush_method'
    innodb_flush_neighbors = 'innodb_flush_neighbors'
    innodb_flush_sync = 'innodb_flush_sync'
    innodb_flushing_avg_loops = 'innodb_flushing_avg_loops'
    innodb_force_load_corrupted = 'innodb_force_load_corrupted'
    innodb_force_recovery = 'innodb_force_recovery'
    innodb_ft_aux_table = 'innodb_ft_aux_table'
    innodb_ft_cache_size = 'innodb_ft_cache_size'
    innodb_ft_enable_diag_print = 'innodb_ft_enable_diag_print'
    innodb_ft_enable_stopword = 'innodb_ft_enable_stopword'
    innodb_ft_max_token_size = 'innodb_ft_max_token_size'
    innodb_ft_min_token_size = 'innodb_ft_min_token_size'
    innodb_ft_num_word_optimize = 'innodb_ft_num_word_optimize'
    innodb_ft_result_cache_limit = 'innodb_ft_result_cache_limit'
    innodb_ft_server_stopword_table = 'innodb_ft_server_stopword_table'
    innodb_ft_sort_pll_degree = 'innodb_ft_sort_pll_degree'
    innodb_ft_total_cache_size = 'innodb_ft_total_cache_size'
    innodb_ft_user_stopword_table = 'innodb_ft_user_stopword_table'
    Innodb_have_atomic_builtins = 'Innodb_have_atomic_builtins'
    innodb_io_capacity = 'innodb_io_capacity'
    innodb_io_capacity_max = 'innodb_io_capacity_max'
    innodb_large_prefix = 'innodb_large_prefix'
    innodb_limit_optimistic_insert_debug = 'innodb_limit_optimistic_insert_debug'
    innodb_lock_wait_timeout = 'innodb_lock_wait_timeout'
    innodb_locks_unsafe_for_binlog = 'innodb_locks_unsafe_for_binlog'
    innodb_log_buffer_size = 'innodb_log_buffer_size'
    innodb_log_checkpoint_now = 'innodb_log_checkpoint_now'
    innodb_log_checksums = 'innodb_log_checksums'
    innodb_log_compressed_pages = 'innodb_log_compressed_pages'
    innodb_log_file_size = 'innodb_log_file_size'
    innodb_log_files_in_group = 'innodb_log_files_in_group'
    innodb_log_group_home_dir = 'innodb_log_group_home_dir'
    Innodb_log_waits = 'Innodb_log_waits'
    innodb_log_write_ahead_size = 'innodb_log_write_ahead_size'
    Innodb_log_write_requests = 'Innodb_log_write_requests'
    Innodb_log_writes = 'Innodb_log_writes'
    innodb_lru_scan_depth = 'innodb_lru_scan_depth'
    innodb_max_dirty_pages_pct = 'innodb_max_dirty_pages_pct'
    innodb_max_dirty_pages_pct_lwm = 'innodb_max_dirty_pages_pct_lwm'
    innodb_max_purge_lag = 'innodb_max_purge_lag'
    innodb_max_purge_lag_delay = 'innodb_max_purge_lag_delay'
    innodb_max_undo_log_size = 'innodb_max_undo_log_size'
    innodb_merge_threshold_set_all_debug = 'innodb_merge_threshold_set_all_debug'
    innodb_monitor_disable = 'innodb_monitor_disable'
    innodb_monitor_enable = 'innodb_monitor_enable'
    innodb_monitor_reset = 'innodb_monitor_reset'
    innodb_monitor_reset_all = 'innodb_monitor_reset_all'
    Innodb_num_open_files = 'Innodb_num_open_files'
    innodb_numa_interleave = 'innodb_numa_interleave'
    innodb_old_blocks_pct = 'innodb_old_blocks_pct'
    innodb_old_blocks_time = 'innodb_old_blocks_time'
    innodb_online_alter_log_max_size = 'innodb_online_alter_log_max_size'
    innodb_open_files = 'innodb_open_files'
    innodb_optimize_fulltext_only = 'innodb_optimize_fulltext_only'
    Innodb_os_log_fsyncs = 'Innodb_os_log_fsyncs'
    Innodb_os_log_pending_fsyncs = 'Innodb_os_log_pending_fsyncs'
    Innodb_os_log_pending_writes = 'Innodb_os_log_pending_writes'
    Innodb_os_log_written = 'Innodb_os_log_written'
    innodb_page_cleaners = 'innodb_page_cleaners'
    Innodb_page_size = 'Innodb_page_size'
    innodb_page_size = 'innodb_page_size'
    Innodb_pages_created = 'Innodb_pages_created'
    Innodb_pages_read = 'Innodb_pages_read'
    Innodb_pages_written = 'Innodb_pages_written'
    innodb_print_all_deadlocks = 'innodb_print_all_deadlocks'
    innodb_purge_batch_size = 'innodb_purge_batch_size'
    innodb_purge_rseg_truncate_frequency = 'innodb_purge_rseg_truncate_frequency'
    innodb_purge_threads = 'innodb_purge_threads'
    innodb_random_read_ahead = 'innodb_random_read_ahead'
    innodb_read_ahead_threshold = 'innodb_read_ahead_threshold'
    innodb_read_io_threads = 'innodb_read_io_threads'
    innodb_read_only = 'innodb_read_only'
    innodb_replication_delay = 'innodb_replication_delay'
    innodb_rollback_on_timeout = 'innodb_rollback_on_timeout'
    innodb_rollback_segments = 'innodb_rollback_segments'
    Innodb_row_lock_current_waits = 'Innodb_row_lock_current_waits'
    Innodb_row_lock_time = 'Innodb_row_lock_time'
    Innodb_row_lock_time_avg = 'Innodb_row_lock_time_avg'
    Innodb_row_lock_time_max = 'Innodb_row_lock_time_max'
    Innodb_row_lock_waits = 'Innodb_row_lock_waits'
    Innodb_rows_deleted = 'Innodb_rows_deleted'
    Innodb_rows_inserted = 'Innodb_rows_inserted'
    Innodb_rows_read = 'Innodb_rows_read'
    Innodb_rows_updated = 'Innodb_rows_updated'
    innodb_saved_page_number_debug = 'innodb_saved_page_number_debug'
    innodb_sort_buffer_size = 'innodb_sort_buffer_size'
    innodb_spin_wait_delay = 'innodb_spin_wait_delay'
    innodb_stats_auto_recalc = 'innodb_stats_auto_recalc'
    innodb_stats_include_delete_marked = 'innodb_stats_include_delete_marked'
    innodb_stats_method = 'innodb_stats_method'
    innodb_stats_on_metadata = 'innodb_stats_on_metadata'
    innodb_stats_persistent = 'innodb_stats_persistent'
    innodb_stats_persistent_sample_pages = 'innodb_stats_persistent_sample_pages'
    innodb_stats_sample_pages = 'innodb_stats_sample_pages'
    innodb_stats_transient_sample_pages = 'innodb_stats_transient_sample_pages'
    innodb_status_file = 'innodb-status-file'
    innodb_status_output = 'innodb_status_output'
    innodb_status_output_locks = 'innodb_status_output_locks'
    innodb_strict_mode = 'innodb_strict_mode'
    innodb_support_xa = 'innodb_support_xa'
    innodb_sync_array_size = 'innodb_sync_array_size'
    innodb_sync_debug = 'innodb_sync_debug'
    innodb_sync_spin_loops = 'innodb_sync_spin_loops'
    innodb_table_locks = 'innodb_table_locks'
    innodb_temp_data_file_path = 'innodb_temp_data_file_path'
    innodb_thread_concurrency = 'innodb_thread_concurrency'
    innodb_thread_sleep_delay = 'innodb_thread_sleep_delay'
    innodb_tmpdir = 'innodb_tmpdir'
    Innodb_truncated_status_writes = 'Innodb_truncated_status_writes'
    innodb_trx_purge_view_update_only_debug = 'innodb_trx_purge_view_update_only_debug'
    innodb_trx_rseg_n_slots_debug = 'innodb_trx_rseg_n_slots_debug'
    innodb_undo_directory = 'innodb_undo_directory'
    innodb_undo_log_truncate = 'innodb_undo_log_truncate'
    innodb_undo_logs = 'innodb_undo_logs'
    innodb_undo_tablespaces = 'innodb_undo_tablespaces'
    innodb_use_native_aio = 'innodb_use_native_aio'
    innodb_version = 'innodb_version'
    innodb_write_io_threads = 'innodb_write_io_threads'
    insert_id = 'insert_id'
    install = 'install'
    install_manual = 'install-manual'
    interactive_timeout = 'interactive_timeout'
    internal_tmp_disk_storage_engine = 'internal_tmp_disk_storage_engine'
    join_buffer_size = 'join_buffer_size'
    keep_files_on_create = 'keep_files_on_create'
    Key_blocks_not_flushed = 'Key_blocks_not_flushed'
    Key_blocks_unused = 'Key_blocks_unused'
    Key_blocks_used = 'Key_blocks_used'
    key_buffer_size = 'key_buffer_size'
    key_cache_age_threshold = 'key_cache_age_threshold'
    key_cache_block_size = 'key_cache_block_size'
    key_cache_division_limit = 'key_cache_division_limit'
    Key_read_requests = 'Key_read_requests'
    Key_reads = 'Key_reads'
    Key_write_requests = 'Key_write_requests'
    Key_writes = 'Key_writes'
    keyring_aws_cmk_id = 'keyring_aws_cmk_id'
    keyring_aws_conf_file = 'keyring_aws_conf_file'
    keyring_aws_data_file = 'keyring_aws_data_file'
    keyring_aws_region = 'keyring_aws_region'
    keyring_encrypted_file_data = 'keyring_encrypted_file_data'
    keyring_encrypted_file_password = 'keyring_encrypted_file_password'
    keyring_file_data = 'keyring_file_data'
    keyring_migration_destination = 'keyring-migration-destination'
    keyring_migration_host = 'keyring-migration-host'
    keyring_migration_password = 'keyring-migration-password'
    keyring_migration_port = 'keyring-migration-port'
    keyring_migration_socket = 'keyring-migration-socket'
    keyring_migration_source = 'keyring-migration-source'
    keyring_migration_user = 'keyring-migration-user'
    keyring_okv_conf_dir = 'keyring_okv_conf_dir'
    keyring_operations = 'keyring_operations'
    language = 'language'
    large_files_support = 'large_files_support'
    large_page_size = 'large_page_size'
    large_pages = 'large_pages'
    last_insert_id = 'last_insert_id'
    Last_query_cost = 'Last_query_cost'
    Last_query_partial_plans = 'Last_query_partial_plans'
    lc_messages = 'lc_messages'
    lc_messages_dir = 'lc_messages_dir'
    lc_time_names = 'lc_time_names'
    license = 'license'
    local_infile = 'local_infile'
    local_service = 'local-service'
    lock_wait_timeout = 'lock_wait_timeout'
    Locked_connects = 'Locked_connects'
    locked_in_memory = 'locked_in_memory'
    log_bin = 'log-bin'
    log_bin = 'log_bin'
    log_bin_basename = 'log_bin_basename'
    log_bin_index = 'log_bin_index'
    log_bin_trust_function_creators = 'log_bin_trust_function_creators'
    log_bin_use_v1_row_events = 'log_bin_use_v1_row_events'
    log_builtin_as_identified_by_password = 'log_builtin_as_identified_by_password'
    log_error = 'log_error'
    log_error_verbosity = 'log_error_verbosity'
    log_isam = 'log-isam'
    log_output = 'log_output'
    log_queries_not_using_indexes = 'log_queries_not_using_indexes'
    log_raw = 'log-raw'
    log_short_format = 'log-short-format'
    log_slave_updates = 'log_slave_updates'
    log_slow_admin_statements = 'log_slow_admin_statements'
    log_slow_slave_statements = 'log_slow_slave_statements'
    log_statements_unsafe_for_binlog = 'log_statements_unsafe_for_binlog'
    log_syslog = 'log_syslog'
    log_syslog_facility = 'log_syslog_facility'
    log_syslog_include_pid = 'log_syslog_include_pid'
    log_syslog_tag = 'log_syslog_tag'
    log_tc = 'log-tc'
    log_tc_size = 'log-tc-size'
    log_throttle_queries_not_using_indexes = 'log_throttle_queries_not_using_indexes'
    log_timestamps = 'log_timestamps'
    log_warnings = 'log_warnings'
    long_query_time = 'long_query_time'
    low_priority_updates = 'low_priority_updates'
    lower_case_file_system = 'lower_case_file_system'
    lower_case_table_names = 'lower_case_table_names'
    master_info_file = 'master-info-file'
    master_info_repository = 'master_info_repository'
    master_retry_count = 'master-retry-count'
    master_verify_checksum = 'master_verify_checksum'
    max_allowed_packet = 'max_allowed_packet'
    max_binlog_cache_size = 'max_binlog_cache_size'
    max_binlog_dump_events = 'max-binlog-dump-events'
    max_binlog_size = 'max_binlog_size'
    max_binlog_stmt_cache_size = 'max_binlog_stmt_cache_size'
    max_connect_errors = 'max_connect_errors'
    max_connections = 'max_connections'
    max_delayed_threads = 'max_delayed_threads'
    max_digest_length = 'max_digest_length'
    max_error_count = 'max_error_count'
    max_execution_time = 'max_execution_time'
    Max_execution_time_exceeded = 'Max_execution_time_exceeded'
    Max_execution_time_set = 'Max_execution_time_set'
    Max_execution_time_set_failed = 'Max_execution_time_set_failed'
    max_heap_table_size = 'max_heap_table_size'
    max_insert_delayed_threads = 'max_insert_delayed_threads'
    max_join_size = 'max_join_size'
    max_length_for_sort_data = 'max_length_for_sort_data'
    max_points_in_geometry = 'max_points_in_geometry'
    max_prepared_stmt_count = 'max_prepared_stmt_count'
    max_relay_log_size = 'max_relay_log_size'
    max_seeks_for_key = 'max_seeks_for_key'
    max_sort_length = 'max_sort_length'
    max_sp_recursion_depth = 'max_sp_recursion_depth'
    max_tmp_tables = 'max_tmp_tables'
    Max_used_connections = 'Max_used_connections'
    Max_used_connections_time = 'Max_used_connections_time'
    max_user_connections = 'max_user_connections'
    max_write_lock_count = 'max_write_lock_count'
    mecab_charset = 'mecab_charset'
    mecab_rc_file = 'mecab_rc_file'
    memlock = 'memlock'
    metadata_locks_cache_size = 'metadata_locks_cache_size'
    metadata_locks_hash_instances = 'metadata_locks_hash_instances'
    min_examined_row_limit = 'min_examined_row_limit'
    multi_range_count = 'multi_range_count'
    myisam_block_size = 'myisam-block-size'
    myisam_data_pointer_size = 'myisam_data_pointer_size'
    myisam_max_sort_file_size = 'myisam_max_sort_file_size'
    myisam_mmap_size = 'myisam_mmap_size'
    myisam_recover_options = 'myisam_recover_options'
    myisam_repair_threads = 'myisam_repair_threads'
    myisam_sort_buffer_size = 'myisam_sort_buffer_size'
    myisam_stats_method = 'myisam_stats_method'
    myisam_use_mmap = 'myisam_use_mmap'
    mysql_firewall_mode = 'mysql_firewall_mode'
    mysql_firewall_trace = 'mysql_firewall_trace'
    mysql_native_password_proxy_users = 'mysql_native_password_proxy_users'
    mysqlx = 'mysqlx'
    Mysqlx_address = 'Mysqlx_address'
    mysqlx_bind_address = 'mysqlx_bind_address'
    Mysqlx_bytes_received = 'Mysqlx_bytes_received'
    Mysqlx_bytes_sent = 'Mysqlx_bytes_sent'
    mysqlx_connect_timeout = 'mysqlx_connect_timeout'
    Mysqlx_connection_accept_errors = 'Mysqlx_connection_accept_errors'
    Mysqlx_connection_errors = 'Mysqlx_connection_errors'
    Mysqlx_connections_accepted = 'Mysqlx_connections_accepted'
    Mysqlx_connections_closed = 'Mysqlx_connections_closed'
    Mysqlx_connections_rejected = 'Mysqlx_connections_rejected'
    Mysqlx_crud_create_view = 'Mysqlx_crud_create_view'
    Mysqlx_crud_delete = 'Mysqlx_crud_delete'
    Mysqlx_crud_drop_view = 'Mysqlx_crud_drop_view'
    Mysqlx_crud_find = 'Mysqlx_crud_find'
    Mysqlx_crud_insert = 'Mysqlx_crud_insert'
    Mysqlx_crud_modify_view = 'Mysqlx_crud_modify_view'
    Mysqlx_crud_update = 'Mysqlx_crud_update'
    Mysqlx_errors_sent = 'Mysqlx_errors_sent'
    Mysqlx_errors_unknown_message_type = 'Mysqlx_errors_unknown_message_type'
    Mysqlx_expect_close = 'Mysqlx_expect_close'
    Mysqlx_expect_open = 'Mysqlx_expect_open'
    mysqlx_idle_worker_thread_timeout = 'mysqlx_idle_worker_thread_timeout'
    Mysqlx_init_error = 'Mysqlx_init_error'
    mysqlx_max_allowed_packet = 'mysqlx_max_allowed_packet'
    mysqlx_max_connections = 'mysqlx_max_connections'
    mysqlx_min_worker_threads = 'mysqlx_min_worker_threads'
    Mysqlx_notice_other_sent = 'Mysqlx_notice_other_sent'
    Mysqlx_notice_warning_sent = 'Mysqlx_notice_warning_sent'
    Mysqlx_port = 'Mysqlx_port'
    mysqlx_port = 'mysqlx_port'
    mysqlx_port_open_timeout = 'mysqlx_port_open_timeout'
    Mysqlx_rows_sent = 'Mysqlx_rows_sent'
    Mysqlx_sessions = 'Mysqlx_sessions'
    Mysqlx_sessions_accepted = 'Mysqlx_sessions_accepted'
    Mysqlx_sessions_closed = 'Mysqlx_sessions_closed'
    Mysqlx_sessions_fatal_error = 'Mysqlx_sessions_fatal_error'
    Mysqlx_sessions_killed = 'Mysqlx_sessions_killed'
    Mysqlx_sessions_rejected = 'Mysqlx_sessions_rejected'
    Mysqlx_socket = 'Mysqlx_socket'
    mysqlx_socket = 'mysqlx_socket'
    Mysqlx_ssl_accept_renegotiates = 'Mysqlx_ssl_accept_renegotiates'
    Mysqlx_ssl_accepts = 'Mysqlx_ssl_accepts'
    Mysqlx_ssl_active = 'Mysqlx_ssl_active'
    mysqlx_ssl_ca = 'mysqlx_ssl_ca'
    mysqlx_ssl_capath = 'mysqlx_ssl_capath'
    mysqlx_ssl_cert = 'mysqlx_ssl_cert'
    Mysqlx_ssl_cipher = 'Mysqlx_ssl_cipher'
    mysqlx_ssl_cipher = 'mysqlx_ssl_cipher'
    Mysqlx_ssl_cipher_list = 'Mysqlx_ssl_cipher_list'
    mysqlx_ssl_crl = 'mysqlx_ssl_crl'
    mysqlx_ssl_crlpath = 'mysqlx_ssl_crlpath'
    Mysqlx_ssl_ctx_verify_depth = 'Mysqlx_ssl_ctx_verify_depth'
    Mysqlx_ssl_ctx_verify_mode = 'Mysqlx_ssl_ctx_verify_mode'
    Mysqlx_ssl_finished_accepts = 'Mysqlx_ssl_finished_accepts'
    mysqlx_ssl_key = 'mysqlx_ssl_key'
    Mysqlx_ssl_server_not_after = 'Mysqlx_ssl_server_not_after'
    Mysqlx_ssl_server_not_before = 'Mysqlx_ssl_server_not_before'
    Mysqlx_ssl_verify_depth = 'Mysqlx_ssl_verify_depth'
    Mysqlx_ssl_verify_mode = 'Mysqlx_ssl_verify_mode'
    Mysqlx_ssl_version = 'Mysqlx_ssl_version'
    Mysqlx_stmt_create_collection = 'Mysqlx_stmt_create_collection'
    Mysqlx_stmt_create_collection_index = 'Mysqlx_stmt_create_collection_index'
    Mysqlx_stmt_disable_notices = 'Mysqlx_stmt_disable_notices'
    Mysqlx_stmt_drop_collection = 'Mysqlx_stmt_drop_collection'
    Mysqlx_stmt_drop_collection_index = 'Mysqlx_stmt_drop_collection_index'
    Mysqlx_stmt_enable_notices = 'Mysqlx_stmt_enable_notices'
    Mysqlx_stmt_ensure_collection = 'Mysqlx_stmt_ensure_collection'
    Mysqlx_stmt_execute_mysqlx = 'Mysqlx_stmt_execute_mysqlx'
    Mysqlx_stmt_execute_sql = 'Mysqlx_stmt_execute_sql'
    Mysqlx_stmt_execute_xplugin = 'Mysqlx_stmt_execute_xplugin'
    Mysqlx_stmt_kill_client = 'Mysqlx_stmt_kill_client'
    Mysqlx_stmt_list_clients = 'Mysqlx_stmt_list_clients'
    Mysqlx_stmt_list_notices = 'Mysqlx_stmt_list_notices'
    Mysqlx_stmt_list_objects = 'Mysqlx_stmt_list_objects'
    Mysqlx_stmt_ping = 'Mysqlx_stmt_ping'
    Mysqlx_worker_threads = 'Mysqlx_worker_threads'
    Mysqlx_worker_threads_active = 'Mysqlx_worker_threads_active'
    named_pipe = 'named_pipe'
    named_pipe_full_access_group = 'named_pipe_full_access_group'
    ndb_allow_copying_alter_table = 'ndb_allow_copying_alter_table'
    Ndb_api_bytes_received_count = 'Ndb_api_bytes_received_count'
    Ndb_api_bytes_received_count_session = 'Ndb_api_bytes_received_count_session'
    Ndb_api_bytes_received_count_slave = 'Ndb_api_bytes_received_count_slave'
    Ndb_api_bytes_sent_count = 'Ndb_api_bytes_sent_count'
    Ndb_api_bytes_sent_count_session = 'Ndb_api_bytes_sent_count_session'
    Ndb_api_bytes_sent_count_slave = 'Ndb_api_bytes_sent_count_slave'
    Ndb_api_event_bytes_count = 'Ndb_api_event_bytes_count'
    Ndb_api_event_bytes_count_injector = 'Ndb_api_event_bytes_count_injector'
    Ndb_api_event_data_count = 'Ndb_api_event_data_count'
    Ndb_api_event_data_count_injector = 'Ndb_api_event_data_count_injector'
    Ndb_api_event_nondata_count = 'Ndb_api_event_nondata_count'
    Ndb_api_event_nondata_count_injector = 'Ndb_api_event_nondata_count_injector'
    Ndb_api_pk_op_count = 'Ndb_api_pk_op_count'
    Ndb_api_pk_op_count_session = 'Ndb_api_pk_op_count_session'
    Ndb_api_pk_op_count_slave = 'Ndb_api_pk_op_count_slave'
    Ndb_api_pruned_scan_count = 'Ndb_api_pruned_scan_count'
    Ndb_api_pruned_scan_count_session = 'Ndb_api_pruned_scan_count_session'
    Ndb_api_pruned_scan_count_slave = 'Ndb_api_pruned_scan_count_slave'
    Ndb_api_range_scan_count = 'Ndb_api_range_scan_count'
    Ndb_api_range_scan_count_session = 'Ndb_api_range_scan_count_session'
    Ndb_api_range_scan_count_slave = 'Ndb_api_range_scan_count_slave'
    Ndb_api_read_row_count = 'Ndb_api_read_row_count'
    Ndb_api_read_row_count_session = 'Ndb_api_read_row_count_session'
    Ndb_api_read_row_count_slave = 'Ndb_api_read_row_count_slave'
    Ndb_api_scan_batch_count = 'Ndb_api_scan_batch_count'
    Ndb_api_scan_batch_count_session = 'Ndb_api_scan_batch_count_session'
    Ndb_api_scan_batch_count_slave = 'Ndb_api_scan_batch_count_slave'
    Ndb_api_table_scan_count = 'Ndb_api_table_scan_count'
    Ndb_api_table_scan_count_session = 'Ndb_api_table_scan_count_session'
    Ndb_api_table_scan_count_slave = 'Ndb_api_table_scan_count_slave'
    Ndb_api_trans_abort_count = 'Ndb_api_trans_abort_count'
    Ndb_api_trans_abort_count_session = 'Ndb_api_trans_abort_count_session'
    Ndb_api_trans_abort_count_slave = 'Ndb_api_trans_abort_count_slave'
    Ndb_api_trans_close_count = 'Ndb_api_trans_close_count'
    Ndb_api_trans_close_count_session = 'Ndb_api_trans_close_count_session'
    Ndb_api_trans_close_count_slave = 'Ndb_api_trans_close_count_slave'
    Ndb_api_trans_commit_count = 'Ndb_api_trans_commit_count'
    Ndb_api_trans_commit_count_session = 'Ndb_api_trans_commit_count_session'
    Ndb_api_trans_commit_count_slave = 'Ndb_api_trans_commit_count_slave'
    Ndb_api_trans_local_read_row_count = 'Ndb_api_trans_local_read_row_count'
    Ndb_api_trans_local_read_row_count_session = 'Ndb_api_trans_local_read_row_count_session'
    Ndb_api_trans_local_read_row_count_slave = 'Ndb_api_trans_local_read_row_count_slave'
    Ndb_api_trans_start_count = 'Ndb_api_trans_start_count'
    Ndb_api_trans_start_count_session = 'Ndb_api_trans_start_count_session'
    Ndb_api_trans_start_count_slave = 'Ndb_api_trans_start_count_slave'
    Ndb_api_uk_op_count = 'Ndb_api_uk_op_count'
    Ndb_api_uk_op_count_session = 'Ndb_api_uk_op_count_session'
    Ndb_api_uk_op_count_slave = 'Ndb_api_uk_op_count_slave'
    Ndb_api_wait_exec_complete_count = 'Ndb_api_wait_exec_complete_count'
    Ndb_api_wait_exec_complete_count_session = 'Ndb_api_wait_exec_complete_count_session'
    Ndb_api_wait_exec_complete_count_slave = 'Ndb_api_wait_exec_complete_count_slave'
    Ndb_api_wait_meta_request_count = 'Ndb_api_wait_meta_request_count'
    Ndb_api_wait_meta_request_count_session = 'Ndb_api_wait_meta_request_count_session'
    Ndb_api_wait_meta_request_count_slave = 'Ndb_api_wait_meta_request_count_slave'
    Ndb_api_wait_nanos_count = 'Ndb_api_wait_nanos_count'
    Ndb_api_wait_nanos_count_session = 'Ndb_api_wait_nanos_count_session'
    Ndb_api_wait_nanos_count_slave = 'Ndb_api_wait_nanos_count_slave'
    Ndb_api_wait_scan_result_count = 'Ndb_api_wait_scan_result_count'
    Ndb_api_wait_scan_result_count_session = 'Ndb_api_wait_scan_result_count_session'
    Ndb_api_wait_scan_result_count_slave = 'Ndb_api_wait_scan_result_count_slave'
    ndb_autoincrement_prefetch_sz = 'ndb_autoincrement_prefetch_sz'
    ndb_batch_size = 'ndb_batch_size'
    ndb_blob_read_batch_bytes = 'ndb_blob_read_batch_bytes'
    ndb_blob_write_batch_bytes = 'ndb_blob_write_batch_bytes'
    ndb_cache_check_time = 'ndb_cache_check_time'
    ndb_clear_apply_status = 'ndb_clear_apply_status'
    ndb_cluster_connection_pool = 'ndb_cluster_connection_pool'
    ndb_cluster_connection_pool_nodeids = 'ndb_cluster_connection_pool_nodeids'
    Ndb_cluster_node_id = 'Ndb_cluster_node_id'
    Ndb_config_from_host = 'Ndb_config_from_host'
    Ndb_config_from_port = 'Ndb_config_from_port'
    Ndb_conflict_fn_epoch = 'Ndb_conflict_fn_epoch'
    Ndb_conflict_fn_epoch_trans = 'Ndb_conflict_fn_epoch_trans'
    Ndb_conflict_fn_epoch2 = 'Ndb_conflict_fn_epoch2'
    Ndb_conflict_fn_epoch2_trans = 'Ndb_conflict_fn_epoch2_trans'
    Ndb_conflict_fn_max = 'Ndb_conflict_fn_max'
    Ndb_conflict_fn_old = 'Ndb_conflict_fn_old'
    Ndb_conflict_last_conflict_epoch = 'Ndb_conflict_last_conflict_epoch'
    Ndb_conflict_last_stable_epoch = 'Ndb_conflict_last_stable_epoch'
    Ndb_conflict_reflected_op_discard_count = 'Ndb_conflict_reflected_op_discard_count'
    Ndb_conflict_reflected_op_prepare_count = 'Ndb_conflict_reflected_op_prepare_count'
    Ndb_conflict_refresh_op_count = 'Ndb_conflict_refresh_op_count'
    Ndb_conflict_trans_conflict_commit_count = 'Ndb_conflict_trans_conflict_commit_count'
    Ndb_conflict_trans_detect_iter_count = 'Ndb_conflict_trans_detect_iter_count'
    Ndb_conflict_trans_reject_count = 'Ndb_conflict_trans_reject_count'
    Ndb_conflict_trans_row_conflict_count = 'Ndb_conflict_trans_row_conflict_count'
    Ndb_conflict_trans_row_reject_count = 'Ndb_conflict_trans_row_reject_count'
    ndb_connectstring = 'ndb-connectstring'
    ndb_data_node_neighbour = 'ndb_data_node_neighbour'
    ndb_default_column_format = 'ndb_default_column_format'
    ndb_default_column_format = 'ndb_default_column_format'
    ndb_deferred_constraints = 'ndb_deferred_constraints'
    ndb_deferred_constraints = 'ndb_deferred_constraints'
    ndb_distribution = 'ndb_distribution'
    ndb_distribution = 'ndb_distribution'
    Ndb_epoch_delete_delete_count = 'Ndb_epoch_delete_delete_count'
    ndb_eventbuffer_free_percent = 'ndb_eventbuffer_free_percent'
    ndb_eventbuffer_max_alloc = 'ndb_eventbuffer_max_alloc'
    Ndb_execute_count = 'Ndb_execute_count'
    ndb_extra_logging = 'ndb_extra_logging'
    ndb_force_send = 'ndb_force_send'
    ndb_fully_replicated = 'ndb_fully_replicated'
    ndb_index_stat_enable = 'ndb_index_stat_enable'
    ndb_index_stat_option = 'ndb_index_stat_option'
    ndb_join_pushdown = 'ndb_join_pushdown'
    Ndb_last_commit_epoch_server = 'Ndb_last_commit_epoch_server'
    Ndb_last_commit_epoch_session = 'Ndb_last_commit_epoch_session'
    ndb_log_apply_status = 'ndb_log_apply_status'
    ndb_log_apply_status = 'ndb_log_apply_status'
    ndb_log_bin = 'ndb_log_bin'
    ndb_log_binlog_index = 'ndb_log_binlog_index'
    ndb_log_empty_epochs = 'ndb_log_empty_epochs'
    ndb_log_empty_epochs = 'ndb_log_empty_epochs'
    ndb_log_empty_update = 'ndb_log_empty_update'
    ndb_log_empty_update = 'ndb_log_empty_update'
    ndb_log_exclusive_reads = 'ndb_log_exclusive_reads'
    ndb_log_exclusive_reads = 'ndb_log_exclusive_reads'
    ndb_log_orig = 'ndb_log_orig'
    ndb_log_orig = 'ndb_log_orig'
    ndb_log_transaction_id = 'ndb_log_transaction_id'
    ndb_log_transaction_id = 'ndb_log_transaction_id'
    ndb_log_update_as_write = 'ndb_log_update_as_write'
    ndb_log_update_minimal = 'ndb_log_update_minimal'
    ndb_log_updated_only = 'ndb_log_updated_only'
    ndb_mgmd_host = 'ndb-mgmd-host'
    ndb_nodeid = 'ndb_nodeid'
    Ndb_number_of_data_nodes = 'Ndb_number_of_data_nodes'
    ndb_optimization_delay = 'ndb_optimization_delay'
    ndb_optimized_node_selection = 'ndb_optimized_node_selection'
    Ndb_pruned_scan_count = 'Ndb_pruned_scan_count'
    Ndb_pushed_queries_defined = 'Ndb_pushed_queries_defined'
    Ndb_pushed_queries_dropped = 'Ndb_pushed_queries_dropped'
    Ndb_pushed_queries_executed = 'Ndb_pushed_queries_executed'
    Ndb_pushed_reads = 'Ndb_pushed_reads'
    ndb_read_backup = 'ndb_read_backup'
    ndb_recv_thread_activation_threshold = 'ndb_recv_thread_activation_threshold'
    ndb_recv_thread_cpu_mask = 'ndb_recv_thread_cpu_mask'
    ndb_report_thresh_binlog_epoch_slip = 'ndb_report_thresh_binlog_epoch_slip'
    ndb_report_thresh_binlog_mem_usage = 'ndb_report_thresh_binlog_mem_usage'
    ndb_row_checksum = 'ndb_row_checksum'
    Ndb_scan_count = 'Ndb_scan_count'
    ndb_show_foreign_key_mock_tables = 'ndb_show_foreign_key_mock_tables'
    ndb_slave_conflict_role = 'ndb_slave_conflict_role'
    Ndb_slave_max_replicated_epoch = 'Ndb_slave_max_replicated_epoch'
    Ndb_system_name = 'Ndb_system_name'
    ndb_table_no_logging = 'ndb_table_no_logging'
    ndb_table_temporary = 'ndb_table_temporary'
    ndb_transid_mysql_connection_map = 'ndb-transid-mysql-connection-map'
    ndb_use_copying_alter_table = 'ndb_use_copying_alter_table'
    ndb_use_exact_count = 'ndb_use_exact_count'
    ndb_use_transactions = 'ndb_use_transactions'
    ndb_version = 'ndb_version'
    ndb_version_string = 'ndb_version_string'
    ndb_wait_connected = 'ndb_wait_connected'
    ndb_wait_setup = 'ndb_wait_setup'
    ndbcluster = 'ndbcluster'
    ndbinfo_database = 'ndbinfo_database'
    ndbinfo_max_bytes = 'ndbinfo_max_bytes'
    ndbinfo_max_rows = 'ndbinfo_max_rows'
    ndbinfo_offline = 'ndbinfo_offline'
    ndbinfo_show_hidden = 'ndbinfo_show_hidden'
    ndbinfo_table_prefix = 'ndbinfo_table_prefix'
    ndbinfo_version = 'ndbinfo_version'
    net_buffer_length = 'net_buffer_length'
    net_read_timeout = 'net_read_timeout'
    net_retry_count = 'net_retry_count'
    net_write_timeout = 'net_write_timeout'
    new = 'new'
    ngram_token_size = 'ngram_token_size'
    no_defaults = 'no-defaults'
    Not_flushed_delayed_rows = 'Not_flushed_delayed_rows'
    offline_mode = 'offline_mode'
    old = 'old'
    old_alter_table = 'old_alter_table'
    old_passwords = 'old_passwords'
    old_style_user_limits = 'old-style-user-limits'
    Ongoing_anonymous_gtid_violating_transaction_count = 'Ongoing_anonymous_gtid_violating_transaction_count'
    Ongoing_anonymous_transaction_count = 'Ongoing_anonymous_transaction_count'
    Ongoing_automatic_gtid_violating_transaction_count = 'Ongoing_automatic_gtid_violating_transaction_count'
    Open_files = 'Open_files'
    open_files_limit = 'open_files_limit'
    Open_streams = 'Open_streams'
    Open_table_definitions = 'Open_table_definitions'
    Open_tables = 'Open_tables'
    Opened_files = 'Opened_files'
    Opened_table_definitions = 'Opened_table_definitions'
    Opened_tables = 'Opened_tables'
    optimizer_prune_level = 'optimizer_prune_level'
    optimizer_search_depth = 'optimizer_search_depth'
    optimizer_switch = 'optimizer_switch'
    optimizer_trace = 'optimizer_trace'
    optimizer_trace_features = 'optimizer_trace_features'
    optimizer_trace_limit = 'optimizer_trace_limit'
    optimizer_trace_max_mem_size = 'optimizer_trace_max_mem_size'
    optimizer_trace_offset = 'optimizer_trace_offset'
    parser_max_mem_size = 'parser_max_mem_size'
    partition = 'partition'
    performance_schema = 'performance_schema'
    Performance_schema_accounts_lost = 'Performance_schema_accounts_lost'
    performance_schema_accounts_size = 'performance_schema_accounts_size'
    Performance_schema_cond_classes_lost = 'Performance_schema_cond_classes_lost'
    Performance_schema_cond_instances_lost = 'Performance_schema_cond_instances_lost'
    performance_schema_consumer_events_stages_current = 'performance-schema-consumer-events-stages-current'
    performance_schema_consumer_events_stages_history = 'performance-schema-consumer-events-stages-history'
    performance_schema_consumer_events_stages_history_long = 'performance-schema-consumer-events-stages-history-long'
    performance_schema_consumer_events_statements_current = 'performance-schema-consumer-events-statements-current'
    performance_schema_consumer_events_statements_history = 'performance-schema-consumer-events-statements-history'
    performance_schema_consumer_events_statements_history_long = 'performance-schema-consumer-events-statements-history-long'
    performance_schema_consumer_events_transactions_current = 'performance-schema-consumer-events-transactions-current'
    performance_schema_consumer_events_transactions_history = 'performance-schema-consumer-events-transactions-history'
    performance_schema_consumer_events_transactions_history_long = 'performance-schema-consumer-events-transactions-history-long'
    performance_schema_consumer_events_waits_current = 'performance-schema-consumer-events-waits-current'
    performance_schema_consumer_events_waits_history = 'performance-schema-consumer-events-waits-history'
    performance_schema_consumer_events_waits_history_long = 'performance-schema-consumer-events-waits-history-long'
    performance_schema_consumer_global_instrumentation = 'performance-schema-consumer-global-instrumentation'
    performance_schema_consumer_statements_digest = 'performance-schema-consumer-statements-digest'
    performance_schema_consumer_thread_instrumentation = 'performance-schema-consumer-thread-instrumentation'
    Performance_schema_digest_lost = 'Performance_schema_digest_lost'
    performance_schema_digests_size = 'performance_schema_digests_size'
    performance_schema_events_stages_history_long_size = 'performance_schema_events_stages_history_long_size'
    performance_schema_events_stages_history_size = 'performance_schema_events_stages_history_size'
    performance_schema_events_statements_history_long_size = 'performance_schema_events_statements_history_long_size'
    performance_schema_events_statements_history_size = 'performance_schema_events_statements_history_size'
    performance_schema_events_transactions_history_long_size = 'performance_schema_events_transactions_history_long_size'
    performance_schema_events_transactions_history_size = 'performance_schema_events_transactions_history_size'
    performance_schema_events_waits_history_long_size = 'performance_schema_events_waits_history_long_size'
    performance_schema_events_waits_history_size = 'performance_schema_events_waits_history_size'
    Performance_schema_file_classes_lost = 'Performance_schema_file_classes_lost'
    Performance_schema_file_handles_lost = 'Performance_schema_file_handles_lost'
    Performance_schema_file_instances_lost = 'Performance_schema_file_instances_lost'
    Performance_schema_hosts_lost = 'Performance_schema_hosts_lost'
    performance_schema_hosts_size = 'performance_schema_hosts_size'
    Performance_schema_index_stat_lost = 'Performance_schema_index_stat_lost'
    performance_schema_instrument = 'performance-schema-instrument'
    Performance_schema_locker_lost = 'Performance_schema_locker_lost'
    performance_schema_max_cond_classes = 'performance_schema_max_cond_classes'
    performance_schema_max_cond_instances = 'performance_schema_max_cond_instances'
    performance_schema_max_digest_length = 'performance_schema_max_digest_length'
    performance_schema_max_file_classes = 'performance_schema_max_file_classes'
    performance_schema_max_file_handles = 'performance_schema_max_file_handles'
    performance_schema_max_file_instances = 'performance_schema_max_file_instances'
    performance_schema_max_index_stat = 'performance_schema_max_index_stat'
    performance_schema_max_memory_classes = 'performance_schema_max_memory_classes'
    performance_schema_max_metadata_locks = 'performance_schema_max_metadata_locks'
    performance_schema_max_mutex_classes = 'performance_schema_max_mutex_classes'
    performance_schema_max_mutex_instances = 'performance_schema_max_mutex_instances'
    performance_schema_max_prepared_statements_instances = 'performance_schema_max_prepared_statements_instances'
    performance_schema_max_program_instances = 'performance_schema_max_program_instances'
    performance_schema_max_rwlock_classes = 'performance_schema_max_rwlock_classes'
    performance_schema_max_rwlock_instances = 'performance_schema_max_rwlock_instances'
    performance_schema_max_socket_classes = 'performance_schema_max_socket_classes'
    performance_schema_max_socket_instances = 'performance_schema_max_socket_instances'
    performance_schema_max_sql_text_length = 'performance_schema_max_sql_text_length'
    performance_schema_max_stage_classes = 'performance_schema_max_stage_classes'
    performance_schema_max_statement_classes = 'performance_schema_max_statement_classes'
    performance_schema_max_statement_stack = 'performance_schema_max_statement_stack'
    performance_schema_max_table_handles = 'performance_schema_max_table_handles'
    performance_schema_max_table_instances = 'performance_schema_max_table_instances'
    performance_schema_max_table_lock_stat = 'performance_schema_max_table_lock_stat'
    performance_schema_max_thread_classes = 'performance_schema_max_thread_classes'
    performance_schema_max_thread_instances = 'performance_schema_max_thread_instances'
    Performance_schema_memory_classes_lost = 'Performance_schema_memory_classes_lost'
    Performance_schema_metadata_lock_lost = 'Performance_schema_metadata_lock_lost'
    Performance_schema_mutex_classes_lost = 'Performance_schema_mutex_classes_lost'
    Performance_schema_mutex_instances_lost = 'Performance_schema_mutex_instances_lost'
    Performance_schema_nested_statement_lost = 'Performance_schema_nested_statement_lost'
    Performance_schema_prepared_statements_lost = 'Performance_schema_prepared_statements_lost'
    Performance_schema_program_lost = 'Performance_schema_program_lost'
    Performance_schema_rwlock_classes_lost = 'Performance_schema_rwlock_classes_lost'
    Performance_schema_rwlock_instances_lost = 'Performance_schema_rwlock_instances_lost'
    Performance_schema_session_connect_attrs_lost = 'Performance_schema_session_connect_attrs_lost'
    performance_schema_session_connect_attrs_size = 'performance_schema_session_connect_attrs_size'
    performance_schema_setup_actors_size = 'performance_schema_setup_actors_size'
    performance_schema_setup_objects_size = 'performance_schema_setup_objects_size'
    Performance_schema_socket_classes_lost = 'Performance_schema_socket_classes_lost'
    Performance_schema_socket_instances_lost = 'Performance_schema_socket_instances_lost'
    Performance_schema_stage_classes_lost = 'Performance_schema_stage_classes_lost'
    Performance_schema_statement_classes_lost = 'Performance_schema_statement_classes_lost'
    Performance_schema_table_handles_lost = 'Performance_schema_table_handles_lost'
    Performance_schema_table_instances_lost = 'Performance_schema_table_instances_lost'
    Performance_schema_table_lock_stat_lost = 'Performance_schema_table_lock_stat_lost'
    Performance_schema_thread_classes_lost = 'Performance_schema_thread_classes_lost'
    Performance_schema_thread_instances_lost = 'Performance_schema_thread_instances_lost'
    Performance_schema_users_lost = 'Performance_schema_users_lost'
    performance_schema_users_size = 'performance_schema_users_size'
    pid_file = 'pid_file'
    plugin_dir = 'plugin_dir'
    plugin_load = 'plugin_load'
    plugin_load_add = 'plugin_load_add'
    plugin_xxx = 'plugin-xxx'
    port = 'port'
    port_open_timeout = 'port-open-timeout'
    preload_buffer_size = 'preload_buffer_size'
    Prepared_stmt_count = 'Prepared_stmt_count'
    print_defaults = 'print-defaults'
    profiling = 'profiling'
    profiling_history_size = 'profiling_history_size'
    protocol_version = 'protocol_version'
    proxy_user = 'proxy_user'
    pseudo_slave_mode = 'pseudo_slave_mode'
    pseudo_thread_id = 'pseudo_thread_id'
    Qcache_free_blocks = 'Qcache_free_blocks'
    Qcache_free_memory = 'Qcache_free_memory'
    Qcache_hits = 'Qcache_hits'
    Qcache_inserts = 'Qcache_inserts'
    Qcache_lowmem_prunes = 'Qcache_lowmem_prunes'
    Qcache_not_cached = 'Qcache_not_cached'
    Qcache_queries_in_cache = 'Qcache_queries_in_cache'
    Qcache_total_blocks = 'Qcache_total_blocks'
    Queries = 'Queries'
    query_alloc_block_size = 'query_alloc_block_size'
    query_cache_limit = 'query_cache_limit'
    query_cache_min_res_unit = 'query_cache_min_res_unit'
    query_cache_size = 'query_cache_size'
    query_cache_type = 'query_cache_type'
    query_cache_wlock_invalidate = 'query_cache_wlock_invalidate'
    query_prealloc_size = 'query_prealloc_size'
    Questions = 'Questions'
    rand_seed1 = 'rand_seed1'
    rand_seed2 = 'rand_seed2'
    range_alloc_block_size = 'range_alloc_block_size'
    range_optimizer_max_mem_size = 'range_optimizer_max_mem_size'
    rbr_exec_mode = 'rbr_exec_mode'
    read_buffer_size = 'read_buffer_size'
    read_only = 'read_only'
    read_rnd_buffer_size = 'read_rnd_buffer_size'
    relay_log = 'relay_log'
    relay_log_basename = 'relay_log_basename'
    relay_log_index = 'relay_log_index'
    relay_log_info_file = 'relay_log_info_file'
    relay_log_info_repository = 'relay_log_info_repository'
    relay_log_purge = 'relay_log_purge'
    relay_log_recovery = 'relay_log_recovery'
    relay_log_space_limit = 'relay_log_space_limit'
    remove = 'remove'
    replicate_do_db = 'replicate-do-db'
    replicate_do_table = 'replicate-do-table'
    replicate_ignore_db = 'replicate-ignore-db'
    replicate_ignore_table = 'replicate-ignore-table'
    replicate_rewrite_db = 'replicate-rewrite-db'
    replicate_same_server_id = 'replicate-same-server-id'
    replicate_wild_do_table = 'replicate-wild-do-table'
    replicate_wild_ignore_table = 'replicate-wild-ignore-table'
    report_host = 'report_host'
    report_password = 'report_password'
    report_port = 'report_port'
    report_user = 'report_user'
    require_secure_transport = 'require_secure_transport'
    rewriter_enabled = 'rewriter_enabled'
    Rewriter_number_loaded_rules = 'Rewriter_number_loaded_rules'
    Rewriter_number_reloads = 'Rewriter_number_reloads'
    Rewriter_number_rewritten_queries = 'Rewriter_number_rewritten_queries'
    Rewriter_reload_error = 'Rewriter_reload_error'
    rewriter_verbose = 'rewriter_verbose'
    Rpl_semi_sync_master_clients = 'Rpl_semi_sync_master_clients'
    rpl_semi_sync_master_enabled = 'rpl_semi_sync_master_enabled'
    Rpl_semi_sync_master_net_avg_wait_time = 'Rpl_semi_sync_master_net_avg_wait_time'
    Rpl_semi_sync_master_net_wait_time = 'Rpl_semi_sync_master_net_wait_time'
    Rpl_semi_sync_master_net_waits = 'Rpl_semi_sync_master_net_waits'
    Rpl_semi_sync_master_no_times = 'Rpl_semi_sync_master_no_times'
    Rpl_semi_sync_master_no_tx = 'Rpl_semi_sync_master_no_tx'
    Rpl_semi_sync_master_status = 'Rpl_semi_sync_master_status'
    Rpl_semi_sync_master_timefunc_failures = 'Rpl_semi_sync_master_timefunc_failures'
    rpl_semi_sync_master_timeout = 'rpl_semi_sync_master_timeout'
    rpl_semi_sync_master_trace_level = 'rpl_semi_sync_master_trace_level'
    Rpl_semi_sync_master_tx_avg_wait_time = 'Rpl_semi_sync_master_tx_avg_wait_time'
    Rpl_semi_sync_master_tx_wait_time = 'Rpl_semi_sync_master_tx_wait_time'
    Rpl_semi_sync_master_tx_waits = 'Rpl_semi_sync_master_tx_waits'
    rpl_semi_sync_master_wait_for_slave_count = 'rpl_semi_sync_master_wait_for_slave_count'
    rpl_semi_sync_master_wait_no_slave = 'rpl_semi_sync_master_wait_no_slave'
    rpl_semi_sync_master_wait_point = 'rpl_semi_sync_master_wait_point'
    Rpl_semi_sync_master_wait_pos_backtraverse = 'Rpl_semi_sync_master_wait_pos_backtraverse'
    Rpl_semi_sync_master_wait_sessions = 'Rpl_semi_sync_master_wait_sessions'
    Rpl_semi_sync_master_yes_tx = 'Rpl_semi_sync_master_yes_tx'
    rpl_semi_sync_slave_enabled = 'rpl_semi_sync_slave_enabled'
    Rpl_semi_sync_slave_status = 'Rpl_semi_sync_slave_status'
    rpl_semi_sync_slave_trace_level = 'rpl_semi_sync_slave_trace_level'
    rpl_stop_slave_timeout = 'rpl_stop_slave_timeout'
    Rsa_public_key = 'Rsa_public_key'
    safe_user_create = 'safe-user-create'
    secure_auth = 'secure_auth'
    secure_file_priv = 'secure_file_priv'
    Select_full_join = 'Select_full_join'
    Select_full_range_join = 'Select_full_range_join'
    Select_range = 'Select_range'
    Select_range_check = 'Select_range_check'
    Select_scan = 'Select_scan'
    server_id = 'server_id'
    server_id_bits = 'server_id_bits'
    server_uuid = 'server_uuid'
    session_track_gtids = 'session_track_gtids'
    session_track_schema = 'session_track_schema'
    session_track_state_change = 'session_track_state_change'
    session_track_system_variables = 'session_track_system_variables'
    session_track_transaction_info = 'session_track_transaction_info'
    sha256_password_auto_generate_rsa_keys = 'sha256_password_auto_generate_rsa_keys'
    sha256_password_private_key_path = 'sha256_password_private_key_path'
    sha256_password_proxy_users = 'sha256_password_proxy_users'
    sha256_password_public_key_path = 'sha256_password_public_key_path'
    shared_memory = 'shared_memory'
    shared_memory_base_name = 'shared_memory_base_name'
    show_compatibility_56 = 'show_compatibility_56'
    show_create_table_verbosity = 'show_create_table_verbosity'
    show_old_temporals = 'show_old_temporals'
    show_slave_auth_info = 'show-slave-auth-info'
    skip_character_set_client_handshake = 'skip-character-set-client-handshake'
    skip_external_locking = 'skip_external_locking'
    skip_grant_tables = 'skip-grant-tables'
    skip_host_cache = 'skip-host-cache'
    skip_name_resolve = 'skip_name_resolve'
    skip_ndbcluster = 'skip-ndbcluster'
    skip_networking = 'skip_networking'
    skip_new = 'skip-new'
    skip_partition = 'skip-partition'
    skip_show_database = 'skip_show_database'
    skip_slave_start = 'skip-slave-start'
    skip_ssl = 'skip-ssl'
    skip_stack_trace = 'skip-stack-trace'
    slave_allow_batching = 'slave_allow_batching'
    slave_checkpoint_group = 'slave_checkpoint_group'
    slave_checkpoint_period = 'slave_checkpoint_period'
    slave_compressed_protocol = 'slave_compressed_protocol'
    slave_exec_mode = 'slave_exec_mode'
    Slave_heartbeat_period = 'Slave_heartbeat_period'
    Slave_last_heartbeat = 'Slave_last_heartbeat'
    slave_load_tmpdir = 'slave_load_tmpdir'
    slave_max_allowed_packet = 'slave_max_allowed_packet'
    slave_net_timeout = 'slave_net_timeout'
    Slave_open_temp_tables = 'Slave_open_temp_tables'
    slave_parallel_type = 'slave_parallel_type'
    slave_parallel_workers = 'slave_parallel_workers'
    slave_pending_jobs_size_max = 'slave_pending_jobs_size_max'
    slave_preserve_commit_order = 'slave_preserve_commit_order'
    Slave_received_heartbeats = 'Slave_received_heartbeats'
    Slave_retried_transactions = 'Slave_retried_transactions'
    Slave_rows_last_search_algorithm_used = 'Slave_rows_last_search_algorithm_used'
    slave_rows_search_algorithms = 'slave_rows_search_algorithms'
    Slave_running = 'Slave_running'
    slave_skip_errors = 'slave_skip_errors'
    slave_sql_verify_checksum = 'slave-sql-verify-checksum'
    slave_sql_verify_checksum = 'slave_sql_verify_checksum'
    slave_transaction_retries = 'slave_transaction_retries'
    slave_type_conversions = 'slave_type_conversions'
    Slow_launch_threads = 'Slow_launch_threads'
    slow_launch_time = 'slow_launch_time'
    Slow_queries = 'Slow_queries'
    slow_query_log = 'slow_query_log'
    slow_query_log_file = 'slow_query_log_file'
    slow_start_timeout = 'slow-start-timeout'
    socket = 'socket'
    sort_buffer_size = 'sort_buffer_size'
    Sort_merge_passes = 'Sort_merge_passes'
    Sort_range = 'Sort_range'
    Sort_rows = 'Sort_rows'
    Sort_scan = 'Sort_scan'
    sporadic_binlog_dump_fail = 'sporadic-binlog-dump-fail'
    sql_auto_is_null = 'sql_auto_is_null'
    sql_big_selects = 'sql_big_selects'
    sql_buffer_result = 'sql_buffer_result'
    sql_log_bin = 'sql_log_bin'
    sql_log_off = 'sql_log_off'
    sql_mode = 'sql_mode'
    sql_notes = 'sql_notes'
    sql_quote_show_create = 'sql_quote_show_create'
    sql_safe_updates = 'sql_safe_updates'
    sql_select_limit = 'sql_select_limit'
    sql_slave_skip_counter = 'sql_slave_skip_counter'
    sql_warnings = 'sql_warnings'
    ssl = 'ssl'
    Ssl_accept_renegotiates = 'Ssl_accept_renegotiates'
    Ssl_accepts = 'Ssl_accepts'
    ssl_ca = 'ssl_ca'
    Ssl_callback_cache_hits = 'Ssl_callback_cache_hits'
    ssl_capath = 'ssl_capath'
    ssl_cert = 'ssl_cert'
    Ssl_cipher = 'Ssl_cipher'
    ssl_cipher = 'ssl_cipher'
    Ssl_cipher_list = 'Ssl_cipher_list'
    Ssl_client_connects = 'Ssl_client_connects'
    Ssl_connect_renegotiates = 'Ssl_connect_renegotiates'
    ssl_crl = 'ssl_crl'
    ssl_crlpath = 'ssl_crlpath'
    Ssl_ctx_verify_depth = 'Ssl_ctx_verify_depth'
    Ssl_ctx_verify_mode = 'Ssl_ctx_verify_mode'
    Ssl_default_timeout = 'Ssl_default_timeout'
    Ssl_finished_accepts = 'Ssl_finished_accepts'
    Ssl_finished_connects = 'Ssl_finished_connects'
    ssl_key = 'ssl_key'
    Ssl_server_not_after = 'Ssl_server_not_after'
    Ssl_server_not_before = 'Ssl_server_not_before'
    Ssl_session_cache_hits = 'Ssl_session_cache_hits'
    Ssl_session_cache_misses = 'Ssl_session_cache_misses'
    Ssl_session_cache_mode = 'Ssl_session_cache_mode'
    Ssl_session_cache_overflows = 'Ssl_session_cache_overflows'
    Ssl_session_cache_size = 'Ssl_session_cache_size'
    Ssl_session_cache_timeouts = 'Ssl_session_cache_timeouts'
    Ssl_sessions_reused = 'Ssl_sessions_reused'
    Ssl_used_session_cache_entries = 'Ssl_used_session_cache_entries'
    Ssl_verify_depth = 'Ssl_verify_depth'
    Ssl_verify_mode = 'Ssl_verify_mode'
    Ssl_version = 'Ssl_version'
    standalone = 'standalone'
    stored_program_cache = 'stored_program_cache'
    super_large_pages = 'super-large-pages'
    super_read_only = 'super_read_only'
    symbolic_links = 'symbolic-links'
    sync_binlog = 'sync_binlog'
    sync_frm = 'sync_frm'
    sync_master_info = 'sync_master_info'
    sync_relay_log = 'sync_relay_log'
    sync_relay_log_info = 'sync_relay_log_info'
    sysdate_is_now = 'sysdate-is-now'
    system_time_zone = 'system_time_zone'
    table_definition_cache = 'table_definition_cache'
    Table_locks_immediate = 'Table_locks_immediate'
    Table_locks_waited = 'Table_locks_waited'
    table_open_cache = 'table_open_cache'
    Table_open_cache_hits = 'Table_open_cache_hits'
    table_open_cache_instances = 'table_open_cache_instances'
    Table_open_cache_misses = 'Table_open_cache_misses'
    Table_open_cache_overflows = 'Table_open_cache_overflows'
    tc_heuristic_recover = 'tc-heuristic-recover'
    Tc_log_max_pages_used = 'Tc_log_max_pages_used'
    Tc_log_page_size = 'Tc_log_page_size'
    Tc_log_page_waits = 'Tc_log_page_waits'
    temp_pool = 'temp-pool'
    thread_cache_size = 'thread_cache_size'
    thread_handling = 'thread_handling'
    thread_pool_algorithm = 'thread_pool_algorithm'
    thread_pool_high_priority_connection = 'thread_pool_high_priority_connection'
    thread_pool_max_unused_threads = 'thread_pool_max_unused_threads'
    thread_pool_prio_kickup_timer = 'thread_pool_prio_kickup_timer'
    thread_pool_size = 'thread_pool_size'
    thread_pool_stall_limit = 'thread_pool_stall_limit'
    thread_stack = 'thread_stack'
    Threads_cached = 'Threads_cached'
    Threads_connected = 'Threads_connected'
    Threads_created = 'Threads_created'
    Threads_running = 'Threads_running'
    time_format = 'time_format'
    time_zone = 'time_zone'
    timestamp = 'timestamp'
    tls_version = 'tls_version'
    tmp_table_size = 'tmp_table_size'
    tmpdir = 'tmpdir'
    transaction_alloc_block_size = 'transaction_alloc_block_size'
    transaction_allow_batching = 'transaction_allow_batching'
    transaction_isolation = 'transaction_isolation'
    transaction_prealloc_size = 'transaction_prealloc_size'
    transaction_read_only = 'transaction_read_only'
    transaction_write_set_extraction = 'transaction_write_set_extraction'
    tx_isolation = 'tx_isolation'
    tx_read_only = 'tx_read_only'
    unique_checks = 'unique_checks'
    updatable_views_with_limit = 'updatable_views_with_limit'
    Uptime = 'Uptime'
    Uptime_since_flush_status = 'Uptime_since_flush_status'
    user = 'user'
    validate_password = 'validate-password'
    validate_password_check_user_name = 'validate_password_check_user_name'
    validate_password_dictionary_file = 'validate_password_dictionary_file'
    validate_password_dictionary_file_last_parsed = 'validate_password_dictionary_file_last_parsed'
    validate_password_dictionary_file_words_count = 'validate_password_dictionary_file_words_count'
    validate_password_length = 'validate_password_length'
    validate_password_mixed_case_count = 'validate_password_mixed_case_count'
    validate_password_number_count = 'validate_password_number_count'
    validate_password_policy = 'validate_password_policy'
    validate_password_special_char_count = 'validate_password_special_char_count'
    validate_user_plugins = 'validate_user_plugins'
    verbose = 'verbose'
    version = 'version'
    version_comment = 'version_comment'
    version_compile_machine = 'version_compile_machine'
    version_compile_os = 'version_compile_os'
    version_tokens_session = 'version_tokens_session'
    version_tokens_session_number = 'version_tokens_session_number'
    wait_timeout = 'wait_timeout'
    warning_count = 'warning_count'

