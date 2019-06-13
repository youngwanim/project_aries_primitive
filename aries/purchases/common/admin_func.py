def get_user_address_data(name, lat, long, fmt_adr):
    result = {
        'id': 0,
        'name': name,
        'latitude': lat,
        'longitude': long,
        'city': 'shanghai',
        'province': 'shanghai',
        'format_address': fmt_adr
    }
    return result
