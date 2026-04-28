% fig12_layer_sweep_leakage_power_32nm.m
% Leakage Power vs. Layer Count @ 32nm — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

layers = [1, 2, 4, 8, 16];

leakage_SRAM  = [234.632, 234.632, 285.915, 386.048, 471.264];
leakage_eDRAM = [29.992, 50.137, 132.416, 352.322, 348.162];

figure('Position', [100 100 700 500]);

plot(layers, leakage_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(layers, leakage_eDRAM, '-s', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XScale', 'log', 'XTick', layers, 'XTickLabel', {'1','2','4','8','16'}, 'FontSize', 11);
xlim([1 16]);
xlabel('Layer Count', 'FontSize', 13);
ylabel('Leakage Power (mW)', 'FontSize', 13);
title('Leakage Power vs. Layer Count @ 32 nm', 'FontSize', 14, 'FontWeight', 'bold');
legend('SRAM', 'eDRAM', 'Location', 'northwest', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', '..', 'plots', 'exploratory_sweeps', 'fig12_layer_sweep_leakage_power_32nm.jpg'));
