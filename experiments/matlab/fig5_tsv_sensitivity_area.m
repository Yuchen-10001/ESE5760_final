% fig5_tsv_sensitivity_area.m
% TSV Parameter Sensitivity — Total Area (3D SRAM @ 32nm) — ESE5760 Final Project
% Baseline: LocalTSVProjection=0, GlobalTSVProjection=0, TSVRedundancy=1.0
% One parameter swept at a time; x-axis = parameter index (0,1,2)

% --- LocalTSVProjection sweep (values 0, 1, 2) ---
local_x    = [0, 1, 2];
local_area = [2.132, 2.250, 2.139];

% --- GlobalTSVProjection sweep (values 0, 1, 2) ---
global_x    = [0, 1, 2];
global_area = [2.132, 2.149, 2.133];

% --- TSVRedundancy sweep (values 1.0, 1.2, 1.5) ---
redund_x    = [1.0, 1.2, 1.5];
redund_area = [2.132, 2.132, 2.133];

figure('Position', [100 100 750 520]);

subplot(1,2,1);   % LocalTSV and GlobalTSV share integer x-axis 0-2
plot(local_x,  local_area,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', 'LocalTSVProjection'); hold on;
plot(global_x, global_area, '-s', 'Color', [1.000 0.498 0.055], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', 'GlobalTSVProjection');
set(gca, 'XTick', [0 1 2], 'FontSize', 10);
xlim([-0.2 2.2]);
xlabel('TSV Projection Level (0=aggressive, 2=conservative)', 'FontSize', 10);
ylabel('Total Area (mm^2)', 'FontSize', 11);
title('LocalTSV & GlobalTSV Sweep', 'FontSize', 11, 'FontWeight', 'bold');
legend('Location', 'northwest', 'FontSize', 9);
grid on; box on;

subplot(1,2,2);   % TSVRedundancy sweep
plot(redund_x, redund_area, '-^', 'Color', [0.173 0.627 0.173], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', 'TSVRedundancy');
set(gca, 'XTick', [1.0 1.2 1.5], 'FontSize', 10);
xlim([0.95 1.6]);
xlabel('TSV Redundancy Factor', 'FontSize', 11);
ylabel('Total Area (mm^2)', 'FontSize', 11);
title('TSVRedundancy Sweep', 'FontSize', 11, 'FontWeight', 'bold');
legend('Location', 'northwest', 'FontSize', 9);
grid on; box on;

sgtitle('TSV Sensitivity — Total Area (3D SRAM @ 32nm)', 'FontSize', 13, 'FontWeight', 'bold');

print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', 'plots', 'fig5_tsv_sensitivity_area.jpg'));
