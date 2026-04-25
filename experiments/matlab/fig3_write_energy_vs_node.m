% fig3_write_energy_vs_node.m
% Write Dynamic Energy vs. Process Node — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

nodes = [65, 45, 32, 22];   % nm

energy_2D_SRAM  = [0.022, 0.173, 0.123, 0.035];
energy_3D_SRAM  = [0.037, 0.132, 0.089, 0.027];
energy_2D_eDRAM = [0.092, 0.117, 0.066, 0.019];
energy_3D_eDRAM = [0.206, 0.102, 0.061, 0.021];

figure('Position', [100 100 700 500]);

plot(nodes, energy_2D_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(nodes, energy_3D_SRAM,  '-s', 'Color', [1.000 0.498 0.055], 'LineWidth', 2, 'MarkerSize', 8);
plot(nodes, energy_2D_eDRAM, '-^', 'Color', [0.173 0.627 0.173], 'LineWidth', 2, 'MarkerSize', 8);
plot(nodes, energy_3D_eDRAM, '-d', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XDir', 'reverse', 'XTick', nodes, 'XTickLabel', {'65 nm','45 nm','32 nm','22 nm'}, 'FontSize', 11);
xlim([18 70]);
xlabel('Process Node', 'FontSize', 13);
ylabel('Write Dynamic Energy (nJ/access)', 'FontSize', 13);
title('Write Dynamic Energy vs. Process Node', 'FontSize', 14, 'FontWeight', 'bold');
legend('2D SRAM', '3D SRAM (2-die)', '2D eDRAM', '3D eDRAM (2-die)', ...
       'Location', 'northeast', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', 'plots', 'fig3_write_energy_vs_node.jpg'));
