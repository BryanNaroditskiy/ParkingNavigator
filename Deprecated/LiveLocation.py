from ipregistry import IpregistryClient

client = IpregistryClient("m0bayumbslcoiw8v")  


ipInfo = client.lookup()
if ipInfo and hasattr(ipInfo, 'location') and 'latitude' in ipInfo.location and 'longitude' in ipInfo.location:
    latitude = ipInfo.location['latitude']
    longitude = ipInfo.location['longitude']
    print(f"Latitude: {latitude}, Longitude: {longitude}")
else:
    print("Latitude and/or longitude not available in the response.")