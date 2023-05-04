
data{

  int y_1_1; //number of concurrent 1s
  int y_0_1; //number of 0,1 occurences
  int y_1_0; //number of 1,0 occurences
  int y_0_0; //number of concurrent 0s
  

}
parameters{
  real<lower=-1, upper=1> rho;
  real<lower=0, upper=1> q;
}
transformed parameters{
  real<lower=0, upper=1> prob_1_1 = q + rho*(1-q);
  real<lower=0, upper=1> prob_0_1 = (1-q)*(1-rho);
  real<lower=0, upper=1> prob_1_0 = q*(1-rho);
  real<lower=0, upper=1> prob_0_0 = 1 - q + rho*q;
}
model{
  q ~ beta(1, 1);
  target += y_1_1 * bernoulli_lpmf(1| prob_1_1);
  target += y_0_1 * bernoulli_lpmf(1| prob_0_1);
  target += y_1_0 * bernoulli_lpmf(1| prob_1_0);
  target += y_0_0 * bernoulli_lpmf(1| prob_0_0);
  
}
