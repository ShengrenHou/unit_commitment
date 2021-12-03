import pandas as pd
from pyomo.environ import *
# /input
chp_params= pd.read_csv('input/'+str('capacity_chp.csv'), index_col=0)
heat_plant_params=pd.read_csv('input/capacity_heat_plant.csv', index_col=0)
storage_params=pd.read_csv('input/capacity_store.csv',index_col=0)
chp_costs = pd.read_csv('input/cost_chp.csv', index_col=0)
heat_plant_costs = pd.read_csv('input/cost_heat_plant.csv', index_col=0)
# chp_params,heat_plant_params,storage_params,chp_costs,heat_plant_costs
gas= pd.read_csv('input/'+str('timeseries_gas.csv'), index_col=0)
demand= pd.read_csv('input/'+str('timeseries_heat_demand.csv'), index_col=0)
spot=pd.read_csv('input/'+str('timeseries_spot.csv'),index_col=0)

m=ConcreteModel()
m.t=RangeSet(1,24)
m.gas=Param(m.t,initialize=gas.value)#
m.spot=Param(m.t,initialize=spot.value)#
m.dem=Param(m.t,initialize=demand.value)# demand for each time step
# set index for all chp
m.chp=Set(initialize=chp_params.index)
m.heat_plant=Set(initialize=heat_plant_params.index)
m.storage=Set(initialize=storage_params.index)
#define variables
m.on_chp=Var(m.chp,m.t,within=Binary)
m.gas_generation_chp=Var(m.chp,m.t,domain=NonNegativeReals)
m.power_generation_chp=Var(m.chp,m.t,domain=NonNegativeReals)
m.heat_generation_chp=Var(m.chp,m.t,domain=NonNegativeReals)
def heat_max_chp_rule(m,j,t):
  return m.heat_generation_chp[j,t]<=chp_params.loc[j,'heat_max']*m.on_chp[j,t]
m.heat_max_chp_rule=Constraint(m.chp,m.t,rule=heat_max_chp_rule)
# min heat should no less than the heat min 
def heat_min_chp_rule(m,j,t):
  return m.heat_generation_chp[j,t]>=chp_params.loc[j,'heat_min']*m.on_chp[j,t]
m.heat_min_chp_rule=Constraint(m.chp,m.t,rule=heat_min_chp_rule)
# the relationship between power and heat generation could be simplied by a linear function.  
def heat_power_chp_rule(m,j,t):
  a= (chp_params.loc[j,'power_max']-chp_params.loc[j,'power_min'])/(chp_params.loc[j,'heat_max']-chp_params.loc[j,'heat_min'])
  b= (chp_params.loc[j,'power_min']-a*chp_params.loc[j,'heat_min'])
  return m.power_generation_chp[j,t]==a*m.heat_generation_chp[j,t]+b*m.on_chp[j,t]
m.heat_power_chp_constrain=Constraint(m.chp,m.t,rule=heat_power_chp_rule)

# def heat_power_chp(m, j, t):
#     """ power = a*heat + b*on """
#     a = (df_chp_param.loc[j, 'power_max']-df_chp_param.loc[j, 'power_min'])\
#         / (df_chp_param.loc[j, 'heat_max']-df_chp_param.loc[j, 'heat_min'])
#     b = df_chp_param.loc[j, 'power_min']-a*df_chp_param.loc[j, 'heat_min']
#     return m.gen_chp_power[j, t] == a*m.gen_chp_heat[j, t]+b*m.on_chp[j, t]
# m.heatpowerchp = Constraint(m.j_chp, m.t, rule=heat_power_chp)

# this defined the relation between gas comsumption and heat generation by a simple linear function
def heat_gas_chp_rule(m,j,t):
  a = (chp_params.loc[j, 'gas_max']-chp_params.loc[j, 'gas_min'])\
        / (chp_params.loc[j, 'heat_max']-chp_params.loc[j, 'heat_min'])
  b= chp_params.loc[j,'gas_min']-a*chp_params.loc[j,'heat_min']
  return m.gas_generation_chp[j,t]==a*m.heat_generation_chp[j,t]+b*m.on_chp[j,t]
m.heat_gas_chp_constrain=Constraint(m.chp,m.t,rule=heat_gas_chp_rule)
# def heat_gas_chp(m, j, t):
#     """ gas = a*heat + b*on """
#     a = (df_chp_param.loc[j, 'gas_max']-df_chp_param.loc[j, 'gas_min'])\
#         / (df_chp_param.loc[j, 'heat_max']-df_chp_param.loc[j, 'heat_min'])
#     b = df_chp_param.loc[j, 'gas_min']-a*df_chp_param.loc[j, 'heat_min']
#     return m.gen_chp_gas[j, t] == a*m.gen_chp_heat[j, t]+b*m.on_chp[j, t]
# m.heatgasrchp = Constraint(m.j_chp, m.t, rule=heat_gas_chp)
m.on_heat_plant=Var(m.heat_plant,m.t,within=Binary)
m.gas_generation_heat_plant=Var(m.heat_plant,m.t,within=NonNegativeReals)
# m.heat_generation_heat_plant=Var(m.heat_plant,m.t,within=NonNegativeReals)

# def heat_max_heat_plant(m,j,t):
#   return heat_generation_heat_plant[j,t]<=heat_plant_params.loc['heat_max']*m.on_heat_plant[j,t]
# m.heat_max_heat_plant_rule=Constraint(m.heat_plant,m.t,rule=heat_max_heat_plant)

# def heat_min_heat_plant_rule(m,j,t):

#   return heat_generation_heat_plant[j,t]>=heat_plant_params.loc['heat_min']*m.on_heat_plant[j,t]
# m.heat_min_heat_plant_rule= Constraint(m.heat_plant,m.t,rule=heat_min_heat_plant_rule)

# def heat_gas_heat_plant_rule(m,j,t):
#   '''the relationship of gas consumption and heat generated'''
#   a=(heat_plant_params.loc[j,'gas_max']-heat_plant_params.loc[j,'gas_min'])/(heat_plant_params.loc[j,'heat_max']-(heat_plant_params.loc[j,'heat_min']))
#   b = heat_plant_params.loc[j, 'gas_min']-a*heat_plant_params.loc[j, 'heat_min']

#   return m.gas_generation_heat_plant[j,t]==a*m.heat_generation_heat_plant+b*m.on_heat_plant[j,t]
# m.heat_gas_heat_plant_rule=Constraint(m.heat_plant,m.t,rule=heat_gas_heat_plant_rule)
# ## define variables and constraints for heat plant
# m.on_heat_plant=Var(m.heat_plant,m.t,within=Binary)
# m.gas_generation_heat_plant=Var(m.heat_plant,m.t,within=NonNegativeReals)
# m.heat_generation_heat_plant=Var(m.heat_plant,m.t,within=NonNegativeReals)

# def heat_max_heat_plant_rule(m,j,t):
#   return heat_generation_heat_plant[j,t]<=heat_plant_params.loc['heat_max']*m.on_heat_plant[j,t]
# m.heat_max_heat_plant_rule=Constraint(m.heat_plant,m.t,rule=heat_max_heat_plant_rule)

# def heat_min_heat_plant_rule(m,j,t):
#   return heat_generation_heat_plant[j,t]>=heat_plant_params.loc['heat_min']*m.on_heat_plant[j,t]
# m.heat_min_heat_plant_rule= Constraint(m.heat_plant,m.t,rule=heat_min_heat_plant_rule)

# def heat_gas_heat_plant_rule(m,j,t):
#   '''the relationship of gas consumption and heat generated'''
#   a=(heat_plant_params.loc[j,'gas_max']-heat_plant_params.loc[j,'gas_min'])/(heat_plant_params.loc[j,'heat_max']-(heat_plant_params.loc[j,'heat_min']))
#   b = heat_plant_params.loc[j, 'gas_min']-a*heat_plant_params.loc[j, 'heat_min']

#   return m.gas_generation_heat_plant[j,t]==a*m.heat_generation_heat_plant+b*m.on_heat_plant[j,t]
# m.heat_gas_heat_plant_rule=Constraint(m.heat_plant,m.t,rule=heat_gas_heat_plant_rule)
## set storage varaibles 
m.on_charge_storage=Var(m.storage,m.t,within=Binary)
m.on_discharge_storage=Var(m.storage,m.t,within=Binary)
m.storage_charge=Var(m.storage,m.t,within=NonNegativeReals)
m.storage_discharge=Var(m.storage,m.t,within=NonNegativeReals)
m.storage_capacity=Var(m.storage,m.t,domain=NonNegativeReals)
# set storage constraints 
def charge_storage_rule(m,j,t):
  return m.storage_charge[j,t]<=storage_params.loc[j,'charge']*m.on_charge_storage[j,t]
m.charge_storage_rule=Constraint(m.storage,m.t,rule=charge_storage_rule)

def discharge_storage_rule(m,j,t):
  if t==m.t.first():
    return m.on_discharge_storage[j,t]==0
  return m.storage_discharge[j,t]<=storage_params.loc[j,'discharge']*m.on_discharge_storage[j,t]
m.discharge_storage_rule=Constraint(m.storage,m.t,rule=discharge_storage_rule)

def capacity_max_storage_rule(m,j,t):
  return m.storage_capacity[j,t]<=storage_params.loc[j,'capacity']
m.capacity_max_storage_rule=Constraint(m.storage,m.t,rule=capacity_max_storage_rule)
# how to update capacity after charge or discharge. More imortantly,
# initialize the first state
def capacity_update_rule(m,j,t):
  '''capacity update based on discharge and charge'''
  if t==m.t.first():
    return m.storage_capacity[j,t]==0
  else:
    return m.storage_capacity[j,t]==m.storage_capacity[j,t-1]+m.storage_charge[j,t]-m.storage_discharge[j,t]
m.capacity_update_rule=Constraint(m.storage,m.t,rule=capacity_update_rule)

def logic_charge_discharge_rule(m,j,t):
  return m.on_charge_storage[j,t]+m.on_discharge_storage[j,t]<=1
m.logic_charge_discharge_rule=Constraint(m.storage,m.t,rule=logic_charge_discharge_rule)