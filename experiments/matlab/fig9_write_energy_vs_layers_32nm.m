% fig9_write_energy_vs_layers_32nm.m
% Write Dynamic Energy vs. Layer Count @ 32nm — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

layers = [1, 2, 4, 8, 16];

write_energy_SRAM  = [0.123, 0.089, 0.126, 0.338, 1.369];
write_energy_eDRAM = [0.066, 0.061, 0.108, 0.339, 1.370];

figure('Position', [100 100 700 500]);

plot(layers, write_energy_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(layers, write_energy_eDRAM, '-s', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XScale', 'log', 'YScale', 'log', 'XTick', layers, 'XTickLabel', {'1','2','4','8','16'}, 'FontSize', 11);
xlim([1 16]);
xlabel('Layer Count', 'FontSize', 13);
ylabel('Write Dynamic Energy (nJ/access)', 'FontSize', 13);
title('Write Dynamic Energy vs. Layer Count @ 32 nm', 'FontSize', 14, 'FontWeight', 'bold');
legend('SRAM', 'eDRAM', 'Location', 'northwest', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', 'plots', 'fig9_write_energy_vs_layers_32nm.jpg'));
