% fig4_leakage_vs_node.m
% Total Leakage Power vs. Process Node — ESE5760 Final Project
% Data: DESTINY simulation, 2MB / 256-bit / Assoc=1 / LOP / 350K / WriteEDP

nodes = [65, 45, 32, 22];   % nm

leak_2D_SRAM  = [124.012,  48.328, 234.632,  65.837];
leak_3D_SRAM  = [145.831,  51.269, 234.632,  70.279];
leak_2D_eDRAM = [ 24.507,   9.986,  29.992,   9.799];
leak_3D_eDRAM = [107.014,  18.412,  50.137,  16.151];

figure('Position', [100 100 700 500]);

plot(nodes, leak_2D_SRAM,  '-o', 'Color', [0.122 0.467 0.706], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', '2D SRAM'); hold on;
plot(nodes, leak_3D_SRAM,  '-s', 'Color', [1.000 0.498 0.055], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', '3D SRAM (2-die)');
plot(nodes, leak_2D_eDRAM, '-^', 'Color', [0.173 0.627 0.173], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', '2D eDRAM');
plot(nodes, leak_3D_eDRAM, '-d', 'Color', [0.839 0.153 0.157], 'LineWidth', 2, 'MarkerSize', 8, 'DisplayName', '3D eDRAM (2-die)');

set(gca, 'XDir', 'reverse', 'XTick', nodes, 'XTickLabel', {'65nm','45nm','32nm','22nm'}, 'FontSize', 11);
xlim([18 70]);
xlabel('Process Node', 'FontSize', 12);
ylabel('Total Leakage Power (mW)', 'FontSize', 12);
title('Total Leakage Power vs. Process Node', 'FontSize', 13, 'FontWeight', 'bold');
legend('Location', 'northeast', 'FontSize', 10);
grid on;
box on;

print('-djpeg', '-r150', fullfile(fileparts(mfilename('fullpath')), '..', 'plots', 'fig4_leakage_vs_node.jpg'));
