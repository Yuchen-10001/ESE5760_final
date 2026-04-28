% node_sweep_equal_spacing_template.m
% Template for process-node sweep figures in this project.
%
% Plotting convention:
%   1. Keep nodes in physical order from older/larger to newer/smaller.
%   2. Use equal-spaced x positions instead of raw nm values.
%      This prevents 180->130 from looking much wider than 32->22.
%   3. Keep the x-axis tick labels as real process nodes.
%   4. Use the same colors/markers as fig01-fig06.
%   5. Save figures under experiments/plots/regular_node_sweep.
%
% To create a new figure:
%   - Copy this file to figXX_metric_vs_node.m.
%   - Replace metric_* arrays, ylabel_text, title_text, and output_name.

nodes = [180, 130, 90, 65, 45, 32, 22];   % real process nodes, nm
x = 1:numel(nodes);                        % equal-spacing display positions
node_labels = {'180 nm','130 nm','90 nm','65 nm','45 nm','32 nm','22 nm'};

% Replace these example arrays with the metric values from results.csv.
metric_2D_SRAM  = [0, 0, 0, 0, 0, 0, 0];
metric_3D_SRAM  = [0, 0, 0, 0, 0, 0, 0];
metric_2D_eDRAM = [0, 0, 0, 0, 0, 0, 0];
metric_3D_eDRAM = [0, 0, 0, 0, 0, 0, 0];

ylabel_text = 'Metric Unit';
title_text = 'Metric vs. Process Node';
output_name = 'figXX_metric_vs_node.jpg';

figure('Position', [100 100 700 500]);

plot(x, metric_2D_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(x, metric_3D_SRAM,  '-s', 'Color', [1.000 0.498 0.055], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, metric_2D_eDRAM, '-^', 'Color', [0.173 0.627 0.173], 'LineWidth', 2, 'MarkerSize', 8);
plot(x, metric_3D_eDRAM, '-d', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8);

set(gca, 'XTick', x, 'XTickLabel', node_labels, 'FontSize', 11);
xlim([0.5 numel(nodes)+0.5]);
xlabel('Process Node', 'FontSize', 13);
ylabel(ylabel_text, 'FontSize', 13);
title(title_text, 'FontSize', 14, 'FontWeight', 'bold');
legend('2D SRAM', '3D SRAM (2-die)', '2D eDRAM', '3D eDRAM (2-die)', ...
       'Location', 'northeast', 'FontSize', 11);
grid on;
box on;

drawnow;
set(gcf, 'Renderer', 'painters');
print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', '..', 'plots', 'regular_node_sweep', output_name));
