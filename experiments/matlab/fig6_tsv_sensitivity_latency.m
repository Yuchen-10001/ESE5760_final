% fig6_tsv_sensitivity_latency.m
% TSV Parameter Sensitivity — Read Latency (3D SRAM @ 32nm) — ESE5760 Final Project
% Baseline: LocalTSVProjection=0, GlobalTSVProjection=0, TSVRedundancy=1.0
% One parameter swept at a time

% --- LocalTSVProjection sweep (values 0, 1, 2) ---
local_x   = [0, 1, 2];
local_lat = [0.633, 0.633, 0.633];

% --- GlobalTSVProjection sweep (values 0, 1, 2) ---
global_x   = [0, 1, 2];
global_lat = [0.633, 0.633, 0.633];

% --- TSVRedundancy sweep (values 1.0, 1.2, 1.5) ---
redund_x   = [1.0, 1.2, 1.5];
redund_lat = [0.633, 0.633, 0.633];

figure('Position', [100 100 750 520]);

subplot(1,2,1);
plot(local_x,  local_lat,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', 'LocalTSVProjection'); hold on;
plot(global_x, global_lat, '-s', 'Color', [1.000 0.498 0.055], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', 'GlobalTSVProjection');
set(gca, 'XTick', [0 1 2], 'FontSize', 10);
xlim([-0.2 2.2]);
ylim([0.60 0.68]);
xlabel('TSV Projection Level (0=aggressive, 2=conservative)', 'FontSize', 10);
ylabel('Read Latency (ns)', 'FontSize', 11);
title('LocalTSV & GlobalTSV Sweep', 'FontSize', 11, 'FontWeight', 'bold');
legend('Location', 'northeast', 'FontSize', 9);
grid on; box on;

subplot(1,2,2);
plot(redund_x, redund_lat, '-^', 'Color', [0.173 0.627 0.173], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', 'TSVRedundancy');
set(gca, 'XTick', [1.0 1.2 1.5], 'FontSize', 10);
xlim([0.95 1.6]);
ylim([0.60 0.68]);
xlabel('TSV Redundancy Factor', 'FontSize', 11);
ylabel('Read Latency (ns)', 'FontSize', 11);
title('TSVRedundancy Sweep', 'FontSize', 11, 'FontWeight', 'bold');
legend('Location', 'northeast', 'FontSize', 9);
grid on; box on;

sgtitle('TSV Sensitivity — Read Latency (3D SRAM @ 32nm)', 'FontSize', 13, 'FontWeight', 'bold');

print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', 'plots', 'fig6_tsv_sensitivity_latency.jpg'));
