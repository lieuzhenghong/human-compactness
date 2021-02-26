TRACT_SPATIAL_DIVERSITY_SCORES = "./tract_spatial_diversity.csv"
STATE_NAMES = {
    "02": "Alaska",
    "01": "Alabama",
    "05": "Arkansas",
    "04": "Arizona",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "12": "Florida",
    "13": "Georgia",
    "66": "Guam",
    "15": "Hawaii",
    "19": "Iowa",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "25": "Massachusetts",
    "24": "Maryland",
    "23": "Maine",
    "26": "Michigan",
    "27": "Minnesota",
    "29": "Missouri",
    "28": "Mississippi",
    "30": "Montana",
    "37": "North_Carolina",
    "38": "North_Dakota",
    "31": "Nebraska",
    "33": "New_Hampshire",
    "34": "New_Jersey",
    "35": "New_Mexico",
    "32": "Nevada",
    "36": "New_York",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "72": "Puerto_Rico",
    "44": "Rhode_Island",
    "45": "South_Carolina",
    "46": "South_Dakota",
    "47": "Tenessee",
    "48": "Texas",
    "49": "Utah",
    "51": "Virginia",
    "50": "Vermont",
    "53": "Washington",
    "55": "Wisconsin",
    "54": "West_Virginia",
    "56": "Wyoming",
}

NUM_DISTRICTS = {
    "01": 7,
    "04": 8,
    "08": 7,
    "09": 5,
    "13": 13,
    "16": 2,
    "19": 4,
    "22": 7,
    "24": 8,
    "33": 2,
    "23": 2,
    "44": 2,
    "49": 3,
    "55": 8,
}

SPATIAL_DIVERSITY_FACTOR_WEIGHTS = (
    0.1464,
    0.1182,
    0.101,
    0.0775,
    0.0501,
    0.0399,
    0.0389,
    0.0366,
)

# I'll be doing the following districts:

# fips_list = ['13'] # Georgia
# fips_list = ['22']  # Louisiana
# fips_list = ['24'] # Maryland
# fips_list = ['55']  # Wisconsin
# fips_list = ['04', '08', '16', '19', '33', '49']
# fips_list = ['13', '22', '24', '55']
# fips_list = ['16']
# fips_list = ['19', '33', '49']
# fips_list = ['23', '44'] # Maine and Rhode Island
FIPS_LIST = ["09"]

SAMPLE_RICHNESS = 1000