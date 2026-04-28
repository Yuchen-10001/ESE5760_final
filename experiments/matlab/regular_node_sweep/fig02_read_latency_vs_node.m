% fig02_read_latency_vs_node.m
% Read Latency (Cache Hit Latency) vs. Process Node — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

nodes = [180, 130, 90, 65, 45, 32, 22];   % nm
x = 1:numel(nodes);                        % equal-spacing display positions
node_labels = {'180 nm','130 nm','90 nm','65 nm','45 nm','32 nm','22 nm'};

lat_2D_SRAM  = [16.429, 10.311, 14.165, 9.942, 0.939, 1.061, 1.184];
lat_3D_SRAM  = [ 7.670,  5.401,  6.345, 4.698, 0.654, 0.633, 0.705];
lat_2D_eDRAM = [ 1.762,  2.907,  1.164, 2.488, 0.663, 0.757, 0.790];
lat_3D_eDRAM = [ 2.679,  1.915,  0.703, 0.538, 0.504, 0.472, 0.420];

figure('Position', [100 100 700 500]);

plot(x, lat_2D_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(x, lat_3D_SRAM,  '-s', 'Color', [1.000 0.498 0.055], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, lat_2D_eDRAM, '-^', 'Color', [0.173 0.627 0.173], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, lat_3D_eDRAM, '-d', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XTick', x, 'XTickLabel', node_labels, 'FontSize', 11);
xlim([0.5 numel(nodes)+0.5]);
xlabel('Process Node', 'FontSize', 13);
ylabel('Cache Hit Latency (ns)', 'FontSize', 13);
title('Read Latency vs. Process Node', 'FontSize', 14, 'FontWeight', 'bold');
legend('2D SRAM', '3D SRAM (2-die)', '2D eDRAM', '3D eDRAM (2-die)', ...
       'Location', 'northeast', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', '..', 'plots', 'regular_node_sweep', 'fig02_read_latency_vs_node.jpg'));
