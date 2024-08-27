import os
from dotenv import load_dotenv
import json
import requests
import pandas as pd
import progressbar

load_dotenv()
API_KEY = os.getenv('API_KEY')


def find_all_indices_of(value, list_to_search):
    results = list()
    for i, list_value in enumerate(list_to_search):
        if type(value) is list:
            if list_value in value:
                results.append(i)
        else:
            if list_value == value:
                results.append(i)
    return results


def multi_index(list_to_index, indices):
    return [element for i, element in enumerate(list_to_index) if i in indices]


wb_sector_map = {
    "000081": "Climate change",
    "000811": "Climate mitigation",
    "000812": "Climate adaptation"
}

country_map = {
    "AF": "Afghanistan",
    "AX": "Åland Islands",
    "AL": "Albania",
    "DZ": "Algeria",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas (the)",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BB": "Barbados",
    "BY": "Belarus",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BO": "Bolivia (Plurinational State of)",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BA": "Bosnia and Herzegovina",
    "BW": "Botswana",
    "BV": "Bouvet Island",
    "BR": "Brazil",
    "IO": "British Indian Ocean Territory (the)",
    "BN": "Brunei Darussalam",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "CV": "Cabo Verde",
    "KY": "Cayman Islands (the)",
    "CF": "Central African Republic (the)",
    "TD": "Chad",
    "CL": "Chile",
    "CN": "China",
    "CX": "Christmas Island",
    "CC": "Cocos (Keeling) Islands (the)",
    "CO": "Colombia",
    "KM": "Comoros (the)",
    "CG": "Congo (the)",
    "CD": "Congo (the Democratic Republic of the)",
    "CK": "Cook Islands (the)",
    "CR": "Costa Rica",
    "CI": "Côte d'Ivoire",
    "HR": "Croatia",
    "CU": "Cuba",
    "CW": "Curaçao",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic (the)",
    "EC": "Ecuador",
    "EG": "Egypt",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "ET": "Ethiopia",
    "FK": "Falkland Islands (the) [Malvinas]",
    "FO": "Faroe Islands (the)",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GF": "French Guiana",
    "PF": "French Polynesia",
    "TF": "French Southern Territories (the)",
    "GA": "Gabon",
    "GM": "Gambia (the)",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GR": "Greece",
    "GL": "Greenland",
    "GD": "Grenada",
    "GP": "Guadeloupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GG": "Guernsey",
    "GN": "Guinea",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "HM": "Heard Island and McDonald Islands",
    "VA": "Holy See (the)",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "ID": "Indonesia",
    "IR": "Iran (Islamic Republic of)",
    "IQ": "Iraq",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JE": "Jersey",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "KP": "Korea (the Democratic People's Republic of)",
    "KR": "Korea (the Republic of)",
    "XK": "Kosovo",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Lao People's Democratic Republic (the)",
    "LV": "Latvia",
    "LB": "Lebanon",
    "LS": "Lesotho",
    "LR": "Liberia",
    "LY": "Libya",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macao",
    "MK": "North Macedonia",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands (the)",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "YT": "Mayotte",
    "MX": "Mexico",
    "FM": "Micronesia (Federated States of)",
    "MD": "Moldova (the Republic of)",
    "MC": "Monaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MS": "Montserrat",
    "MA": "Morocco",
    "MZ": "Mozambique",
    "MM": "Myanmar",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NL": "Netherlands (the)",
    "AN": "NETHERLAND ANTILLES",
    "NC": "New Caledonia",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger (the)",
    "NG": "Nigeria",
    "NU": "Niue",
    "NF": "Norfolk Island",
    "MP": "Northern Mariana Islands (the)",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PS": "Palestine, State of",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines (the)",
    "PN": "Pitcairn",
    "PL": "Poland",
    "PT": "Portugal",
    "PR": "Puerto Rico",
    "QA": "Qatar",
    "RE": "Réunion",
    "RO": "Romania",
    "RU": "Russian Federation (the)",
    "RW": "Rwanda",
    "BL": "Saint Barthélemy",
    "SH": "Saint Helena, Ascension and Tristan da Cunha",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "MF": "Saint Martin (French part)",
    "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SX": "Sint Maarten (Dutch part)",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SB": "Solomon Islands",
    "SO": "Somalia",
    "ZA": "South Africa",
    "GS": "South Georgia and the South Sandwich Islands",
    "SS": "South Sudan",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SD": "Sudan (the)",
    "SR": "Suriname",
    "SJ": "Svalbard and Jan Mayen",
    "SZ": "Eswatini",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SY": "Syrian Arab Republic (the)",
    "TW": "Taiwan (Province of China)",
    "TJ": "Tajikistan",
    "TZ": "Tanzania, the United Republic of",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TN": "Tunisia",
    "TR": "Türkiye",
    "TM": "Turkmenistan",
    "TC": "Turks and Caicos Islands (the)",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates (the)",
    "GB": "United Kingdom of Great Britain and Northern Ireland (the)",
    "US": "United States of America (the)",
    "UM": "United States Minor Outlying Islands (the)",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela (Bolivarian Republic of)",
    "VN": "Viet Nam",
    "VG": "Virgin Islands (British)",
    "VI": "Virgin Islands (U.S.)",
    "WF": "Wallis and Futuna",
    "EH": "Western Sahara",
    "YE": "Yemen",
    "ZM": "Zambia",
    "ZW": "Zimbabwe",
}


transaction_type_map = {
    '3': 'Disbursement',
    '4': 'Expenditure',
}


finance_type_map = {
    "1": "GNI: Gross National Income",
    "110": "Standard grant",
    "1100": "Guarantees/insurance",
    "111": "Subsidies to national private investors",
    "2": "ODA % GNI",
    "210": "Interest subsidy",
    "211": "Interest subsidy to national private exporters",
    "3": "Total Flows % GNI",
    "310": "Capital subscription on deposit basis",
    "311": "Capital subscription on encashment basis",
    "4": "Population",
    "410": "Aid loan excluding debt reorganisation",
    "411": "Investment-related loan to developing countries",
    "412": "Loan in a joint venture with the recipient",
    "413": "Loan to national private investor",
    "414": "Loan to national private exporter",
    "421": "Standard loan",
    "422": "Reimbursable grant",
    "423": "Bonds",
    "424": "Asset-backed securities",
    "425": "Other debt securities",
    "431": "Subordinated loan",
    "432": "Preferred equity",
    "433": "Other hybrid instruments",
    "451": "Non-banks guaranteed export credits",
    "452": "Non-banks non-guaranteed portions of guaranteed export credits",
    "453": "Bank export credits",
    "510": "Common equity",
    "511": "Acquisition of equity not part of joint venture in developing countries",
    "512": "Other acquisition of equity",
    "520": "Shares in collective investment vehicles",
    "530": "Reinvested earnings",
    "610": "Debt forgiveness: ODA claims (P)",
    "611": "Debt forgiveness: ODA claims (I)",
    "612": "Debt forgiveness: OOF claims (P)",
    "613": "Debt forgiveness: OOF claims (I)",
    "614": "Debt forgiveness: Private claims (P)",
    "615": "Debt forgiveness: Private claims (I)",
    "616": "Debt forgiveness: OOF claims (DSR)",
    "617": "Debt forgiveness: Private claims (DSR)",
    "618": "Debt forgiveness: Other",
    "620": "Debt rescheduling: ODA claims (P)",
    "621": "Debt rescheduling: ODA claims (I)",
    "622": "Debt rescheduling: OOF claims (P)",
    "623": "Debt rescheduling: OOF claims (I)",
    "624": "Debt rescheduling: Private claims (P)",
    "625": "Debt rescheduling: Private claims (I)",
    "626": "Debt rescheduling: OOF claims (DSR)",
    "627": "Debt rescheduling: Private claims (DSR)",
    "630": "Debt rescheduling: OOF claim (DSR – original loan principal)",
    "631": "Debt rescheduling: OOF claim (DSR – original loan interest)",
    "632": "Debt rescheduling: Private claim (DSR – original loan principal)",
    "633": "Debt forgiveness/conversion: export credit claims (P)",
    "634": "Debt forgiveness/conversion: export credit claims (I)",
    "635": "Debt forgiveness: export credit claims (DSR)",
    "636": "Debt rescheduling: export credit claims (P)",
    "637": "Debt rescheduling: export credit claims (I)",
    "638": "Debt rescheduling: export credit claims (DSR)",
    "639": "Debt rescheduling: export credit claim (DSR – original loan principal)",
    "710": "Foreign direct investment, new capital outflow (includes reinvested earnings if separate identification not available)",
    "711": "Other foreign direct investment, including reinvested earnings",
    "712": "Foreign direct investment, reinvested earnings",
    "810": "Bank bonds",
    "811": "Non-bank bonds",
    "910": "Other bank securities/claims",
    "911": "Other non-bank securities/claims",
    "912": "Purchase of securities from issuing agencies",
    "913": "Securities and other instruments originally issued by multilateral agencies",
}


def main():
    # Use the IATI Datastore API to fetch all titles for a given publisher
    rows = 1000
    next_cursor_mark = '*'
    current_cursor_mark = ''
    results = []
    with progressbar.ProgressBar(max_value=1) as bar:
        while next_cursor_mark != current_cursor_mark:
            url = (
                'https://api.iatistandard.org/datastore/transaction/select'
                '?q=(reporting_org_ref:"44000" AND '
                'transaction_transaction_type_code:("3" OR "4") AND '
                'sector_code:("000081" OR "000811" OR "000812"))'
                '&sort=id asc'
                '&wt=json&fl=iati_identifier,title_narrative,'
                'sector_code,sector_percentage,sector_vocabulary,'
                'recipient_country_code,recipient_country_percentage,'
                'transaction_value,transaction_transaction_date_iso_date,transaction_transaction_type_code,'
                'transaction_finance_type_code'
                '&rows={}&cursorMark={}'
            ).format(rows, next_cursor_mark)
            api_json_str = requests.get(url, headers={'Ocp-Apim-Subscription-Key': API_KEY}).content
            api_content = json.loads(api_json_str)
            if bar.max_value == 1:
                bar.max_value = api_content['response']['numFound']
            transactions = api_content['response']['docs']
            len_results = len(transactions)
            current_cursor_mark = next_cursor_mark
            next_cursor_mark = api_content['nextCursorMark']
            for transaction_number, transaction in enumerate(transactions):
                transaction_type_code = transaction['transaction_transaction_type_code'][0]
                transaction_finance_type_code = transaction['transaction_finance_type_code'][0]
                transaction_dict = dict()
                transaction_dict['iati_identifier'] = transaction['iati_identifier']
                transaction_dict['transaction_number'] = transaction_number
                transaction_dict['title'] = transaction['title_narrative'][0]
                transaction_dict['date'] = transaction['transaction_transaction_date_iso_date'][0]
                transaction_dict['transaction_type'] = transaction_type_map[transaction_type_code]
                transaction_dict['finance_type'] = finance_type_map[transaction_finance_type_code]
                transaction_value = float(transaction['transaction_value'][0])
                transaction_dict['original_transaction_value'] = transaction_value
                reporting_org_v2_indices = find_all_indices_of('98', transaction['sector_vocabulary'])
                reporting_org_sector_codes = multi_index(transaction['sector_code'], reporting_org_v2_indices)
                reporting_org_sector_percentages = multi_index(transaction['sector_percentage'], reporting_org_v2_indices)
                sector_relevant = False
                for wb_sector in wb_sector_map.keys():
                    if wb_sector in reporting_org_sector_codes:
                        sector_relevant = True
                        break
                recipient_relevant = False
                for recipient in country_map.keys():
                    if 'recipient_country_code' in transaction.keys() and recipient in transaction['recipient_country_code']:
                        recipient_relevant = True
                        break
                if not (sector_relevant and recipient_relevant):
                    continue
                wb_sector_indices = find_all_indices_of(list(wb_sector_map.keys()), reporting_org_sector_codes)
                recipient_indices = find_all_indices_of(list(country_map.keys()), transaction['recipient_country_code'])
                for wb_sector_index in wb_sector_indices:
                    for recipient_index in recipient_indices:
                        split_dict = transaction_dict.copy()
                        wb_sector_code = reporting_org_sector_codes[wb_sector_index]
                        split_dict['wb_sector_name'] = wb_sector_map[wb_sector_code]
                        wb_sector_percentage = float(reporting_org_sector_percentages[wb_sector_index]) / 100
                        split_dict['wb_sector_percentage'] = reporting_org_sector_percentages[wb_sector_index]
                        au_recipient_code = transaction['recipient_country_code'][recipient_index]
                        split_dict['recipient_name'] = country_map[au_recipient_code]
                        au_recipient_percentage = float(transaction['recipient_country_percentage'][recipient_index]) / 100
                        split_dict['recipient_percentage'] = transaction['recipient_country_percentage'][recipient_index]
                        split_dict['split_transaction_value'] = transaction_value * wb_sector_percentage * au_recipient_percentage
                        results.append(split_dict)
            if bar.value + len_results <= bar.max_value:
                bar.update(bar.value + len_results)
    
    # Collate into Pandas dataframe
    df = pd.DataFrame.from_records(results)

    # Write to disk
    df.to_csv(
        os.path.join('input', 'world_bank_climate.csv'),
        index=False,
    )


if __name__ == '__main__':
    main()