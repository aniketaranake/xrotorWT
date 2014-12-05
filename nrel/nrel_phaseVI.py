import numpy as np, pylab as py
from xrotorWT import *

airspeeds = np.array([7.,10.,15.,20.,25])
thrust    = np.zeros(airspeeds.shape)
torque    = np.zeros(airspeeds.shape)

for j,airspeed in enumerate(airspeeds):
  rotor = Rotor('nrelPhaseVI_v%3.2f'%airspeed)
  rotor.airspeed = airspeed
  
  rotor.run_rotor(72.)
  thrust[j] = rotor.performance['thrust']
  torque[j] = rotor.performance['torque']

thrust_exp = [1188.416016,1805.560303,2754.355713,3531.849365,4424.200195]
torque_exp = [822.479187,1431.653931,1622.347534,1219.413940,1497.689331]


py.figure()
py.subplot(2,1,1)
py.plot(airspeeds,thrust,'b.-')
py.plot(airspeeds,thrust_exp,'ks')
py.subplot(2,1,2)
py.plot(airspeeds,torque,'b.-')
py.plot(airspeeds,torque_exp,'ks')
py.show()
