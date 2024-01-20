clc
clear
close all

r1 = 3; %cm
theta1 = 0;
r2 = 0.3; %cm
theta2 = 2*pi-pi/2;
r_outer = 3.25;

preload = 1; %cm
M = 1.5; %kg
alpha = 75;
d_bushing = 5; %mm
displacement = (r1 - r2)/100;
preload = preload + d_bushing/2/10;
equi_dia = (displacement / pi)/(theta2 / (2*pi)); %pinion diameter m
tau = 2.65; %N-m
xf = displacement + (preload/100);
xi = preload/100;
k_max = tau/(equi_dia/2)/xf; %N/m
k_spring = k_max/2; %N/m

k_spring_imp = k_spring/4.448/39.37 %lbf/in
k_spring_m = k_spring_imp/25.4 %lbf/mm

h_max = (0.5*k_max*(xf^2-xi^2))/(9.81)/M;
h_max = h_max*100*sind(alpha) %cm
compression_max_mm = xf*1000
compression_max_in = compression_max_mm/25.4

b = r1;
m = (r2-r1)/(theta2-theta1);

syms theta

x = (m*theta+b)*cos(theta);
y = (m*theta+b)*sin(theta);

theta_cam = linspace(theta1,theta2,100);
theta_cam2 = linspace(theta2,2*pi,20);
x_cam = subs(x,theta,theta_cam);
x_cam = [x_cam, r2*cos(theta_cam2), r1];
y_cam = subs(y,theta,theta_cam);
y_cam = [y_cam, r2*sin(theta_cam2), 0];

xcircle = r_outer*cos(linspace(0,2*pi,100));
ycircle = r_outer*sin(linspace(0,2*pi,100));

figure
plot(xcircle,ycircle)
hold on
grid on
xlabel("cm")
ylabel("cm")
title("CAM profile")

plot(x_cam,y_cam)
axis square

r_cam = zeros(size(x_cam));
for i = 1:length(x_cam)
    r_cam(i) = norm([x_cam(i),y_cam(i)]);
end
thetacam = [theta_cam, theta_cam2, 2*pi];
figure()
plot(thetacam, r1-r_cam)
grid on
ylabel("Displacement [cm]")
xlabel("Angle [rad]")

