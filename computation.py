import yaml
import numpy as np
import pandas as pd



# Read master customer data file YAML
def read_data(file_name):
    with open(file_name) as file:
        customers_data = yaml.safe_load(file)
    return customers_data



# SUPPORTED DISTRIBUTIONS
def Gaussian_Dist(mean, stddev):
    return np.random.normal(loc=mean, scale=stddev)

def Beta_Dist(a, b):
    return np.random.beta(a, b)

def Lognormal_Dist(log_mean, sigma):
    return np.random.lognormal(mean=log_mean, sigma=sigma)

all_distributions = {'Gaussian': Gaussian_Dist,
                     'Beta': Beta_Dist, 
                     'Lognormal': Lognormal_Dist}



# GET CUSTOMER PROBABILITY FROM CUSTOMER DATA
def get_customer_probability(customers_data, customer):
    if(customer == 'All' or customer == ''):
        customers_propability = np.array([])
        for cus in list(customers_data.keys())[1:]:
            customers_propability = np.append(customers_propability, customers_data[cus]['probability'])
        
    else:
        customers_propability = np.zeros(len(list(customers_data.keys())[1:]))
        idx = list(customers_data.keys())[1:].index(customer)
        customers_propability[idx] = 1
    
    customers_propability = customers_propability/np.sum(customers_propability)
    return customers_propability



# GET TYPE PROBABILITY FROM SPECIFIC CUSTOMER
def get_type_prob(customers_data, customer):
    type_propability = np.array([])
    for type in list(customers_data[customer].keys())[:-1]:
        type_propability = np.append(type_propability, customers_data[customer][type]['probability'])
    
    type_propability = type_propability/np.sum(type_propability)
    return type_propability



# FUNCTION TO COMPUTE LP
def computed_LP(mileage, SOCe, t0, Tf, Pm, E0, Pch0, eta, mode):
    LP = np.zeros(2880)

    Em = mileage * Pm
    Em_m = Em*60
    E0_m = E0*60000
    Tf_m = Tf*60

    Pch   = Pch0*eta/100
    Pch_m = Pch*1000
    t0_m  = t0*60

    if (mode == 1):                 # final SOC
        Ech = Em_m
        Tch = Ech/Pch_m
        np.ceil(Tch).astype(int)
        T = t0_m + Tch
        Tch = np.ceil(Tch)
        T = np.ceil(T)

    else:
        SOCi = (SOCe/100 - Em_m/E0_m)
        Ech = (1 - SOCi)*E0_m
        Tch = Ech/Pch_m
        if (Tf_m > Tch):
            T = t0_m + Tch
        else:
            T = t0_m + Tf
        Tch = np.ceil(Tch)
        T = np.ceil(T)

    LP[t0_m: int(np.ceil(T))] = Pch_m

    return LP, Tch, T



# FUNCTION TO COMPUTE TOTAL LP
def compute_total_LP(all_distributions, customers_data, customer):
    Vehicle_database = pd.read_csv('data.csv')

    all_custormers = list(customers_data.keys())[1:]
    customers_propability = get_customer_probability(customers_data, customer)
    
    N = customers_data['Number_of_sample']

    # load profile initialization
    Load_profile = []
    Total_LP = np.zeros(2880)

    for i in range(N):
        # Sample from customers
        cust = np.random.choice(all_custormers, 1, p=customers_propability)
        cust_data = customers_data[cust[0]]

        # discrete disttribution of customer's vehicle
        V = list(cust_data.keys())[0:-1]

        # probability = cust_data['Probability']
        probability = get_type_prob(customers_data, cust[0])

        Vehicle = np.random.choice(V, 1, p=probability)
        cust_vehicle_data = cust_data[Vehicle[0]]
        
        # read the distribution
        dist_mileage = cust_vehicle_data['mileage']
        dist_SOC     = cust_vehicle_data['SOC']
        dist_t0      = cust_vehicle_data['t0']
        dist_Tf      = cust_vehicle_data['Tf']
        mode         = cust_vehicle_data['mode']

        # sample from distribution        
        mileage = int(all_distributions[dist_mileage['Distribution']](**dist_mileage['Parameters']))
        SOC     = int(all_distributions[dist_SOC['Distribution']](**dist_SOC['Parameters']))
        t0      = int(all_distributions[dist_t0['Distribution']](**dist_t0['Parameters']))
        Tf      = int(all_distributions[dist_Tf['Distribution']](**dist_Tf['Parameters']))

        # vehicle parameters
        Pm = Vehicle_database.loc[Vehicle_database["Name"] == Vehicle[0], "Power consumption (Wh/km)"].values[0]
        E0 = Vehicle_database.loc[Vehicle_database["Name"] == Vehicle[0], "Battery capacity(kWh)"].values[0]
        Pch0 = Vehicle_database.loc[Vehicle_database["Name"] == Vehicle[0], "Charging power (kW)"].values[0]
        eta = 100

        # load profile calculation (single vehicle)
        Lp, Tch, T = computed_LP(mileage, SOC, t0, Tf, Pm, E0, Pch0, eta, mode)
        Load_profile.append(Lp)

        # Total load profile accumulation
        Total_LP = np.add(Total_LP, Load_profile[i])

    return Total_LP