% fig03_write_latency_vs_node.m
% Write Latency (Cache Write Latency) vs. Process Node — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

nodes = [180, 130, 90, 65, 45, 32, 22];   % nm
x = 1:numel(nodes);                        % equal-spacing display positions
node_labels = {'180 nm','130 nm','90 nm','65 nm','45 nm','32 nm','22 nm'};

lat_2D_SRAM  = [11.758, 7.623, 10.088, 7.213, 0.526, 0.605, 0.710];
lat_3D_SRAM  = [ 5.951, 4.321,  4.939, 3.740, 0.367, 0.423, 0.447];
lat_2D_eDRAM = [ 1.277, 1.846,  0.965, 1.550, 0.453, 0.607, 0.579];
lat_3D_eDRAM = [ 1.757, 1.303,  0.439, 0.347, 0.273, 0.340, 0.281];

figure('Position', [100 100 700 500]);

plot(x, lat_2D_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(x, lat_3D_SRAM,  '-s', 'Color', [1.000 0.498 0.055], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, lat_2D_eDRAM, '-^', 'Color', [0.173 0.627 0.173], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, lat_3D_eDRAM, '-d', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XTick', x, 'XTickLabel', node_labels, 'FontSize', 11);
xlim([0.5 numel(nodes)+0.5]);
xlabel('Process Node', 'FontSize', 13);
ylabel('Cache Write Latency (ns)', 'FontSize', 13);
title('Write Latency vs. Process Node', 'FontSize', 14, 'FontWeight', 'bold');
legend('2D SRAM', '3D SRAM (2-die)', '2D eDRAM', '3D eDRAM (2-die)', ...
       'Location', 'northeast', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', '..', 'plots', 'regular_node_sweep', 'fig03_write_latency_vs_node.jpg'));
