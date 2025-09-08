import sys
sys.path.insert(0, 'C:/Users/scopi/source/repos/PAGOS/PAGOS/src')

from pint import UnitRegistry, Context
from pagos.constants import MOLAR_MASSES, MOLAR_VOLUMES
from pagos.water import calc_dens
import re

u = UnitRegistry()

# define units that distinguish beween gas and water phases
u.define('gram_gas = [mass_gas] = g_gas')
u.define('mole_gas = [amount_gas] = mol_gas')
u.define('meter_cubed_STP_gas = [STPvolume_gas] = m3STP_gas')
u.define('gram_water = [mass_water] = g_water')
u.define('mole_water = [amount_water] = mol_water')
u.define('meter_cubed_water = [volume_water] = m3_water')

# Make physicochemical context with conversion between grams and moles of substance
pc = Context('physicochemical', ('pc'), defaults={'gas': None, 'T': None, 'S': None})
# gas phase transformations
pc.add_transformation('[amount_gas]', '[mass_gas]', lambda ureg, n, gas, T, S:n * u.Quantity(MOLAR_MASSES[gas], u.g_gas/u.mol_gas))
pc.add_transformation('[mass_gas]', '[amount_gas]', lambda ureg, m, gas, T, S:m / u.Quantity(MOLAR_MASSES[gas], u.g_gas/u.mol_gas))
pc.add_transformation('[amount_gas]', '[STPvolume_gas]', lambda ureg, n, gas, T, S:n * u.Quantity(MOLAR_VOLUMES[gas], u.cm3STP_gas/u.mol_gas))
pc.add_transformation('[STPvolume_gas]', '[amount_gas]', lambda ureg, v, gas, T, S:v / u.Quantity(MOLAR_VOLUMES[gas], u.cm3STP_gas/u.mol_gas))
# water phase transformations
pc.add_transformation('[amount_water]', '[mass_water]', lambda ureg, n, gas, T, S:n * u.Quantity(18.0153, u.g_water/u.mol_water))
pc.add_transformation('[mass_water]', '[amount_water]', lambda ureg, m, gas, T, S:m / u.Quantity(18.0153, u.g_water/u.mol_water))
pc.add_transformation('[mass_water]', '[volume_water]', lambda ureg, m, gas, T, S:m / (calc_dens(T, S, magnitude=True) * u.kg_water/u.m3_water))
pc.add_transformation('[volume_water]', '[mass_water]', lambda ureg, v, gas, T, S:v * calc_dens(T, S, magnitude=True) * u.kg_water/u.m3_water)
# inverted transformations so that units ^-1 can be handled
# gas phase inverse transformations
pc.add_transformation('[amount_gas]^-1', '[mass_gas]^-1', lambda ureg, n, gas, T, S: n / u.Quantity(MOLAR_MASSES[gas], u.g_gas/u.mol_gas))
pc.add_transformation('[mass_gas]^-1', '[amount_gas]^-1', lambda ureg, m, gas, T, S: m * u.Quantity(MOLAR_MASSES[gas], u.g_gas/u.mol_gas))
pc.add_transformation('[amount_gas]^-1', '[STPvolume_gas]^-1', lambda ureg, n, gas, T, S: n / u.Quantity(MOLAR_VOLUMES[gas], u.cm3STP_gas/u.mol_gas))
pc.add_transformation('[STPvolume_gas]^-1', '[amount_gas]^-1', lambda ureg, v, gas, T, S: v * u.Quantity(MOLAR_VOLUMES[gas], u.cm3STP_gas/u.mol_gas))
# water phase inverse  transformations
pc.add_transformation('[amount_water]^-1', '[mass_water]^-1', lambda ureg, n, gas, T, S: n / u.Quantity(18.0153, u.g_water/u.mol_water))
pc.add_transformation('[mass_water]^-1', '[amount_water]^-1', lambda ureg, m, gas, T, S: m * u.Quantity(18.0153, u.g_water/u.mol_water))
pc.add_transformation('[mass_water]^-1', '[volume_water]^-1', lambda ureg, m, gas, T, S: m * (calc_dens(T, S, magnitude=True) * u.kg_water/u.m3_water))
pc.add_transformation('[volume_water]^-1', '[mass_water]^-1', lambda ureg, v, gas, T, S: v / (calc_dens(T, S, magnitude=True) * u.kg_water/u.m3_water))

u.add_context(pc)
u.enable_contexts('physicochemical')

# Test with single dimensions of mass or amount of gas and water:
M_gas = u.Quantity(10, 'g_gas')
N_gas = u.Quantity(1.51e-5, 'mol_gas')
M_water = u.Quantity(1, 'kg_water')
N_water = u.Quantity(18, 'mol_water')
C_Ar = N_gas / M_water


print(C_Ar)
print('equals')
print(C_Ar.to('g_gas/g_water', gas='Ar'))
print(C_Ar.to('cm3STP_gas/g_water', gas='Ar'))
print(C_Ar.to('mol_gas/kg_water', gas='Ar'))
print(C_Ar.to('g_gas/cm3_water', gas='Ar', T=10, S=20))
print(C_Ar.to('g_gas/cm3_water', gas='Ar', T=10, S=20))

print((N_gas**2).to('g_gas**2', gas='Ar'))
