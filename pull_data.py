import solaredge as se

from utilities import *

# API access
key = se.Solaredge("###")

# Choose data end date
end_date = '2018-11-18'

# List of all sites of interest
site_ids = [655402, 655467, 410977, 605351, 672695, 520043, 558809, 644207,
            852227, 295363, 460596, 322405, 424625, 417624, 658334, 598654]

# Check what is already stored
site_ids = check_data(site_ids, end_date)

# Pull data and consolidate
df = consolidate_data(key, site_ids, end_date)

# Save data to disk
save_data(df)

