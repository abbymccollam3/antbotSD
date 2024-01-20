%% init params
lb_kg = 0.453592;
in_m = 0.0254;
m = 3; % robot mass, lb
mu_s = 0.6; % static friction coefficient, gravel and wheel
M = 0.25; % wheel mass, lb
R = 3; % wheel radius, inches
a = 0.1; % linear acceleration, m^2/s
g = 9.81; % gravity, m/s^2
m = m * lb_kg;
M = M * lb_kg;
R = R * in_m;

%% drive motor torque
% approach 1
torque_1 = R / 2 * (m * a + mu_s * m * g); % N-m
fprintf('Required torque (approach 1): %.3f kgf-cm\n', torque_1 * 100 / 10);

% approach 2
inertia = 1 / 2 * M * R^2;
torque_2 = R / 2 * (M * a + mu_s * m * g); % N-m
fprintf('Required torque (approach 2): %.3f kgf-cm\n', torque_2 * 100 / 10);

% approach 3
% https://engineering.stackexchange.com/questions/31501/how-can-i-calculate-the-power-and-torque-required-for-the-motor-on-a-wheeled-rob
mu_roll = 0.2;
N = 1; % gear ratio (v_in / v_out)
n = 2; % # motors engaged with ground
eta_drive = 0.8; % drivetrain efficiency
eta_motor = 0.7; % motor efficiency
v = 1; % desired max speed (m/s)
t = 2; % time desired to reach max speed (s)
a = v / t; % desired acceleration
theta = 10; % incline angle (deg)
w_v = m * g; % vehicle weight (N)
w_v_perp = w_v * cosd(theta);

f_roll = w_v_perp * mu_roll;
f_incline = w_v * sind(theta);
f_a = m * a;

omega = v / R;
rps = omega / (2 * pi);
rpm = rps * 60;

torque_roll = f_roll * R;
torque_incline = f_incline * R;
torque_accel = f_a * R;
torque_const = torque_roll + torque_incline;
torque_wheel = torque_const + torque_accel;
torque_motors = 1 / eta_drive * (torque_wheel / N);
torque_motor = torque_motors / n;
torque_3 = torque_motor;
fprintf('Required torque (approach 3): %.3f kgf-cm\n', torque_3 * 100 / 10);

%% bolt calcs
% cap adapter - perpendicular

% cap adapter - axial
moment_arm = 4; % in, perependicular distance from wheel to bolt
M = m * moment_arm;
s_y = 60e3; % psi
syms d; % bolt diameter
iz = pi * d^4 / 64;
s_b = M * (d / 2) / iz;
d_min = solve(s_b == s_y, d);
d_min = d_min(1) * 2.54 * 10; % mm
fprintf('Min bolt dia: %.3f mm\n', d_min);
