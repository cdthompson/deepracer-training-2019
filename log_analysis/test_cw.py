import cw_utils

sim_id = 'sim-bqj8wrck88b3'
stream_name = 'sim-bqj8wrck88b3/2019-08-02T16-49-45.117Z_80272e43-24e4-4de6-a6bb-78dcd5db7477/SimulationApplicationLogs' ## CHANGE This to your simulation application ID
fname = 'logs/deepracer-%s.log' % sim_id
cw_utils.download_log(fname, log_group='/aws/robomaker/SimulationJobs', stream_prefix=stream_name)
