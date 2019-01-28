import geocoder


def geocode(address):
    key = 'FgtSCnlfiP0myLJssXyRAFuIsyHAzjx4'
    g = geocoder.mapquest(address, key=key)
    coords = (g.lat, g.lng)
    return coords


def retrieve_address(details):
    location = details['details']['location']
    order = ['address', 'address2', 'city', 'country']
    address = []
    for item in order:
        try:
            address.append(location[item])
        except KeyError:
            continue
    address = ' '.join(address)
    return address


