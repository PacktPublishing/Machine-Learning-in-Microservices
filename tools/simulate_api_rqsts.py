import sys, requests, os, asyncio, aiohttp, datetime, time, random

build_no = "0.1"
usage_help = """
        Usage:
            simulate_api_rqsts --version | --help | <rate> <url list file> [-r] [-v]
            
        Where:
            --version: Shows the current release/build version
            
            --help: shows this message
            
            rate: API call simulate requests rate measured in requests per minute
            
            url list file: Is the text file with a list of all target URLs where the API calls will be sent to
                 Have each target URL in a separate line
            
            -r: Specify a randomly paced rate. If omitted, a uniformly paced rate will be used.
                
                The uniformly paced requests are paced out so that the time between each API call is always the same,
                so if we are configuring a uniformly paced load of 600 API requests/min, simulate_api_rqsts
                will send 1 API call every T = 100 ms.
                
                In the randomly-paced case, each API call is sent after a random period, TR, from the time where
                the previous call was sent, but so that TR can never be larger or smaller than 95% of T. So if we are
                configuring a randomly-paced load of 600 API requests/min, TR, in that case, will be equal to a value
                greater than 5 ms and smaller than 195 ms.
                simulate_api_rqsts will send 1 API call every:
                (1-95%)T <= TR <= (1+95%)T (i.e., for 600 requests/min: 5 ms <= TR <= 195 ms)
                The sum of all TRs, however, will still be approximately equal to the configured requests/min. In our
                example here, the load is 600 API requests/min.
                Uniformly paced requests are better when you are manually analyzing how a particular microservice
                responds to the API load, while randomly paced requests are a better representation of a real-time
                production API request load.
                
            -v: Verbose mode
"""

#Initialize Configuration Params
REQ_TIMEOUT = 2
variable_reqs = '-r' in sys.argv
verbose = '-v' in sys.argv
reqs_rate = 0

async def get(url, session):
    try:
        async with session.get(url=url, timeout=REQ_TIMEOUT) as response:
            resp = await response.read()

    except Exception as e:
        pass

async def main(urls):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(url, session) for url in urls])

        
        
# Function to get a list of random delays for every minute
def get_1min_delays(reqs_rate):
    if not reqs_rate:
        return []
    
    t = 60 / reqs_rate
    reqs_rate_min = t * 0.05
    reqs_rate_max = t * 1.95

    # calculate the random Tr list size based on worse case scenario of, all Tr List element are equal to reqs_rate_min. There will be a break anyway to avoid too many items in the list
    tr_list = []
    tr_list_size = int(round(60 /reqs_rate_min ,0))
    total_Tr = 0

    for i in range(1, tr_list_size):
        Tr = round(random.uniform(reqs_rate_min, reqs_rate_max), 2)
        tr_list.append(Tr)
        total_Tr = total_Tr + Tr
        if total_Tr >= 60:
            break;
        
    return tr_list



show_version_output = "\nsimulate_api_rqsts ver. %s\n" % build_no

if len(sys.argv) > 1:
    if '--help' in sys.argv:
        print(show_version_output)
        print(usage_help)
        sys.exit(0)

    if '--version' in sys.argv:
        print(show_version_output)
        sys.exit(0)
        
    reqs_rate = sys.argv[1]
    if reqs_rate.isnumeric():
        reqs_rate = int(reqs_rate)
        if reqs_rate<=0:
            print("ERROR: API Calls Rate needs to be a number > 0")
            sys.exit(-1)

        url_list = []
        if len(sys.argv) > 2:
            url_list_file = open(sys.argv[2], "r")
            for url in url_list_file:
                url_list.append(url)
            
    else:
        print("ERROR: API Calls Rate needs to be an integer")
        sys.exit(-1)
        
            
else:
    print("ERROR: Missing parameters")
    print(show_version_output)
    print(usage_help)
    sys.exit(-1)
    
           
# Assume the default of a uniformly paced requests
# Calculate T, the frequency of the API calls
sleep_time = 60 / reqs_rate

tr_list_len = 0
if variable_reqs:
    tr_list = get_1min_delays(reqs_rate)
    tr_list_len = len(tr_list)

    
if verbose:
    print("Simulating API calls to the URL List:")
    print(url_list)

n = 1
i = 0
while True:
    if verbose:
        print("HTTP Req... #"+ str(n))
        n = n+1
    
    asyncio.run(main(url_list))
        
    if variable_reqs and tr_list_len>0:
        time.sleep(tr_list[i])                        
        i = i+1
        # If all random generated delays are processed, regenerate a new 1-min list of delays
        if i>=tr_list_len:
            i=0
            tr_list = get_1min_delays(reqs_rate)         
    else:
        time.sleep(sleep_time)
