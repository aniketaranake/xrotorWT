class Airfoil():

  def __init__(self):

    # Initialized to S809 properties (Re~65k)
    self.alpha_zero_lift = -0.32307692307692
    self.clmax           = 1.02
    self.clmin           = -.84
    self.cdmin           = 0.0107
    self.cl_at_cdmin     = 0.3 
