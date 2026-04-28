% fig04_read_energy_vs_node.m
% Read Dynamic Energy vs. Process Node — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

nodes = [180, 130, 90, 65, 45, 32, 22];   % nm
x = 1:numel(nodes);                        % equal-spacing display positions
node_labels = {'180 nm','130 nm','90 nm','65 nm','45 nm','32 nm','22 nm'};

energy_2D_SRAM  = [1.995, 1.057, 0.483, 0.266, 0.174, 0.123, 0.035];
energy_3D_SRAM  = [1.021, 0.542, 0.249, 0.138, 0.133, 0.090, 0.027];
energy_2D_eDRAM = [1.152, 0.359, 0.330, 0.098, 0.117, 0.066, 0.019];
energy_3D_eDRAM = [0.527, 0.282, 0.392, 0.207, 0.103, 0.061, 0.022];

figure('Position', [100 100 700 500]);

plot(x, energy_2D_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(x, energy_3D_SRAM,  '-s', 'Color', [1.000 0.498 0.055], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, energy_2D_eDRAM, '-^', 'Color', [0.173 0.627 0.173], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, energy_3D_eDRAM, '-d', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XTick', x, 'XTickLabel', node_labels, 'FontSize', 11);
xlim([0.5 numel(nodes)+0.5]);
xlabel('Process Node', 'FontSize', 13);
ylabel('Read Dynamic Energy (nJ/access)', 'FontSize', 13);
title('Read Dynamic Energy vs. Process Node', 'FontSize', 14, 'FontWeight', 'bold');
legend('2D SRAM', '3D SRAM (2-die)', '2D eDRAM', '3D eDRAM (2-die)', ...
       'Location', 'northeast', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', '..', 'plots', 'regular_node_sweep', 'fig04_read_energy_vs_node.jpg'));
