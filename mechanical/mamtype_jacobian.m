clc
clear all
close
%%joint distance
L1 = 2; %cm
L2 = 4; %cm
L3 = 4; %cm

%% chasis estimation
m = 5/2.205; %5lbs
F_0 = [0;0;m*9.81/2];

syms theta1 theta2 theta3

t0H1 = [cos(theta1) -sin(theta1) 0 0;
        sin(theta1)  cos(theta1) 0 0;
             0            0      1 0;
             0            0      0 1];
 
t1H2 = [1      0            0      L1;
        0 cos(theta2) -sin(theta2)  0;
        0 sin(theta2)  cos(theta2)  0;
        0      0            0       1];

t2H3 = [1      0            0       0;
        0 cos(theta3) -sin(theta3)  0;
        0 sin(theta3)  cos(theta3) L2;
        0      0            0       1];

t3He = [1 0 0  0;
        0 1 0  0;
        0 0 1 L3;
        0 0 0  1];

t0He = t0H1*t1H2*t2H3*t3He;
thetae = t0He(1:3,1:3);
rho = t0He(1:3,4);
J = jacobian(rho,[theta1, theta2, theta3]);
J_T = J.';
int = 9;

for i = 0:int
t1 = (0*i/int)/180*pi;
t2 = (90*i/int)/180*pi;
t3 = (180*(int-i)/int)/180*pi;
M = subs(J_T,{theta1, theta2, theta3},{t1, t2, t3});
M = double(inv(M));

F_e = double(subs(thetae,{theta1, theta2, theta3},{t1, t2, t3}))*F_0;
tau = M*F_e;
tau1(i+1) = tau(1);
tau2(i+1) = tau(2);
tau3(i+1) = tau(3);
A = double(subs(t0He,{theta1, theta2, theta3},{t1, t2, t3}));
end
x = 1:int+1;
plot(x,tau1,x,tau2,x,tau3)
legend("tau1","tau2","tau3")
ylabel("Torque kg*cm")
grid on
