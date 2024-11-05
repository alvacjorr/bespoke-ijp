function [l,I] = plot_spectrum(filename)
%plots and returns data for a USB2000 spectrum text file

fid = fopen(filename);
%header = textscan(fid,'%s',3);            % Optionally save header names
C = textscan(fid,'%f %f','HeaderLines',15); % Read data skipping header
fclose(fid);                                % Don't forget to close file
l = cell2mat(C(:,1)); %wavelength in nm
I = cell2mat(C(:,2)); %intensity in AU from 0 to 1
I = I/max(I);

plot(l,I);
ylim ([0 1]);


end