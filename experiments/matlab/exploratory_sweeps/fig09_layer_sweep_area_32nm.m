% fig09_layer_sweep_area_32nm.m
% Total Area vs. Layer Count @ 32nm — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

layers = [1, 2, 4, 8, 16];

area_SRAM  = [4.262, 2.132, 1.542, 1.014, 0.620];
area_eDRAM = [1.440, 1.068, 0.927, 1.199, 0.618];

figure('Position', [100 100 700 500]);

plot(layers, area_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(layers, area_eDRAM, '-s', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XScale', 'log', 'XTick', layers, 'XTickLabel', {'1','2','4','8','16'}, 'FontSize', 11);
xlim([1 16]);
xlabel('Layer Count', 'FontSize', 13);
ylabel('Total Area (mm^2)', 'FontSize', 13);
title('Total Area vs. Layer Count @ 32 nm', 'FontSize', 14, 'FontWeight', 'bold');
legend('SRAM', 'eDRAM', 'Location', 'northeast', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', '..', 'plots', 'exploratory_sweeps', 'fig09_layer_sweep_area_32nm.jpg'));
