from bs4 import BeautifulSoup
import re
import asyncio
import aiohttp
import ssl
import itertools

# unable to scrape bank links, all available banks from 'everydaybankbonus' is in this array
# we iterate over every link and grab all of its contents
# such as bank name, bonus amount, expiration, and information

urls = ['https://everybankbonus.com/bank/chase',
        'https://everybankbonus.com/bank/acorns'
        'https://everybankbonus.com/bank/midflorida_credit_union',
        'https://everybankbonus.com/bank/td_bank',
        'https://everybankbonus.com/bank/hometrust_bank',
        'https://everybankbonus.com/bank/associated_bank',
        'https://everybankbonus.com/bank/oneaz_credit_union',
        'https://everybankbonus.com/bank/alliant_credit_union',
        'https://everybankbonus.com/bank/fidelity_bank',
        'https://everybankbonus.com/bank/wells_fargo',
        'https://everybankbonus.com/bank/flushing_bank',
        'https://everybankbonus.com/bank/sterling_national_bank',
        'https://everybankbonus.com/bank/cape_cod_5_bank',
        'https://everybankbonus.com/bank/arizona_bank_and_trust',
        'https://everybankbonus.com/bank/bank-and-trust-htlf',
        'https://everybankbonus.com/bank/cibm_bank',
        'https://everybankbonus.com/bank/citywide_banks',
        'https://everybankbonus.com/bank/illinois_bank_trust',
        'https://everybankbonus.com/bank/minnesota_bank_and_trust',
        'https://everybankbonus.com/bank/nve_bank',
        'https://everybankbonus.com/bank/rocky_mountain_bank',
        'https://everybankbonus.com/bank/tbk_bank',
        'https://everybankbonus.com/bank/investors_bank', #this is where the code gets slow
        'https://everybankbonus.com/bank/allegent_community_federal_credit_union',
        'https://everybankbonus.com/bank/wintrust_community_bank',
        'https://everybankbonus.com/bank/clearview_federal_credit_union',
        'https://everybankbonus.com/bank/credit_union_1',
        'https://everybankbonus.com/bank/energy_one_federal_credit_union',
        'https://everybankbonus.com/bank/freestar_financial_credit_union',
        'https://everybankbonus.com/bank/hiway_fcu',
        'https://everybankbonus.com/bank/redstone-federal-credit-union',
        'https://everybankbonus.com/bank/old_national_bank',
        'https://everybankbonus.com/bank/laurel_road', #nurses can get bonuses
        'https://everybankbonus.com/bank/addition_financial_credit_union',
        'https://everybankbonus.com/bank/central_bank',
        'https://everybankbonus.com/bank/cn_bank',
        'https://everybankbonus.com/bank/first_national_bank',
        'https://everybankbonus.com/bank/first_national_bank_online',
        'https://everybankbonus.com/bank/georgias_own_cu',
        'https://everybankbonus.com/bank/hancock_whitney_bank',
        'https://everybankbonus.com/bank/peoplesbank',
        'https://everybankbonus.com/bank/equity_bank',
        'https://everybankbonus.com/bank/first_tech_federal_cu',
        'https://everybankbonus.com/bank/general_electric_cu',
        'https://everybankbonus.com/bank/gesa_cu',
        'https://everybankbonus.com/bank/inb_illinois_national_bank',
        'https://everybankbonus.com/bank/abington_bank',
        'https://everybankbonus.com/bank/alltru_credit_union',
        'https://everybankbonus.com/bank/american_express',
        'https://everybankbonus.com/bank/american_united_fcu',
        'https://everybankbonus.com/bank/bank_five_nine',
        'https://everybankbonus.com/bank/benchmark_fcu',
        'https://everybankbonus.com/bank/broadway_bank',
        'https://everybankbonus.com/bank/citadel_credit_union',
        'https://everybankbonus.com/bank/credit_union_west',
        'https://everybankbonus.com/bank/dollar_bank',
        'https://everybankbonus.com/bank/easthampton_savings_bank',
        'https://everybankbonus.com/bank/excite_credit_union',
        'https://everybankbonus.com/bank/financial_one_credit_union',
        'https://everybankbonus.com/bank/firstbank',
        'https://everybankbonus.com/bank/first_bank',
        'https://everybankbonus.com/bank/first_bank_virginia',
        'https://everybankbonus.com/bank/first_entertainment_cu',
        'https://everybankbonus.com/bank/fulton_bank',
        'https://everybankbonus.com/bank/harbor_one_bank',
        'https://everybankbonus.com/bank/inspire_federal_credit_union',
        'https://everybankbonus.com/bank/landmark_credit_union',
        'https://everybankbonus.com/bank/midfirst_bank',
        'https://everybankbonus.com/bank/neighborhood_credit_union',
        'https://everybankbonus.com/bank/new_mexico_bank_trust',
        'https://everybankbonus.com/bank/old_second_bank',
        'https://everybankbonus.com/bank/pathways_financial_credit_union',
        'https://everybankbonus.com/bank/pennsylvania_state_employee_credit_union',
        'https://everybankbonus.com/bank/peoples_bancorp',
        'https://everybankbonus.com/bank/premier_valley_bank',
        'https://everybankbonus.com/bank/provident_cu',
        'https://everybankbonus.com/bank/rocky_mountain_credit_union',
        'https://everybankbonus.com/bank/sf_fire_cu',
        'https://everybankbonus.com/bank/point_breeze_credit_union',
        'https://everybankbonus.com/bank/allegius_credit_union',
        'https://everybankbonus.com/bank/amalgamated_bank',
        'https://everybankbonus.com/bank/american_bank_and_trust',
        'https://everybankbonus.com/bank/ballston_spa_national_bank',
        'https://everybankbonus.com/bank/bankers_trust',
        'https://everybankbonus.com/bank/bank_of_texas',
        'https://everybankbonus.com/bank/commonwealth_cu',
        'https://everybankbonus.com/bank/cutx',
        'https://everybankbonus.com/bank/dedham_savings_bank',
        'https://everybankbonus.com/bank/gateway_first_bank',
        'https://everybankbonus.com/bank/home_federal_savings_bank',
        'https://everybankbonus.com/bank/honor_cu',
        'https://everybankbonus.com/bank/people_first_federal_credit_union',
        'https://everybankbonus.com/bank/rockland_trust_bank',
        'https://everybankbonus.com/bank/safe_credit_union',
        'https://everybankbonus.com/bank/trustone_financial_fcu',
        'https://everybankbonus.com/bank/wecu_credit_union',
        'https://everybankbonus.com/bank/royal_cu',
        'https://everybankbonus.com/bank/1st_united_credit_union',
        'https://everybankbonus.com/bank/andrews_fcu',
        'https://everybankbonus.com/bank/bankesb',
        'https://everybankbonus.com/bank/bankhometown',
        'https://everybankbonus.com/bank/banner_bank',
        'https://everybankbonus.com/bank/bar_harbor_bank_trust',
        'https://everybankbonus.com/bank/bmi_fcu',
        'https://everybankbonus.com/bank/christian_community_cu',
        'https://everybankbonus.com/bank/community_first_cu',
        'https://everybankbonus.com/bank/cornerstone_financial__cu',
        'https://everybankbonus.com/bank/country_bank',
        'https://everybankbonus.com/bank/darden_credit_union',
        'https://everybankbonus.com/bank/department_of_labor_fcu',
        'https://everybankbonus.com/bank/east_wisconsin_savings_bank',
        'https://everybankbonus.com/bank/fidelity_bank_pa',
        'https://everybankbonus.com/bank/first_commonwealth_bank',
        'https://everybankbonus.com/bank/first_financial_bank',
        'https://everybankbonus.com/bank/first_national_1870',
        'https://everybankbonus.com/bank/freedom_federal_credit_union',
        'https://everybankbonus.com/bank/keypoint_cu',
        'https://everybankbonus.com/bank/land_of_lincoln_credit_union',
        'https://everybankbonus.com/bank/macatawa_bank',
        'https://everybankbonus.com/bank/middlesex_savings_bank',
        'https://everybankbonus.com/bank/midhudson_valley_fcu',
        'https://everybankbonus.com/bank/mt_bank',
        'https://everybankbonus.com/bank/notre_dame_fcu',
        'https://everybankbonus.com/bank/pinnacle_financial_partners',
        'https://everybankbonus.com/bank/premier_bank',
        'https://everybankbonus.com/bank/river_bank',
        'https://everybankbonus.com/bank/simplicity_credit_union',
        'https://everybankbonus.com/bank/southland_cu',
        'https://everybankbonus.com/bank/south_state_bank',
        'https://everybankbonus.com/bank/sunflower_bank',
        'https://everybankbonus.com/bank/sunwest_credit_union',
        'https://everybankbonus.com/bank/thrivent_federal_credit_union',
        'https://everybankbonus.com/bank/transcend_credit_union',
        'https://everybankbonus.com/bank/united_community_bank',
        'https://everybankbonus.com/bank/valley_first_federal_credit_union',
        'https://everybankbonus.com/bank/citizens_equity_first_cu',
        'https://everybankbonus.com/bank/fcb_banks',
        'https://everybankbonus.com/bank/vystar_credit_union',
        'https://everybankbonus.com/bank/altra_federal_credit_union',
        'https://everybankbonus.com/bank/america_first_cu',
        'https://everybankbonus.com/bank/bhcu',
        'https://everybankbonus.com/bank/charter_oak_cu',
        'https://everybankbonus.com/bank/community_america_cu',
        'https://everybankbonus.com/bank/educational_employees_credit_union',
        'https://everybankbonus.com/bank/farm_bureau_bank',
        'https://everybankbonus.com/bank/first_savings_bank_hegewisch',
        'https://everybankbonus.com/bank/greater_nevada_cu',
        'https://everybankbonus.com/bank/holyoke_cu',
        'https://everybankbonus.com/bank/idaho_central_credit_union',
        'https://everybankbonus.com/bank/jovia_financial_credit_union',
        'https://everybankbonus.com/bank/lafayette_fcu',
        'https://everybankbonus.com/bank/middlesex_federal_savings',
        'https://everybankbonus.com/bank/nbt_bank',
        'https://everybankbonus.com/bank/newtown_savings_bank',
        'https://everybankbonus.com/bank/on_tap_credit_union',
        'https://everybankbonus.com/bank/republic_bank_of_chicago',
        'https://everybankbonus.com/bank/univest',
        'https://everybankbonus.com/bank/community_choice_credit_union',
        'https://everybankbonus.com/bank/community_cu_florida',
        'https://everybankbonus.com/bank/elite_community_credit_union',
        'https://everybankbonus.com/bank/diversified_members_credit_union',
        'https://everybankbonus.com/bank/exchange_bank',
        'https://everybankbonus.com/bank/1st_advantage_federal_credit_union',
        'https://everybankbonus.com/bank/achieva_credit_union',
        'https://everybankbonus.com/bank/advantis_credit_union',
        'https://everybankbonus.com/bank/a_plus_federal_credit_union',
        'https://everybankbonus.com/bank/americas_christian_credit_union',
        'https://everybankbonus.com/bank/bank_of_america',
        'https://everybankbonus.com/bank/bank_of_princeton',
        'https://everybankbonus.com/bank/bankplus',
        'https://everybankbonus.com/bank/bellco_cu',
        'https://everybankbonus.com/bank/brightstar_cu',
        'https://everybankbonus.com/bank/california_cu',
        'https://everybankbonus.com/bank/caped_credit_union',
        'https://everybankbonus.com/bank/compass_credit_union',
        'https://everybankbonus.com/bank/cport_cu',
        'https://everybankbonus.com/bank/deseret_first_cu',
        'https://everybankbonus.com/bank/dow_credit_union',
        'https://everybankbonus.com/bank/dundee_bank',
        'https://everybankbonus.com/bank/dutrac_cummunity_cu',
        'https://everybankbonus.com/bank/eastman_credit_union',
        'https://everybankbonus.com/bank/first_bank_and_trust_company',
        'https://everybankbonus.com/bank/first_community_bank',
        'https://everybankbonus.com/bank/first_community_cu_tx',
        'https://everybankbonus.com/bank/first_community_cu',
        'https://everybankbonus.com/bank/fort_bragg_federal_credit_union',
        'https://everybankbonus.com/bank/frontwave_credit_union',
        'https://everybankbonus.com/bank/great_river_federal_credit_union',
        'https://everybankbonus.com/bank/grow_financial_federal_credit_union',
        'https://everybankbonus.com/bank/illinois_state_credit_union',
        'https://everybankbonus.com/bank/independent_bank',
        'https://everybankbonus.com/bank/inroads_credit_union',
        'https://everybankbonus.com/bank/local_first_bank',
        'https://everybankbonus.com/bank/magnolia_federal_credit_union',
        'https://everybankbonus.com/bank/michigan_state_university_fcu',
        'https://everybankbonus.com/bank/mission_fcu',
        'https://everybankbonus.com/bank/mountain_america_credit_union',
        'https://everybankbonus.com/bank/navy_federal_cu',
        'https://everybankbonus.com/bank/north_island_credit_union',
        'https://everybankbonus.com/bank/northwest_bank',
        'https://everybankbonus.com/bank/oakland-university-credit-union',
        'https://everybankbonus.com/bank/orange_county_credit_union',
        'https://everybankbonus.com/bank/our_cu',
        'https://everybankbonus.com/bank/power_financial_cu',
        'https://everybankbonus.com/bank/profed_credit_union',
        'https://everybankbonus.com/bank/public_employees_cu',
        'https://everybankbonus.com/bank/public_service_credit_union',
        'https://everybankbonus.com/bank/purdue-federal-credit-union',
        'https://everybankbonus.com/bank/red_canoe_credit_union',
        'https://everybankbonus.com/bank/regions',
        'https://everybankbonus.com/bank/san_mateo_cu',
        'https://everybankbonus.com/bank/savings_bank_of_danbury',
        'https://everybankbonus.com/bank/savings_bank_of_walpole',
        'https://everybankbonus.com/bank/scient_federal_credit_union',
        'https://everybankbonus.com/bank/simmons_bank',
        'https://everybankbonus.com/bank/south_carolina_fcu',
        'https://everybankbonus.com/bank/spire_credit_union',
        'https://everybankbonus.com/bank/staley_cu',
        'https://everybankbonus.com/bank/stanford_fcu',
        'https://everybankbonus.com/bank/s_&_t_bank',
        'https://everybankbonus.com/bank/technology_cu',
        'https://everybankbonus.com/bank/the_county_federal_credit_union',
        'https://everybankbonus.com/bank/u$x_fcu',
        'https://everybankbonus.com/bank/vantage_west_credit_union',
        'https://everybankbonus.com/bank/wings_financial_cu',
        'https://everybankbonus.com/bank/waukesha_state_bank',
        'https://everybankbonus.com/bank/linn_area_cu',
        'https://everybankbonus.com/bank/sandy_spring_bank',
        'https://everybankbonus.com/bank/bank_of_washington',
        'https://everybankbonus.com/bank/community_bank_of_lawndale',
        'https://everybankbonus.com/bank/dane_county_cu',
        'https://everybankbonus.com/bank/first_american_bank',
        'https://everybankbonus.com/bank/first_citizens_federal_credit_union',
        'https://everybankbonus.com/bank/first_south_financial_cu',
        'https://everybankbonus.com/bank/hawaii_state_fcu',
        'https://everybankbonus.com/bank/patelco_credit_union',
        'https://everybankbonus.com/bank/spruce_mobile_banking',
        'https://everybankbonus.com/bank/summit_cu',
        'https://everybankbonus.com/bank/interior_fcu',
        'https://everybankbonus.com/bank/north_cascades_bank',
        'https://everybankbonus.com/bank/american_airlines_cu'
        # # 401 banks in this array
        # # worth $88,914
]
output = {}
bonus_amount = []

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Function to fetch the HTML content of a given URL asynchronously
async def fetch(url):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with session.get(url) as response:
            return await response.text()

# Function to process a single URL asynchronously
async def process_url(url):
    html = await fetch(url)
    soup = BeautifulSoup(html, 'html.parser')
    bank_name_chase = soup.select('h6.MuiTypography-root.jss57.MuiTypography-h6.MuiTypography-gutterBottom')
    expiration_date = soup.select('h6.MuiTypography-root.MuiTypography-h6.MuiTypography-gutterBottom')
    bank_information = soup.select('p.MuiTypography-root.jss58.MuiTypography-body1.MuiTypography-gutterBottom')

    # Extract bank information and expiration dates from the HTML content
    for bank_name, expiration, info in itertools.islice(zip(bank_name_chase, expiration_date, bank_information), None):
        if re.search(r'\$\d+', expiration.text):
            # output[bank_name.text] = {"Expiration": None, "Bank Information": None}
            continue
        else:
            expiration_text = expiration.text.strip() or "N/A"
            output[bank_name.text] = {"Expiration": expiration_text, "Bank Information": info.text}

        matches = re.findall(r'\(\$(\d+)\)', bank_name.text)
        bonus_amount.extend(int(match) for match in matches)

# Main function to process all the URLs
async def main():
    tasks = [process_url(url) for url in urls]
    await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

sorted_banks = sorted(output.items(), key=lambda x: x[0])  # Sort banks by name

result = []

# Prepare the final output in JSON format
for bank, details in sorted_banks:
    print("Bank: ", bank)
    print(f"Expiration: {details['Expiration']}")
    print(f"Bank Information: {details['Bank Information']}")
    print()

total_sum = sum(bonus_amount)
num_accounts = len(output)
print('We found:', num_accounts, "Bonuses")
print(f"Worth: ${total_sum:,}")


# # this is the json converter

#     bank = {
#         "Bank": bank,
#         "Expiration": details['Expiration'],
#         "Bank Information": details['Bank Information']
#     }
#     result.append(bank)

# total_sum = sum(bonus_amount)
# num_accounts = len(output)

# output_json = {
#     "Banks": result
# }

# # Print the final output as JSON
# print(json.dumps(output_json, indent=4))
# json_output = json.dumps(output_json, indent=4)

# # Print the generated JSON code
# print(json_output)
# print("Total number of accounts", num_accounts)
# print(f"Total bonus amount: ${total_sum:,}")
