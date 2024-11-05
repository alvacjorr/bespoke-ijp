% Define the folder where the .txt files are located
folderPath = './photofluor';

% Get a list of all .txt files in the folder
fileList = dir(fullfile(folderPath, '*.txt'));
figure
hold on
% Loop through each file and apply the plot_spectrum function



for k = 1:length(fileList)
    % Get the full path of the .txt file
    filePath = fullfile(folderPath, fileList(k).name);
    
    % Apply the plot_spectrum function to the file

    plot_spectrum(filePath);
end

legend(fileList(:).name)

xlabel("wavelength/nm");
ylabel("intensity/AU");
