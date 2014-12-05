# Main case file
import os
import numpy as np
from xrotorWT import *
from math import pi

class Rotor():
  '''Rotor object. '''
  
  def __init__(self,casename):
    '''Initialize rotor'''

    # Need a unique filename for each rotor. If filename is taken, append with underscores
    self.datfilename = casename+".dat"
    while os.path.isfile(self.datfilename):
      casename += "_"
      self.datfilename = casename+".dat"
    self.casename = casename

    # Initialize to NREL Phase VI inputs
    self.nrel_init()

  def run_rotor(self,inputval,input_is='rpm'):

    if input_is=='rpm':
      self.rpm = inputval
    else:
      print "Only RPM input implemented so far! Need to complete Rotor.py for additional functionality"
      exit(1)

    # Write xrotor input file        
    with open(self.inpfilename,'w') as inpfile:
      w  = lambda string_line : inpfile.write(string_line+"\n")
      wf = lambda float_line  : inpfile.write("%21.12f\n"%float_line)
      wd = lambda int_line  : inpfile.write("%d\n"%int_line)

      # Airfoil properties
      w('AERO')
      w('EDIT')
      w('1')
      wf(self.airfoil.alpha_zero_lift)
      w('4')
      wf(self.airfoil.clmax)
      w('5')
      wf(self.airfoil.clmin)
      w('7')
      wf(self.airfoil.cdmin)
      w('8')
      wf(self.airfoil.cl_at_cdmin)
      w('')
      w('')

      # Arbitrary rotor
      w('ARBI')
      wd(self.nblades)
      wf(self.airspeed)
      wf(self.radius)
      wf(self.hubr)
      # Stations
      wd(self.nstations)
      for j in range(self.nstations):
        w('%21.12e '*3%(self.r_R[j],self.c_R[j],self.twist[j]))
      w('n')

      # Run prop
      w('OPER')
      w('RPM')
      wf(self.rpm)
      w('WRIT '+self.datfilename) 
      w('')

      # Clean exit (hopefully!)
      w('QUIT')

    # Now that the input file is written, run xrotor
    os.system('xrotor < %s > %s 2>&1'%(self.inpfilename,self.outfilename))

    # Post process
    self.process_dat()

  def process_dat(self):
    '''Routine to post process xrotor .dat output.'''

    # Performance quantities will be stored in this dictionary
    self.performance = {}

    # Read output file        
    with open(self.datfilename,'r') as f:
      # Skip the header
      for j in range(3):
        f.readline()
      
      line4 = f.readline()
      # Check if xrotor converged
      if line4.find('NOT CONVERGED')>-1:
        self.converged = False
        self.bad_rotor()
        return
        
      self.converged = True
      f.readline()
      
      # Fifth line has the relevant performance metrics
      line5 = f.readline()
      splt  = line5.split()
      self.performance['thrust'] = -float(splt[2])
      self.performance['power']  = -float(splt[5])
      self.performance['torque'] = -float(splt[7])

      # Compute coefficients using wind turbine convention
      thrust_norm = 0.5*self.rho*self.airspeed**2*pi*self.radius**2    # N
      power_norm  = thrust_norm * self.airspeed
      torque_norm = thrust_norm * self.radius
      self.performance['CT'] = self.performance['thrust']/thrust_norm
      self.performance['CP'] = self.performance['power' ]/power_norm
      self.performance['CQ'] = self.performance['torque']/torque_norm

      return

  def bad_rotor(self):
    '''Convenience method. Declares that rotor is infinitely bad. Useful if (when) unconverged cases occur during optimization'''
    self.performance['thrust'] = float('Inf')
    self.performance['CT'    ] = float('Inf')
    self.performance['power' ] = -float('Inf')
    self.performance['CP'    ] = -float('Inf')

  def nrel_init(self):
    '''Settings for NREL Phase VI rotor'''

    # STDIN and STDOUT for xrotor
    self.inpfilename = self.casename+".inp"
    self.outfilename = self.casename+".out"

    # Default values for xrotor inputs
    self.nblades       = 2
    self.radius        = 5.029                       # m 
    self.hubr          = 1.0/self.radius             # m
    self.airspeed      = 7.                          # m/s
    self.rpm           = 72.
    self.rho           = 1.226

    # Airfoil stations (Initialize to NREL Phase VI)
    self.r_R, self.c_R, self.twist, self.airfoil = get_nrel_stations()

    self.nstations = len(self.r_R)
