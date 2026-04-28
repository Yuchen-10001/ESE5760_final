% fig01_total_area_vs_node.m
% Total Area vs. Process Node — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

nodes = [180, 130, 90, 65, 45, 32, 22];   % nm
x = 1:numel(nodes);                        % equal-spacing display positions
node_labels = {'180 nm','130 nm','90 nm','65 nm','45 nm','32 nm','22 nm'};

area_2D_SRAM  = [94.721, 49.407, 23.680, 12.348, 8.893, 4.262, 1.836];
area_3D_SRAM  = [47.988, 25.035, 12.002,  7.105, 5.245, 2.132, 0.969];
area_2D_eDRAM = [38.646, 23.844, 11.789,  5.957, 4.555, 1.440, 0.630];
area_3D_eDRAM = [22.978, 12.001, 14.848,  7.743, 3.125, 1.068, 0.550];

figure('Position', [100 100 700 500]);

plot(x, area_2D_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(x, area_3D_SRAM,  '-s', 'Color', [1.000 0.498 0.055], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, area_2D_eDRAM, '-^', 'Color', [0.173 0.627 0.173], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, area_3D_eDRAM, '-d', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XTick', x, 'XTickLabel', node_labels, 'FontSize', 11);
xlim([0.5 numel(nodes)+0.5]);
xlabel('Process Node', 'FontSize', 13);
ylabel('Total Area (mm^2)', 'FontSize', 13);
title('Total Area vs. Process Node', 'FontSize', 14, 'FontWeight', 'bold');
legend('2D SRAM', '3D SRAM (2-die)', '2D eDRAM', '3D eDRAM (2-die)', ...
       'Location', 'northeast', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', '..', 'plots', 'regular_node_sweep', 'fig01_total_area_vs_node.jpg'));
