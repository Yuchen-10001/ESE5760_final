% fig8_read_latency_vs_layers_32nm.m
% Read Latency vs. Layer Count @ 32nm — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

layers = [1, 2, 4, 8, 16];

read_latency_SRAM  = [1.061, 0.633, 0.488, 0.338, 0.244];
read_latency_eDRAM = [0.757, 0.472, 0.316, 0.337, 0.248];

figure('Position', [100 100 700 500]);

plot(layers, read_latency_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(layers, read_latency_eDRAM, '-s', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XScale', 'log', 'XTick', layers, 'XTickLabel', {'1','2','4','8','16'}, 'FontSize', 11);
xlim([1 16]);
xlabel('Layer Count', 'FontSize', 13);
ylabel('Read Latency (ns)', 'FontSize', 13);
title('Read Latency vs. Layer Count @ 32 nm', 'FontSize', 14, 'FontWeight', 'bold');
legend('SRAM', 'eDRAM', 'Location', 'northeast', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', 'plots', 'fig8_read_latency_vs_layers_32nm.jpg'));
