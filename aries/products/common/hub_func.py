def get_hub_status_msg(status, cn_header):
    hub_status_msg_en = ['Current unavailable', 'Normally operation', 'Coming soon']
    hub_status_msg_cn = ['Current unavailable (CHN)', 'Normally operation (CHN)', 'Coming soon (CHN)']

    if cn_header:
        return hub_status_msg_cn[status]

    return hub_status_msg_en[status]
