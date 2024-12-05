# sim_energy_system_cap.py
#
# Usage:  python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s
#  Simulation for a capacitor-based energy system
# Parameters:
#  sa_m2: solar cell surface area in meter^2
#  eff: solar cell efficiency
#  voc: solar array open circuit voltage
#  c_f: energy buffer capacitance in Farads
#  r_esr: capacitor effective series resistance
#  q0_c: initial charge of capacitor in Coulombs
#  p_on_w: power draw during operation Watts
#  v_thresh: voltage threshold for power off in Volts
#  dt_s: simulation time step in seconds
#  dur_s: simulation duration in seconds
# Output:
#  Writes a time and voltage pair in a csv file 
#

# Written by Evan Schlein
# Other contributors: Brad Denby

# import Python modules
import math  # math module
import sys  # argv
import csv

# constants
irr_w_m2 = 1366.1


# initialize script arguments
sa_m2 = float('nan') #  solar cell surface area in meter^2
eff = float('nan') #  solar cell efficiency
voc = float('nan') #  solar array open circuit voltage
c_f = float('nan') #  energy buffer capacitance in Farads
r_esr = float('nan') #  capacitor effective series resistance
q0_c = float('nan') #  initial charge of capacitor in Coulombs
p_on_w = float('nan') #  power draw during operation Watts
v_thresh = float('nan') #  voltage threshold for power off in Volts
dt_s = float('nan') #  simulation time step in seconds
dur_s = float('nan') #  simulation duration in seconds

# helper functions
def calc_solar_current(irr_w_m2, sa_m2, eff, voc):
    return irr_w_m2*sa_m2*eff/voc

def calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w):
    return (qt_c/c_f + i1_a*r_esr)**2 - 4*p_mode_w*r_esr

def calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr):
    return (qt_c/c_f + i1_a*r_esr + math.sqrt(node_discr))/2

# parse script arguments
if len(sys.argv) == 11:
    sa_m2 = float(sys.argv[1])
    eff = float(sys.argv[2])
    voc = float(sys.argv[3])
    c_f = float(sys.argv[4])
    r_esr = float(sys.argv[5])
    q0_c = float(sys.argv[6])
    p_on_w = float(sys.argv[7])
    v_thresh = float(sys.argv[8])
    dt_s = float(sys.argv[9])
    dur_s = float(sys.argv[10])
else:
    print(
        'Usage: python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s'
    )
    exit()

# write script below this line
    
# Set initial values:
isc_a = calc_solar_current(irr_w_m2, sa_m2, eff, voc)
i1_a = isc_a
qt_c = q0_c
p_mode_w = p_on_w
t_s = 0.0
log = []

# Calculate initial node discriminant:
node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
if(node_discr < 0.0):
    p_mode_w = 0.0
    node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)

# Calculate initial node voltage:
node_v = calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr)

# Solar cell cannot produce current at high voltage:
if voc<=node_v and i1_a!=0.0:
    i1_a = 0.0
# Energy consumers cannot operate at low voltage:
if node_v < v_thresh:
    p_mode_w = 0.0

# Initialize log with initial data
log = [[t_s,node_v]]

while log[-1][0]<dur_s:
    # Calculate the load current:
    i3_a = p_mode_w/node_v
    # Update charge:
    qt_c += (i1_a-i3_a)*dt_s
    if qt_c<0.0:
        qt_c = 0.0
    # Set solar array current:
    i1_a = isc_a if 0<=node_v<voc else 0

    # Power on after charging:
    if p_mode_w==0.0 and node_v>=voc:
        p_mode_w = p_on_w
        
    # Calculate initial node discriminant:
    node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
    if(node_discr<0.0):
        p_mode_w = 0.0
        node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
    node_v = calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr)
    if voc<=node_v and i1_a!=0.0:
        i1_a = 0.0
    if node_v<v_thresh:
        p_mode_w = 0.0
    # Append data and iterate t_s by dt_s    
    log.append([t_s,node_v])
    t_s += dt_s
    
# write to csv
with open('./log.csv',mode='w',newline='') as outfile:
  csvwriter = csv.writer(outfile)
  csvwriter.writerow(\
   ['t_s','volts']\
  )
  for e in log:
    csvwriter.writerow(e)